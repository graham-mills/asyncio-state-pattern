import pytest

from asyncio_state_pattern import State, initial_state, StateMachine


class StateA(State):
    pass


class StateB(State):
    pass


async def test_implicit_initial_state_class():
    """
    When a StateMachine is initialized with a list of state *classes* without a
    state being explicitly specified as the initial state, the first state in
    the list is used as the initial state.
    """

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[StateA, StateB])

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateA


async def test_explicit_initial_state_first():
    """
    When a StateMachine is initialized with a list of states and the first
    state value is wrapped with the initial_state function, then that state is
    used as the initial state.
    """

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[initial_state(StateA), StateB])

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateA


async def test_explicit_initial_state_last():
    """
    When a StateMachine is initialized with a list of states and the first
    state value is wrapped with the initial_state function, then that state is
    used as the initial state.
    """

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(
                states=[
                    StateB,
                    initial_state(StateA),
                ]
            )

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateA


async def test_multiple_initial_states():
    """
    When a StateMachine is initialized with a list of states and more than one
    state is wrapped with the initial_state function, then a ValueError is
    raised.
    """

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(
                states=[
                    initial_state(StateB),
                    initial_state(StateA),
                ]
            )

    with pytest.raises(ValueError):
        UnitUnderTest()
