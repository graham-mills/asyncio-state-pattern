from typing import Type, TypeAlias

from .state import State

StateInstanceOrClass: TypeAlias = State | Type[State]
