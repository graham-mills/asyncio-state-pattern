from asyncio_state_pattern import State
from asyncio_state_pattern.state_machine import (
    _get_transition_exit_states,
    _get_transition_entry_states,
    _diff_state_hierarchies,
)
from asyncio_state_pattern.state_tree import create_state_tree

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


state_tree = create_state_tree([StateA, StateB, StateC, StateD, StateE, StateF, StateG])


def test_get_transition_exit_states():
    """
    Given a source state and a destination state, test that a list is returned
    containing all states that would be exited when transitioning between them,
    in the order of tree traversal.
    """
    # From StateA
    assert _get_transition_exit_states(StateA, StateA, state_tree) == []
    assert _get_transition_exit_states(StateA, StateB, state_tree) == []
    assert _get_transition_exit_states(StateA, StateC, state_tree) == [StateA]
    assert _get_transition_exit_states(StateA, StateD, state_tree) == [StateA]
    assert _get_transition_exit_states(StateA, StateE, state_tree) == [StateA]
    assert _get_transition_exit_states(StateA, StateF, state_tree) == [StateA]
    assert _get_transition_exit_states(StateA, StateG, state_tree) == [StateA]

    # From StateB
    assert _get_transition_exit_states(StateB, StateA, state_tree) == [StateB]
    assert _get_transition_exit_states(StateB, StateB, state_tree) == []
    assert _get_transition_exit_states(StateB, StateC, state_tree) == [StateB, StateA]
    assert _get_transition_exit_states(StateB, StateD, state_tree) == [StateB, StateA]
    assert _get_transition_exit_states(StateB, StateE, state_tree) == [StateB, StateA]
    assert _get_transition_exit_states(StateB, StateF, state_tree) == [StateB, StateA]
    assert _get_transition_exit_states(StateB, StateG, state_tree) == [StateB, StateA]

    # From StateC
    assert _get_transition_exit_states(StateC, StateA, state_tree) == [StateC]
    assert _get_transition_exit_states(StateC, StateB, state_tree) == [StateC]
    assert _get_transition_exit_states(StateC, StateC, state_tree) == []
    assert _get_transition_exit_states(StateC, StateD, state_tree) == []
    assert _get_transition_exit_states(StateC, StateE, state_tree) == []
    assert _get_transition_exit_states(StateC, StateF, state_tree) == []
    assert _get_transition_exit_states(StateC, StateG, state_tree) == []

    # From StateD
    assert _get_transition_exit_states(StateD, StateA, state_tree) == [StateD, StateC]
    assert _get_transition_exit_states(StateD, StateB, state_tree) == [StateD, StateC]
    assert _get_transition_exit_states(StateD, StateC, state_tree) == [StateD]
    assert _get_transition_exit_states(StateD, StateE, state_tree) == [StateD]
    assert _get_transition_exit_states(StateD, StateF, state_tree) == []
    assert _get_transition_exit_states(StateD, StateG, state_tree) == [StateD]

    # From StateF
    assert _get_transition_exit_states(StateF, StateA, state_tree) == [
        StateF,
        StateD,
        StateC,
    ]
    assert _get_transition_exit_states(StateF, StateB, state_tree) == [
        StateF,
        StateD,
        StateC,
    ]
    assert _get_transition_exit_states(StateF, StateC, state_tree) == [StateF, StateD]
    assert _get_transition_exit_states(StateF, StateD, state_tree) == [StateF]
    assert _get_transition_exit_states(StateF, StateE, state_tree) == [StateF, StateD]
    assert _get_transition_exit_states(StateF, StateF, state_tree) == []
    assert _get_transition_exit_states(StateF, StateG, state_tree) == [StateF, StateD]

    # From StateG
    assert _get_transition_exit_states(StateG, StateA, state_tree) == [
        StateG,
        StateE,
        StateC,
    ]
    assert _get_transition_exit_states(StateG, StateB, state_tree) == [
        StateG,
        StateE,
        StateC,
    ]
    assert _get_transition_exit_states(StateG, StateC, state_tree) == [StateG, StateE]
    assert _get_transition_exit_states(StateG, StateD, state_tree) == [StateG, StateE]
    assert _get_transition_exit_states(StateG, StateE, state_tree) == [StateG]
    assert _get_transition_exit_states(StateG, StateF, state_tree) == [StateG, StateE]
    assert _get_transition_exit_states(StateG, StateG, state_tree) == []
    assert _get_transition_exit_states(StateG, StateG, state_tree) == []


def test_get_transition_entry_states():
    """
    Given a source state and a destination state, test that a list is returned
    containing all states that would be entered when transitioning between them,
    in the order of tree traversal.
    """

    # From None (Initial transition)
    assert _get_transition_entry_states(None, StateA, state_tree) == [StateA]
    assert _get_transition_entry_states(None, StateB, state_tree) == [StateA, StateB]
    assert _get_transition_entry_states(None, StateC, state_tree) == [StateC]
    assert _get_transition_entry_states(None, StateD, state_tree) == [StateC, StateD]
    assert _get_transition_entry_states(None, StateE, state_tree) == [StateC, StateE]
    assert _get_transition_entry_states(None, StateF, state_tree) == [
        StateC,
        StateD,
        StateF,
    ]
    assert _get_transition_entry_states(None, StateG, state_tree) == [
        StateC,
        StateE,
        StateG,
    ]

    # From StateA
    assert _get_transition_entry_states(StateA, StateA, state_tree) == []
    assert _get_transition_entry_states(StateA, StateB, state_tree) == [StateB]
    assert _get_transition_entry_states(StateA, StateC, state_tree) == [StateC]
    assert _get_transition_entry_states(StateA, StateD, state_tree) == [StateC, StateD]
    assert _get_transition_entry_states(StateA, StateE, state_tree) == [StateC, StateE]
    assert _get_transition_entry_states(StateA, StateF, state_tree) == [
        StateC,
        StateD,
        StateF,
    ]
    assert _get_transition_entry_states(StateA, StateG, state_tree) == [
        StateC,
        StateE,
        StateG,
    ]

    # From StateB
    assert _get_transition_entry_states(StateB, StateA, state_tree) == []
    assert _get_transition_entry_states(StateB, StateC, state_tree) == [StateC]
    assert _get_transition_entry_states(StateB, StateD, state_tree) == [StateC, StateD]
    assert _get_transition_entry_states(StateB, StateE, state_tree) == [StateC, StateE]
    assert _get_transition_entry_states(StateB, StateF, state_tree) == [
        StateC,
        StateD,
        StateF,
    ]
    assert _get_transition_entry_states(StateB, StateG, state_tree) == [
        StateC,
        StateE,
        StateG,
    ]

    # From StateC
    assert _get_transition_entry_states(StateC, StateA, state_tree) == [StateA]
    assert _get_transition_entry_states(StateC, StateB, state_tree) == [StateA, StateB]
    assert _get_transition_entry_states(StateC, StateC, state_tree) == []
    assert _get_transition_entry_states(StateC, StateD, state_tree) == [StateD]
    assert _get_transition_entry_states(StateC, StateE, state_tree) == [StateE]
    assert _get_transition_entry_states(StateC, StateF, state_tree) == [StateD, StateF]
    assert _get_transition_entry_states(StateC, StateG, state_tree) == [StateE, StateG]

    # From StateD
    assert _get_transition_entry_states(StateD, StateA, state_tree) == [StateA]
    assert _get_transition_entry_states(StateD, StateB, state_tree) == [StateA, StateB]
    assert _get_transition_entry_states(StateD, StateC, state_tree) == []
    assert _get_transition_entry_states(StateD, StateD, state_tree) == []
    assert _get_transition_entry_states(StateD, StateE, state_tree) == [StateE]
    assert _get_transition_entry_states(StateD, StateF, state_tree) == [StateF]
    assert _get_transition_entry_states(StateD, StateG, state_tree) == [StateE, StateG]

    # From StateE
    assert _get_transition_entry_states(StateE, StateA, state_tree) == [StateA]
    assert _get_transition_entry_states(StateE, StateB, state_tree) == [StateA, StateB]
    assert _get_transition_entry_states(StateE, StateC, state_tree) == []
    assert _get_transition_entry_states(StateE, StateD, state_tree) == [StateD]
    assert _get_transition_entry_states(StateE, StateE, state_tree) == []
    assert _get_transition_entry_states(StateE, StateF, state_tree) == [StateD, StateF]
    assert _get_transition_entry_states(StateE, StateG, state_tree) == [StateG]

    # From StateF
    assert _get_transition_entry_states(StateF, StateA, state_tree) == [StateA]
    assert _get_transition_entry_states(StateF, StateB, state_tree) == [StateA, StateB]
    assert _get_transition_entry_states(StateF, StateC, state_tree) == []
    assert _get_transition_entry_states(StateF, StateD, state_tree) == []
    assert _get_transition_entry_states(StateF, StateE, state_tree) == [StateE]
    assert _get_transition_entry_states(StateF, StateF, state_tree) == []
    assert _get_transition_entry_states(StateF, StateG, state_tree) == [StateE, StateG]

    # From StateG
    assert _get_transition_entry_states(StateG, StateA, state_tree) == [StateA]
    assert _get_transition_entry_states(StateG, StateB, state_tree) == [StateA, StateB]
    assert _get_transition_entry_states(StateG, StateC, state_tree) == []
    assert _get_transition_entry_states(StateG, StateD, state_tree) == [StateD]
    assert _get_transition_entry_states(StateG, StateE, state_tree) == []
    assert _get_transition_entry_states(StateG, StateF, state_tree) == [StateD, StateF]
    assert _get_transition_entry_states(StateG, StateG, state_tree) == []


def test_diff_state_hierarchies():
    """
    Given a left and right state class, test that a list is returned containing
    all state classes from the left state's class hierarchy that are not present
    in the right state's class hierarchy, ordered by proximity to the State
    base class.
    """

    assert _diff_state_hierarchies(StateB, StateD, state_tree) == [StateA, StateB]
    assert _diff_state_hierarchies(StateA, StateB, state_tree) == []
    assert _diff_state_hierarchies(StateB, StateA, state_tree) == [StateB]
    assert _diff_state_hierarchies(StateF, StateB, state_tree) == [
        StateC,
        StateD,
        StateF,
    ]
    assert _diff_state_hierarchies(StateF, StateE, state_tree) == [StateD, StateF]
    assert _diff_state_hierarchies(StateF, StateG, state_tree) == [StateD, StateF]
    assert _diff_state_hierarchies(StateG, StateF, state_tree) == [StateE, StateG]
