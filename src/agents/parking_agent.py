import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

from constants import DEFAULT_HOST


class ParkingAgent(Agent):
    def __init__(self, jid, password, x, y, parking_spots):
        super().__init__(jid, password)
        self._x = x
        self._y = y
        self._parking_spots = parking_spots
        self._available_parking_spots = parking_spots

    def _prepare_check_parking_spots_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "inform")
        template.set_metadata("inform", "parking-availability")
        return template

    class CheckParkingSpots(CyclicBehaviour):
        async def run(self):
            print("Waiting for incoming messages...")
            msg = await self.receive(timeout=10)  # Wait for a message for 10 seconds
            if msg:
                print(f"Message received with content: {msg.body}")
                available_spots = self.get_available_parking_spots()
                reply = Message(to=msg.sender)  # Create a reply message
                reply.body = f"Available parking spots: {available_spots}"
                await self.send(reply)
                print(f"Reply sent: {reply.body}")
            else:
                print("No message received within the timeout period")

        def get_available_parking_spots(self):
            return self.get_available_parking_spots

    async def setup(self):
        check_parking_spots_behaviour = self.CheckParkingSpots()
        check_parking_spots_template = self._prepare_check_parking_spots_template()
        self.add_behaviour(check_parking_spots_behaviour, check_parking_spots_template)
