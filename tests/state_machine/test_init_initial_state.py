import pytest

from asyncio_state_pattern import State, StateMachine


async def test_implicit_initial_state_class():
    """
    When a StateMachine is initialized with a list of state *classes* without a
    state being explicitly specified as the initial state, the first state in
    the list is used as the initial state.
    """

    class StateA(State):
        pass

    class StateB(State):
        pass

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[StateA, StateB])

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateA


async def test_explicit_initial_state_class():
    """
    When a StateMachine is initialized with a list of state classes and one of
    the classes is declared as the initial state, then that state is used as the
    initial state.
    """

    class StateA(State):
        pass

    class StateB(State, initial=True):
        pass

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[StateA, StateB])

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateB


async def test_multiple_initial_states():
    """
    When a StateMachine is initialized with a list of non-sub states and more
    than one state is declared as an initial state, then a ValueError is raised.
    """

    class StateA(State, initial=True):
        pass

    class StateB(State, initial=True):
        pass

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(
                states=[
                    StateB,
                    StateA,
                ]
            )

    with pytest.raises(ValueError):
        UnitUnderTest()


async def test_initial_sub_state_not_declared():
    """
    When a StateMachine is initialized with a composite state as the initial
    state, and that composite state has multiple sub states not none declared as
    the initial state, then a ValueError is raised.
    """

    class StateA(State, initial=True):
        pass

    class StateB(StateA):
        pass

    class StateC(StateA):
        pass

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(
                states=[
                    StateA,
                    StateB,
                    StateC,
                ]
            )

    with pytest.raises(ValueError):
        _ = UnitUnderTest()


async def test_implicit_sub_state():
    """
    When a StateMachine is initialized with a composite state as the initial
    state, and that composite state has 1 sub state, which is not declared
    as the initial state, then that sub state is used as the initial state.
    """

    class StateA(State, initial=True):
        pass

    class StateB(StateA):
        pass

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(
                states=[
                    StateA,
                    StateB,
                ]
            )

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateB


async def test_explicit_sub_state():
    """
    When a StateMachine is initialized with a composite state as the initial
    state, and that composite state has a sub state declared as the initial
    state, then that sub state is entered when the StateMachine is started.
    """

    class StateA(State, initial=True):
        pass

    class StateB(StateA):
        pass

    class StateC(StateA, initial=True):
        pass

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(
                states=[
                    StateA,
                    StateB,
                    StateC,
                ]
            )

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateC
