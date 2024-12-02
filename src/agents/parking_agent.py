import spade
import json
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from constants import DEFAULT_HOST
from messages.check_parking import CheckParking


class ParkingAgent(Agent):
    def __init__(self, jid, password, x, y, parking_spots):
        super().__init__(jid, password)
        self._x = x
        self._y = y
        self._parking_spots = parking_spots
        self._available_parking_spots = [parking_spots for _ in range(24)]  # assuming 24h time period with 1h intervals

    def _prepare_check_parking_spots_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "inform")
        template.set_metadata("inform", "parking-availability")
        return template

    class CheckParkingSpots(CyclicBehaviour):
        """Behaviour for answering requests for parking spots"""

        async def run(self):
            print("Waiting for incoming messages...")
            msg = await self.receive(timeout=10)  # Wait for a message for 10 seconds
            if msg:
                print(f"Message received with content: {msg.body}")
                check_parking_message = CheckParking(**json.loads(msg.body))
                available_spots = self.get_available_parking_spots(
                    check_parking_message.time_start, check_parking_message.time_stop
                )
                reply = Message(
                    to=f"{msg.thread}",
                    body=available_spots,
                    thread=f"{self.jid}@{DEFAULT_HOST}",
                    metadata={"performative": "inform", "action": "check-parking"},
                )
                await self.send(reply)
                print(f"Reply sent: {reply}")
            else:
                print("No message received within the timeout period")

        def get_available_parking_spots(self, time_start, time_stop):
            max_available = self._parking_spots
            for i in range(time_start, time_stop):
                max_available = min(max_available, self._available_parking_spots[i])

            return max_available

    async def setup(self):
        check_parking_spots_behaviour = self.CheckParkingSpots()
        check_parking_spots_template = self._prepare_check_parking_spots_template()
        self.add_behaviour(check_parking_spots_behaviour, check_parking_spots_template)
