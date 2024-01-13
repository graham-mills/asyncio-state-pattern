from logging import Logger
from typing import Generic, TypeVar, Optional

from .logger import logger as asp_logger
from .constants import (
    entry_action_attr,
    exit_action_attr,
    event_action_attr,
    initial_state_attr,
)

T = TypeVar("T")


class State(Generic[T]):
    """
    Base class for a state.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._logger = logger or asp_logger
        self._context: Optional[T] = None
        self._entry_actions = [
            item
            for item in self.__class__.__dict__.values()
            if hasattr(item, entry_action_attr)
        ]
        self._exit_actions = [
            item
            for item in self.__class__.__dict__.values()
            if hasattr(item, exit_action_attr)
        ]
        self._event_actions_by_id = {}
        for item in [
            i for i in self.__class__.__dict__.values() if hasattr(i, event_action_attr)
        ]:
            event_id = getattr(item, event_action_attr)
            if event_id not in self._event_actions_by_id:
                self._event_actions_by_id[event_id] = [item]
            else:
                self._event_actions_by_id[event_id].append(item)

    def __init_subclass__(cls, initial: bool = False) -> None:
        if initial:
            if not hasattr(cls, initial_state_attr):
                setattr(cls, initial_state_attr, [])
            getattr(cls, initial_state_attr).append(cls.__name__)

    @property
    def context(self) -> T:
        """The state's StateMachine context."""
        return self._context

    @context.setter
    def context(self, context: T) -> None:
        self._context = context

    @property
    def name(self) -> str:
        """The state's name."""
        return self.__class__.__name__

    async def enter(self) -> None:
        for method in self._entry_actions:
            await method(self)

    async def exit(self) -> None:
        for method in self._exit_actions:
            await method(self)

    async def queue_event(self) -> None:
        await self.context.queue_event(self.name)

    async def process_event(self, event) -> bool:
        if event not in self._event_actions_by_id:
            return False

        for action in self._event_actions_by_id[event]:
            consumed = await action(self)
            if consumed:
                return True
        return False
