from typing import Type, TypeAlias, Union

from .state import State

StateInstanceOrClass: TypeAlias = Union[State, Type[State]]
