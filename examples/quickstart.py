import asyncio
from asyncio_state_pattern import State, StateMachine

class InitialState(State):
    def greet(self):
        print(f"Hello from {self.name}!")

class GreetingStateMachine(StateMachine):
    def __init__(self):
        super().__init__(states=[InitialState])

    def greet(self):
        self.state.greet()

async def main():
    state_machine = GreetingStateMachine() # State is initially `None`
    await state_machine.start() # State set to `InitialState`
    state_machine.greet() # Prints "Hello from InitialState!"

asyncio.run(main())