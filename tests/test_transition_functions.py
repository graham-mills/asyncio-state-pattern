from asyncio_state_pattern import State
from asyncio_state_pattern.state_machine import (
    _get_transition_exit_states,
    _get_transition_entry_states,
    _diff_state_hierarchies,
    _get_state_hierarchy,
)

#   State
#    / \
#   A   C
#  /   / \
# B   D   E
#     |   |
#     F   G


class NotAState:
    pass


class StateA(State):
    pass


class StateC(State, NotAState):
    pass


class StateB(StateA):
    pass


class StateD(StateC):
    pass


class StateE(StateC):
    pass


class StateF(StateD):
    pass


class StateG(StateE):
    pass


def test_get_state_hierarchy():
    """
    Given a class that derives from the State base class, test that a list
    is returned containing the given class and all ancestor classes that
    also derive from the State base class, ordered by proximity to the State
    base class.
    """
    assert _get_state_hierarchy(StateA) == [StateA]
    assert _get_state_hierarchy(StateB) == [StateA, StateB]
    assert _get_state_hierarchy(StateC) == [StateC]
    assert _get_state_hierarchy(StateD) == [StateC, StateD]
    assert _get_state_hierarchy(StateF) == [StateC, StateD, StateF]
    assert _get_state_hierarchy(StateE) == [StateC, StateE]
    assert _get_state_hierarchy(StateG) == [StateC, StateE, StateG]


def test_get_transition_exit_states():
    """
    Given a source state and a destination state, test that a list is returned
    containing all states that would be exited when transitioning between them,
    in the order of tree traversal.
    """

    # From StateA
    assert _get_transition_exit_states(StateA, StateA) == []
    assert _get_transition_exit_states(StateA, StateB) == []
    assert _get_transition_exit_states(StateA, StateC) == [StateA]
    assert _get_transition_exit_states(StateA, StateD) == [StateA]
    assert _get_transition_exit_states(StateA, StateE) == [StateA]
    assert _get_transition_exit_states(StateA, StateF) == [StateA]
    assert _get_transition_exit_states(StateA, StateG) == [StateA]

    # From StateB
    assert _get_transition_exit_states(StateB, StateA) == [StateB]
    assert _get_transition_exit_states(StateB, StateB) == []
    assert _get_transition_exit_states(StateB, StateC) == [StateB, StateA]
    assert _get_transition_exit_states(StateB, StateD) == [StateB, StateA]
    assert _get_transition_exit_states(StateB, StateE) == [StateB, StateA]
    assert _get_transition_exit_states(StateB, StateF) == [StateB, StateA]
    assert _get_transition_exit_states(StateB, StateG) == [StateB, StateA]

    # From StateC
    assert _get_transition_exit_states(StateC, StateA) == [StateC]
    assert _get_transition_exit_states(StateC, StateB) == [StateC]
    assert _get_transition_exit_states(StateC, StateC) == []
    assert _get_transition_exit_states(StateC, StateD) == []
    assert _get_transition_exit_states(StateC, StateE) == []
    assert _get_transition_exit_states(StateC, StateF) == []
    assert _get_transition_exit_states(StateC, StateG) == []

    # From StateD
    assert _get_transition_exit_states(StateD, StateA) == [StateD, StateC]
    assert _get_transition_exit_states(StateD, StateB) == [StateD, StateC]
    assert _get_transition_exit_states(StateD, StateC) == [StateD]
    assert _get_transition_exit_states(StateD, StateE) == [StateD]
    assert _get_transition_exit_states(StateD, StateF) == []
    assert _get_transition_exit_states(StateD, StateG) == [StateD]

    # From StateF
    assert _get_transition_exit_states(StateF, StateA) == [StateF, StateD, StateC]
    assert _get_transition_exit_states(StateF, StateB) == [StateF, StateD, StateC]
    assert _get_transition_exit_states(StateF, StateC) == [StateF, StateD]
    assert _get_transition_exit_states(StateF, StateD) == [StateF]
    assert _get_transition_exit_states(StateF, StateE) == [StateF, StateD]
    assert _get_transition_exit_states(StateF, StateF) == []
    assert _get_transition_exit_states(StateF, StateG) == [StateF, StateD]

    # From StateG
    assert _get_transition_exit_states(StateG, StateA) == [StateG, StateE, StateC]
    assert _get_transition_exit_states(StateG, StateB) == [StateG, StateE, StateC]
    assert _get_transition_exit_states(StateG, StateC) == [StateG, StateE]
    assert _get_transition_exit_states(StateG, StateD) == [StateG, StateE]
    assert _get_transition_exit_states(StateG, StateE) == [StateG]
    assert _get_transition_exit_states(StateG, StateF) == [StateG, StateE]
    assert _get_transition_exit_states(StateG, StateG) == []
    assert _get_transition_exit_states(StateG, StateG) == []


def test_get_transition_entry_states():
    """
    Given a source state and a destination state, test that a list is returned
    containing all states that would be entered when transitioning between them,
    in the order of tree traversal.
    """

    # From StateA
    assert _get_transition_entry_states(StateA, StateA) == []
    assert _get_transition_entry_states(StateA, StateB) == [StateB]
    assert _get_transition_entry_states(StateA, StateC) == [StateC]
    assert _get_transition_entry_states(StateA, StateD) == [StateC, StateD]
    assert _get_transition_entry_states(StateA, StateE) == [StateC, StateE]
    assert _get_transition_entry_states(StateA, StateF) == [StateC, StateD, StateF]

    # From StateB
    assert _get_transition_entry_states(StateB, StateA) == []
    assert _get_transition_entry_states(StateB, StateC) == [StateC]
    assert _get_transition_entry_states(StateB, StateD) == [StateC, StateD]
    assert _get_transition_entry_states(StateB, StateE) == [StateC, StateE]
    assert _get_transition_entry_states(StateB, StateF) == [StateC, StateD, StateF]
    assert _get_transition_entry_states(StateB, StateG) == [StateC, StateE, StateG]

    # From StateC
    assert _get_transition_entry_states(StateC, StateA) == [StateA]
    assert _get_transition_entry_states(StateC, StateB) == [StateA, StateB]
    assert _get_transition_entry_states(StateC, StateC) == []
    assert _get_transition_entry_states(StateC, StateD) == [StateD]
    assert _get_transition_entry_states(StateC, StateE) == [StateE]
    assert _get_transition_entry_states(StateC, StateF) == [StateD, StateF]
    assert _get_transition_entry_states(StateC, StateG) == [StateE, StateG]

    # From StateD
    assert _get_transition_entry_states(StateD, StateA) == [StateA]
    assert _get_transition_entry_states(StateD, StateB) == [StateA, StateB]
    assert _get_transition_entry_states(StateD, StateC) == []
    assert _get_transition_entry_states(StateD, StateD) == []
    assert _get_transition_entry_states(StateD, StateE) == [StateE]
    assert _get_transition_entry_states(StateD, StateF) == [StateF]
    assert _get_transition_entry_states(StateD, StateG) == [StateE, StateG]

    # From StateE
    assert _get_transition_entry_states(StateE, StateA) == [StateA]
    assert _get_transition_entry_states(StateE, StateB) == [StateA, StateB]
    assert _get_transition_entry_states(StateE, StateC) == []
    assert _get_transition_entry_states(StateE, StateD) == [StateD]
    assert _get_transition_entry_states(StateE, StateE) == []
    assert _get_transition_entry_states(StateE, StateF) == [StateD, StateF]
    assert _get_transition_entry_states(StateE, StateG) == [StateG]

    # From StateF
    assert _get_transition_entry_states(StateF, StateA) == [StateA]
    assert _get_transition_entry_states(StateF, StateB) == [StateA, StateB]
    assert _get_transition_entry_states(StateF, StateC) == []
    assert _get_transition_entry_states(StateF, StateD) == []
    assert _get_transition_entry_states(StateF, StateE) == [StateE]
    assert _get_transition_entry_states(StateF, StateF) == []
    assert _get_transition_entry_states(StateF, StateG) == [StateE, StateG]

    # From StateG
    assert _get_transition_entry_states(StateG, StateA) == [StateA]
    assert _get_transition_entry_states(StateG, StateB) == [StateA, StateB]
    assert _get_transition_entry_states(StateG, StateC) == []
    assert _get_transition_entry_states(StateG, StateD) == [StateD]
    assert _get_transition_entry_states(StateG, StateE) == []
    assert _get_transition_entry_states(StateG, StateF) == [StateD, StateF]
    assert _get_transition_entry_states(StateG, StateG) == []


def test_diff_state_hierarchies():
    """
    Given a left and right state class, test that a list is returned containing
    all state classes from the left state's class hierarchy that are not present
    in the right state's class hierarchy, ordered by proximity to the State
    base class.
    """

    assert _diff_state_hierarchies(StateB, StateD) == [StateA, StateB]
    assert _diff_state_hierarchies(StateA, StateB) == []
    assert _diff_state_hierarchies(StateB, StateA) == [StateB]
    assert _diff_state_hierarchies(StateF, StateB) == [StateC, StateD, StateF]
    assert _diff_state_hierarchies(StateF, StateE) == [StateD, StateF]
    assert _diff_state_hierarchies(StateF, StateG) == [StateD, StateF]
    assert _diff_state_hierarchies(StateG, StateF) == [StateE, StateG]
