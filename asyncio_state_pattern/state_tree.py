from dataclasses import dataclass, field
from typing import List, Type, Optional, Dict

from .state import State
from .constants import initial_state_attr


@dataclass
class StateNode:
    name: str
    """The name of the state."""

    state_class: Type[State]
    """The state class type."""

    state_instance: Optional[Type[State]] = None
    """Instance of the state class."""

    initial: bool = False
    """
    Whether the state is the initial state in its region (i.e. the state 
    is the initial root state or the initial sub state of a composite state).
    """
    children: List["StateNode"] = field(default_factory=list)
    """
    If the state is a composite state, contains nodes for each sub state.
    """

    ancestors: List["StateNode"] = field(default_factory=list)
    """
    If the state is a sub state, contains nodes for each of its super states
    ordered with the root state first and the immediate parent last.
    """

    @property
    def is_composite(self) -> bool:
        return len(self.children) > 0

    @property
    def is_simple(self) -> bool:
        return len(self.children) == 0

    def infer_initial_states(self) -> None:
        if self.is_simple:
            return

        if not any([child.initial for child in self.children]):
            if self.state_class is State or len(self.children) == 1:
                self.children[0].initial = True
            else:
                raise ValueError(
                    f"Composite state '{self.name}' has multiple sub states but none declared as the initial sub state. Add `initial=True` to the declaration of one of the following classes: {', '.join([s.name for s in self.children])}"
                )

        for child in self.children:
            child.infer_initial_states()

    def validate(self) -> None:
        if self.is_composite:
            self._validate_composite()

        for node in self.children:
            node.validate()

    def _validate_composite(self) -> None:
        initial_sub_states = [node for node in self.children if node.initial]
        if not initial_sub_states:
            raise ValueError(
                f"Composite state '{self.name}' has no sub state declared as the initial state. Add `initial=True` to the declaration of one of the following classes: {', '.join([s.name for s in self.children])}"
            )

        if len(initial_sub_states) > 1:
            raise ValueError(
                f"Composite state '{self.name}' has multiple sub states declared as the initial state. Only one initial sub state is allowed. See conflicting state declarations: {', '.join([s.name for s in initial_sub_states])}"
            )

    def find_innermost_initial_sub_state(self) -> Optional["StateNode"]:
        if self.is_simple and self.initial:
            return self
        for child in self.children:
            if found := child.find_innermost_initial_sub_state():
                return found
        return None


@dataclass
class StateTree:
    root_node: StateNode = field(
        default_factory=lambda: StateNode(name=State.__name__, state_class=State)
    )
    nodes: Dict[str, StateNode] = field(default_factory=dict)

    def infer_initial_states(self) -> None:
        """
        For state regions that have no initial state declared, attempt to infer
        the initial state following the rules:
        - If there is no top level initial state declared, then the first top
          level state is set as the initial state
        - If a composite state has no sub state declared as the initial state,
          and there is only 1 sub state, then that sub state is used as the
          initial state
        """
        self.root_node.infer_initial_states()

    def validate(self) -> None:
        self.root_node.validate()


def create_state_tree(state_classes: List[Type[State]]) -> StateTree:
    """
    Creates a tree of StateNodes from the given list of state classes.
    """
    tree = StateTree()

    for state_class in state_classes:
        _add_state_to_tree(state_class, tree)

    return tree


def _add_state_to_tree(state_class: Type[State], tree: StateTree) -> None:
    """
    Adds a node to the tree for the given state class, and adds nodes for any
    ancestor states that are not already in the tree.
    """

    parent = None
    for cls in _get_state_hierarchy(state_class):
        existing_node = tree.nodes.get(cls.__name__, None)
        if existing_node:
            parent = existing_node
            continue
        node = StateNode(name=cls.__name__, state_class=cls)
        if hasattr(cls, initial_state_attr):
            node.initial = cls.__name__ in getattr(cls, initial_state_attr)

        if parent:
            node.ancestors = [*parent.ancestors, parent]
            parent.children.append(node)
        else:
            tree.root_node.children.append(node)
        tree.nodes[node.name] = node
        parent = node


def _get_state_hierarchy(cls: Type[State]) -> List[Type[State]]:
    """
    Returns a list containing cls and all ancestor state classes, ordered by
    proximity to the State base class.
    """
    hierarchy = []
    for ancestor in cls.__bases__:
        if ancestor is State:
            break
        if issubclass(ancestor, State):
            hierarchy.extend(_get_state_hierarchy(ancestor))
            break
    hierarchy.append(cls)
    return hierarchy
