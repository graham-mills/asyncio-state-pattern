import pytest

from asyncio_state_pattern import State, StateMachine, StateMachineError


class StateA(State):
    pass


async def test_start():
    """
    Given a StateMachine that is not started, when it is requested to be
    started, then the initial state is entered.
    """

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[StateA])

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) is StateA


async def test_start_when_already_started():
    """
    Given a StateMachine that is already started, when it is requested to be
    started again, then a StateMachineError is raised.
    """

    class UnitUnderTest(StateMachine):
        def __init__(self):
            super().__init__(states=[StateA])

    uut = UnitUnderTest()
    await uut.start()
    with pytest.raises(StateMachineError):
        await uut.start()
