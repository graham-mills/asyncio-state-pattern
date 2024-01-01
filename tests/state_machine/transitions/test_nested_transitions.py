import pytest

from asyncio_state_pattern import State, initial_state, StateMachine, on_entry, on_exit

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


class StateB(StateA):
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


class StateD(StateB):
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
                    initial_state(StateD),
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


async def test_transition_from_d_to_e(uut: StateMachine):
    await uut.transition_to(StateE)
    assert type(uut.state) == StateE
    assert exited_states == [StateD, StateB]
    assert entered_states == [StateC, StateE]
