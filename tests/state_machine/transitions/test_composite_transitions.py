import pytest

from asyncio_state_pattern import State, StateMachine, on_entry, on_exit

entered_states = []
exited_states = []

#   State
#     |
#     A
#    / \
#   B   C
#  /     \
# D       E


class StateA(State):
    @on_entry
    async def entry(self) -> None:
        global entered_states
        entered_states.append(self.__class__)

    @on_exit
    async def exit(self) -> None:
        global exited_states
        exited_states.append(self.__class__)


class StateB(StateA, initial=True):
    @on_entry
    async def entry(self) -> None:
        global entered_states
        entered_states.append(self.__class__)

    @on_exit
    async def exit(self) -> None:
        global exited_states
        exited_states.append(self.__class__)


class StateC(StateA):
    @on_entry
    async def entry(self) -> None:
        global entered_states
        entered_states.append(self.__class__)

    @on_exit
    async def exit(self) -> None:
        global exited_states
        exited_states.append(self.__class__)


class StateD(StateB, initial=True):
    @on_entry
    async def entry(self) -> None:
        global entered_states
        entered_states.append(self.__class__)

    @on_exit
    async def exit(self) -> None:
        global exited_states
        exited_states.append(self.__class__)


class StateE(StateC):
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
                    StateC,
                    StateD,
                    StateE,
                ]
            )

    uut = UnitUnderTest()
    await uut.start()
    assert type(uut.state) is StateD
    return uut


@pytest.fixture(autouse=True)
async def reset_test_outputs(uut: StateMachine):
    global entered_states, exited_states
    entered_states = []
    exited_states = []


async def test_transition_from_simple_to_simple(uut: StateMachine):
    await uut.transition_to(StateE)
    assert type(uut.state) == StateE
    assert exited_states == [StateD, StateB]
    assert entered_states == [StateC, StateE]


async def test_transition_from_simple_to_composite(uut: StateMachine):
    await uut.transition_to(StateC)
    assert type(uut.state) == StateE
    assert exited_states == [StateD, StateB]
    assert entered_states == [StateC, StateE]


async def test_transition_to_same_ancestor_state(uut: StateMachine):
    await uut.transition_to(StateA)
    assert type(uut.state) == StateD
    assert exited_states == []
    assert entered_states == []
