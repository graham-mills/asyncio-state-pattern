import asyncio
import inspect
from logging import Logger
from typing import List, Type, Optional, Any
from inspect import isclass

from .state import State
from .logger import logger as asp_logger
from .types import StateInstanceOrClass
from .state_tree import create_state_tree, StateTree


class StateMachineError(Exception):
    pass


class StateMachine:
    def __init__(
        self,
        states=List[StateInstanceOrClass],
        logger: Optional[Logger] = None,
        max_event_queue_size: int = 0,
    ):
        if not states:
            raise ValueError(
                "Arg `states` - must provide at least one State instance or subclass"
            )

        if any(not _is_state_instance_or_subclass(s) for s in states):
            raise ValueError(
                "Arg `states` - values must be an instance or subclass of State"
            )

        self._logger = logger or asp_logger
        self._transitioning = False
        self._event_queue = asyncio.Queue(max_event_queue_size)
        self._running = False
        self._state: State | None = None
        self._run_task: Optional[asyncio.Task] = None
        self._state_tree = self._init_states(states)

        try:
            self._state_tree.infer_initial_states()
            self._state_tree.validate()
        except ValueError as e:
            raise ValueError(f"{log_prefix(self)} {e}")

    def _init_states(self, states: List[StateInstanceOrClass]) -> StateTree:
        state_classes = map(
            lambda s: s if _is_state_subclass(s) else s.__class__, states
        )
        tree = create_state_tree(state_classes)

        for s in states:
            if _is_state_instance(s):
                node = tree.nodes[s.name]
                node.state_instance = s
            else:
                node = tree.nodes[s.__name__]
                node.state_instance = node.state_class()
            node.state_instance.context = self

        return tree

    @property
    def state(self) -> State | None:
        """
        Returns the current state instance, or None if the state machine is
        not started.
        """
        return self._state

    @property
    def state_cls(self) -> Type[State] | None:
        """
        Returns the class of the current state, or None if the state machine is
        not started.
        """
        return self.state if self.state else None

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
        if not self._state:
            await self.start()
        try:
            event = await self._event_queue.get_nowait()
            await self._state.process_event(event)
        except asyncio.QueueEmpty:
            pass

    async def stop(self) -> None:
        if not self._running:
            self._logger.warning(f"{log_prefix(self)}: Already stopped")
            return
        self._running = False
        await self._event_queue.put(None)
        await asyncio.wait_for(self._run_task, timeout=None)
        await self._reset()
        self._logger.debug(f"{log_prefix(self)} Stopped")

    async def start(self) -> None:
        if self._state:
            raise StateMachineError(f"{log_prefix(self)} State machine already started")
        initial_state = next(
            s.name for s in self._state_tree.root_node.children if s.initial
        )
        await self._transition_to(initial_state)

    async def queue_event(self, event) -> None:
        await self._event_queue.put(event)

    async def transition_to(self, state: Type[State]) -> None:
        if not _is_state_subclass(state):
            raise ValueError(
                f"{log_prefix(self)} Arg `state` - must be a subclass of State"
            )

        state_name = state.__name__
        if state_name not in self._state_tree.nodes:
            raise ValueError(f"{log_prefix(self)} State '{state_name}' not found")

        if self._transitioning:
            raise StateMachineError(
                f"{log_prefix(self)} Cannot transition while a transition is already in progress"
            )

        await self._transition_to(state_name)

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

    async def _transition_to(self, state_name: str):
        dest_node = self._state_tree.nodes[state_name]
        if dest_node.is_composite:
            dest_node = dest_node.find_innermost_initial_sub_state()

        self._transitioning = True
        try:
            if not self._state:
                self._logger.debug(f"{self.name}: [*] -> {state_name}")
            else:
                self._logger.debug(f"{self.name}: {self._state.name} -> {state_name}")
                exit_states_classes = _get_transition_exit_states(
                    self._state.__class__, dest_node.state_class, self._state_tree
                )
                for exit_state_cls in exit_states_classes:
                    await self._state_tree.nodes[
                        exit_state_cls.__name__
                    ].state_instance.exit()

            entry_state_classes = _get_transition_entry_states(
                source=self._state.__class__ if self._state else None,
                dest=dest_node.state_class,
                tree=self._state_tree,
            )
            self._state = dest_node.state_instance
            for entry_state in entry_state_classes:
                await self._state_tree.nodes[
                    entry_state.__name__
                ].state_instance.enter()
        finally:
            self._transitioning = False


def _get_transition_exit_states(
    source: Type[State], dest: Type[State], tree: StateTree
) -> List[Type[State]]:
    return list(reversed(_diff_state_hierarchies(source, dest, tree)))


def _get_transition_entry_states(
    source: Optional[Type[State]], dest: Type[State], tree: StateTree
) -> List[Type[State]]:
    if source is None:  # Initial transition
        dest_ancestors = [n.state_class for n in tree.nodes[dest.__name__].ancestors]
        return [*dest_ancestors, dest]

    return _diff_state_hierarchies(dest, source, tree)


def _diff_state_hierarchies(
    left: Type[State], right: Type[State], tree: StateTree
) -> List[Type[State]]:
    """
    Returns a list of the all state classes in left's class hierarchy that are
    not present in right's class hierarchy, ordered by proximity to the State
    base class.
    """
    left_hierarchy = [n.state_class for n in tree.nodes[left.__name__].ancestors]
    left_hierarchy.append(left)
    right_hierarchy = [n.state_class for n in tree.nodes[right.__name__].ancestors]
    right_hierarchy.append(right)
    for index, cls in enumerate(left_hierarchy):
        if cls in right_hierarchy:
            continue
        return left_hierarchy[index:]
    return []


def log_prefix(sm: StateMachine) -> str:
    return f"{sm.name}.{inspect.stack()[1][3]}:"


def _is_state_instance_or_subclass(s: Any) -> bool:
    return _is_state_instance(s) or _is_state_subclass(s)


def _is_state_instance(obj: Any) -> bool:
    return isinstance(obj, State)


def _is_state_subclass(cls: Type) -> bool:
    return isclass(cls) and issubclass(cls, State)
