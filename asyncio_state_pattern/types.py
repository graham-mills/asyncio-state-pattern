from typing import Type, TypeAlias

from .state import State

StateInstanceOrType: TypeAlias = State | Type[State]
