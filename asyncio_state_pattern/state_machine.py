import asyncio
import inspect
from logging import Logger
from typing import List, Type, Optional
from inspect import isclass

from .state import State
from .logger import logger
from .types import StateInstanceOrClass
from .constants import initial_state_attr


class StateMachineError(Exception):
    pass


class StateMachine:
    def __init__(
        self,
        states=List[StateInstanceOrClass],
        logger: Logger = logger,
        max_event_queue_size: int = 0,
    ):
        self._logger = logger
        if not states:
            raise ValueError(f"{log_prefix(self)} Must provide at least one state")

        self._states = {}
        self._initial_state = None
        self._transitioning = False
        self._event_queue = asyncio.Queue(max_event_queue_size)
        self._running = False
        self._run_task: Optional[asyncio.Task] = None

        for s in states:
            if isinstance(s, State):
                instance = s
            elif isclass(s) and issubclass(s, State):
                instance = s()
            else:
                raise ValueError(
                    f"{log_prefix(self)} Unexpected state {s}, expected instance of State or subclass of State"
                )

            instance.context = self
            self._states[instance.name] = instance

        for state in self._states.values():
            if hasattr(state.__class__, initial_state_attr) and getattr(
                state.__class__, initial_state_attr
            ):
                if self._initial_state:
                    raise ValueError(
                        f"{log_prefix(self)} Cannot have more than one initial state"
                    )
                self._initial_state = state
                delattr(state.__class__, initial_state_attr)

        if not self._initial_state:
            self._initial_state = next(iter(self._states.values()))

        self._state: State | None = None

    @property
    def state(self) -> State | None:
        return self._state

    @property
    def name(self) -> str:
        return self.__class__.__name__

    async def run(self, event_loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """
        Runs the state machine until stopped.
        """
        if self._running:
            raise StateMachineError(
                f"{log_prefix(self)} is already running and must be stopped before running again"
            )

        loop = event_loop if event_loop else asyncio.get_event_loop()
        self._run_task = loop.create_task(self._run_loop())
        self._running = True

    async def run_once(self) -> None:
        if self._running:
            raise StateMachineError(
                f"{log_prefix(self)} Method cannot be used in conjunction with run"
            )
        try:
            event = await self._event_queue.get_nowait()
            await self._state.process_event(event)
        except asyncio.QueueEmpty:
            pass

    async def stop(self) -> None:
        if not self._running:
            logger.warning(f"{log_prefix(self)}: Already stopped")
            return
        self._running = False
        await self._event_queue.put(None)
        await asyncio.wait_for(self._run_task, timeout=None)
        await self._reset()
        logger.debug(f"{log_prefix(self)} Stopped")

    async def start(self) -> None:
        if self._state:
            raise StateMachineError(f"{log_prefix(self)} State machine already started")
        await self._transition_to(self._initial_state)

    async def queue_event(self, event) -> None:
        await self._event_queue.put(event)

    async def transition_to(self, state: Type[State]) -> None:
        if name_of(state) not in self._states:
            raise ValueError(f"{log_prefix(self)} State {name_of(state)} not known")

        if self._transitioning:
            raise StateMachineError(
                f"{log_prefix(self)} Cannot transition while a transition is already in progress"
            )

        await self._transition_to(self._states[name_of(state)])

    async def _run_loop(self) -> None:
        if not self._state:
            await self.start()
        while self._running:
            event = await self._event_queue.get()
            if event is None:
                # Check if we've been stopped
                continue
            await self._state.process_event(event)

    async def _reset(self):
        self._state = None
        self._transitioning = False
        self._running = False
        while not self._event_queue.empty():
            self._event_queue.get_nowait()

    async def _transition_to(self, state: State):
        self._transitioning = True
        if not self._state:
            logger.debug(f"{self.name}: [*] -> {state.name}")
        else:
            logger.debug(f"{self.name}: {self._state.name} -> {state.name}")
            exit_states = _get_transition_exit_states(
                self._state.__class__, state.__class__
            )
            for exit_state in exit_states:
                await self._states[name_of(exit_state)].exit()

        entry_states = _get_transition_entry_states(
            self._state.__class__, state.__class__
        )
        self._state = state
        for entry_state in entry_states:
            await self._states[name_of(entry_state)].enter()

        self._transitioning = False


def _get_transition_exit_states(
    source: Type[State], dest: Type[State]
) -> List[Type[State]]:
    return list(reversed(_diff_state_hierarchies(source, dest)))


def _get_transition_entry_states(
    source: Type[State], dest: Type[State]
) -> List[Type[State]]:
    return _diff_state_hierarchies(dest, source)


def _diff_state_hierarchies(left: Type[State], right: Type[State]) -> List[Type[State]]:
    """
    Returns a list of the all state classes in left's class hierarchy that are
    not present in right's class hierarchy, ordered by proximity to the State
    base class.
    """
    left_hierarchy = _get_state_hierarchy(left)
    right_hierarchy = _get_state_hierarchy(right)
    for index, cls in enumerate(left_hierarchy):
        if cls in right_hierarchy:
            continue
        return left_hierarchy[index:]
    return []


def _get_state_hierarchy(cls: Type[State]) -> List[Type[State]]:
    """
    Returns a list containing cls and all ancestor state classes, ordered by
    proximity to the State base class.
    """
    hierarchy = []
    for ancestor in cls.__bases__:
        if name_of(ancestor) == name_of(State):
            break
        if issubclass(ancestor, State):
            hierarchy.extend(_get_state_hierarchy(ancestor))
            break
    hierarchy.append(cls)
    return hierarchy


def name_of(state: StateInstanceOrClass) -> str:
    if isinstance(state, State):
        return state.name
    else:
        return state.__name__


def log_prefix(sm: StateMachine) -> str:
    return f"{sm.name}.{inspect.stack()[1][3]}:"
