from .types import StateInstanceOrType
from .constants import initial_state_attr


def initial_state(state: StateInstanceOrType) -> StateInstanceOrType:
    setattr(state, initial_state_attr, True)
    return state
