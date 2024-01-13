import asyncio

from asyncio_state_pattern import (
    State,
    StateMachine,
    on_entry,
    on_exit,
    on_event,
)


class CoffeeMaker(StateMachine):
    def __init__(self):
        super().__init__(states=[PoweredOff, PoweredOn, Idle, DispensingCoffee])

    async def make_coffee(self, type):
        return await self.state.make_coffee()

    async def power_on(self, type):
        return await self.state.power_on()

    async def power_off(self, type):
        return await self.state.power_off()


class PoweredOff(State, initial=True):
    async def make_coffee(type):
        return False

    async def power_on(self, type):
        return True

    async def power_off(self, type):
        return False

    @on_entry
    async def enter(self):
        print("Entered PoweredOff")

    @on_exit
    async def exit(self):
        print("Exited PoweredOff")

    @on_event("power_on")
    async def on_power_on(self):
        await self.context.transition_to(PoweredOn)


class PoweredOn(State):
    @on_entry
    async def enter(self):
        print("Entered PoweredOn")

    @on_exit
    async def exit(self):
        print("Exited PoweredOn")


class Idle(PoweredOn, initial=True):
    async def make_coffee(type):
        return False

    async def power_on(self, type):
        return False

    async def power_off(self, type):
        return False

    @on_entry
    async def enter(self):
        print("Entered Idle")

    @on_exit
    async def exit(self):
        print("Exited Idle")


class DispensingCoffee(PoweredOn):
    async def make_coffee(type):
        return False

    async def power_on(self, type):
        return False

    async def power_off(self, type):
        return False

    @on_entry
    async def enter(self):
        print("Entered DispensingCoffee")

    @on_exit
    async def exit(self):
        print("Exited DispensingCoffee")


async def main():
    cm = CoffeeMaker()
    await cm.run()
    await cm.queue_event("power_on")

    await asyncio.sleep(1)
    await cm.transition_to(DispensingCoffee)
    await asyncio.sleep(1)
    await cm.transition_to(PoweredOff)
    await cm.stop()


asyncio.run(main())
