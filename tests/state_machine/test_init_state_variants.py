from asyncio_state_pattern import State, StateMachine


class StateA(State):
    pass


class StateB(State):
    pass


async def test_init_states_from_classes():
    """
    When a StateMachine is initialized with a list of state *classes*, then
    those classes can be used to transition to those states.
    """

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[StateA, StateB])

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateA
    await uut.transition_to(StateB)
    assert type(uut.state) == StateB


async def test_init_states_from_instances():
    """
    When a StateMachine is initialized with a list of state *instances*, then
    those instances can be used to transition to those states.
    """
    state_a = StateA()
    state_b = StateB()

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[state_a, state_b])

    uut = UnitUnderTest()
    await uut.start()
    assert uut.state is state_a
    await uut.transition_to(state_b)
    assert uut.state is state_b


async def test_init_states_from_classes_and_instances():
    """
    When a StateMachine is initialized with a list of state instances and
    classes, then those instances and classes can be used to transition to.
    """
    state_b = StateB()

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[StateA, state_b])

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) == StateA
    await uut.transition_to(state_b)
    assert uut.state is state_b
