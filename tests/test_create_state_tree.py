from asyncio_state_pattern.state_tree import create_state_tree
from asyncio_state_pattern.state import State


def test_create_tree_from_simple_states():
    """Tests construction of a state tree from 2 simple states."""
    #   State
    #   /   \
    #  A     B

    class StateA(State):
        pass

    class StateB(State):
        pass

    tree = create_state_tree([StateA, StateB])

    assert len(tree.root_node.children) == 2

    StateA_node = tree.root_node.children[0]
    assert StateA_node.name == StateA.__name__
    assert StateA_node.is_simple
    assert StateA_node.state_class == StateA
    assert StateA_node.ancestors == []
    assert len(StateA_node.children) == 0

    StateB_node = tree.root_node.children[1]
    assert StateB_node.name == StateB.__name__
    assert StateB_node.is_simple
    assert StateB_node.state_class == StateB
    assert StateB_node.ancestors == []
    assert len(StateB_node.children) == 0

    assert len(tree.nodes) == 2
    assert tree.nodes[StateA_node.name] is StateA_node
    assert tree.nodes[StateB_node.name] is StateB_node


def test_create_tree_from_composite_states():
    """Tests construction of a state tree from 2 composite states."""
    #   State
    #   /   \
    #  A     B
    #  |     |
    #  C     D

    class StateA(State):
        pass

    class StateB(State):
        pass

    class StateC(StateA):
        pass

    class StateD(StateB):
        pass

    tree = create_state_tree([StateC, StateD])

    assert len(tree.root_node.children) == 2

    StateA_node = tree.root_node.children[0]
    assert StateA_node.name == StateA.__name__
    assert StateA_node.is_composite
    assert StateA_node.state_class == StateA
    assert StateA_node.ancestors == []
    assert len(StateA_node.children) == 1

    StateB_node = tree.root_node.children[1]
    assert StateB_node.name == StateB.__name__
    assert StateB_node.is_composite
    assert StateB_node.state_class == StateB
    assert StateB_node.ancestors == []
    assert len(StateB_node.children) == 1

    StateC_node = StateA_node.children[0]
    assert StateC_node.name == StateC.__name__
    assert StateC_node.is_simple
    assert StateC_node.state_class == StateC
    assert StateC_node.ancestors == [StateA_node]
    assert len(StateC_node.children) == 0

    StateD_node = StateB_node.children[0]
    assert StateD_node.name == StateD.__name__
    assert StateD_node.is_simple
    assert StateD_node.state_class == StateD
    assert StateD_node.ancestors == [StateB_node]
    assert len(StateD_node.children) == 0

    assert len(tree.nodes) == 4
    assert tree.nodes[StateA_node.name] is StateA_node
    assert tree.nodes[StateB_node.name] is StateB_node
    assert tree.nodes[StateC_node.name] is StateC_node
    assert tree.nodes[StateD_node.name] is StateD_node
