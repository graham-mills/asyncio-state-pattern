import pytest

from asyncio_state_pattern import State, StateMachine, on_entry, on_exit

entered_states = []
exited_states = []

# State
#  / \
# A   B


class StateA(State):
    @on_entry
    async def entry(self) -> None:
        global entered_states
        entered_states.append(self.__class__)

    @on_exit
    async def exit(self) -> None:
        global exited_states
        exited_states.append(self.__class__)


class StateB(State):
    @on_entry
    async def entry(self) -> None:
        global entered_states
        entered_states.append(self.__class__)

    @on_exit
    async def exit(self) -> None:
        global exited_states
        exited_states.append(self.__class__)


@pytest.fixture
async def uut() -> StateMachine:
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
    assert type(uut.state) is StateA
    return uut


@pytest.fixture(autouse=True)
async def reset_test_outputs(uut: StateMachine):
    global entered_states, exited_states
    entered_states = []
    exited_states = []


async def test_basic_transitions(uut: StateMachine):
    await uut.transition_to(StateB)
    assert type(uut.state) == StateB
    assert exited_states == [StateA]
    assert entered_states == [StateB]

    await uut.transition_to(StateA)
    assert type(uut.state) == StateA
    assert exited_states == [StateA, StateB]
    assert entered_states == [StateB, StateA]


async def test_transition_to_same_state(uut: StateMachine):
    await uut.transition_to(StateA)
    assert type(uut.state) == StateA
    assert exited_states == []
    assert entered_states == []
