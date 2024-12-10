import spade
import string
import json
import random
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from constants import DEFAULT_HOST, PARKING_AGENT_MESSAGE_TIMEOUT
from messages.check_parking import CheckParking
from messages.parking_availability import ParkingAvailable
from messages.reservation_request import RequestReservation
from messages.response import ReservationResponse
from messages.modify_reservation import ModifyReservation


class ParkingAgent(Agent):
    def __init__(self, jid, password, x, y, parking_spots):
        super().__init__(jid, password)
        self._x = x
        self._y = y
        self._parking_spots = parking_spots
        self._available_parking_spots = [
            parking_spots for _ in range(24)
        ]  # a list with number of free/available spots at a given hour

    def _prepare_check_parking_spots_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "inform")
        template.set_metadata("inform", "parking-availability")
        return template

    def _prepare_make_reservation_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "inform")
        template.set_metadata("inform", "make-reservation")
        return template

    def _prepare_modify_reservation_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "inform")
        template.set_metadata("inform", "modify-reservation")
        return template

    class CheckParkingSpots(CyclicBehaviour):
        """Behaviour for answering requests for parking spots"""

        async def run(self):
            msg = await self.receive(timeout=PARKING_AGENT_MESSAGE_TIMEOUT)
            if msg:
                check_parking_message = CheckParking(**json.loads(msg.body))
                available_spots = self.get_available_parking_spots(
                    check_parking_message.time_start, check_parking_message.time_stop
                )
                reply_body = ParkingAvailable(self.jid, 40, self._x, self._y, True if available_spots else False)
                reply = Message(
                    to=msg.sender,
                    body=str(reply_body.dict()),
                    thread=msg.thread,
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

    class MakeReservation(CyclicBehaviour):
        """Behaviour for answering reservation requests"""

        async def run(self):
            msg = await self.receive(timeout=PARKING_AGENT_MESSAGE_TIMEOUT)
            if msg:
                request = RequestReservation(**json.loads(msg.body))
                reservation_status = self.try_to_reserve_parking_spot(request.time_start, request.time_stop)
                reservation_id = self.generate_reservation_id() if reservation_status else ""

                reply_body = ReservationResponse(reservation_status, request.user_id, reservation_id)
                reply = Message(
                    to=msg.sender,
                    body=str(reply_body.dict()),
                    thread=msg.thread,
                    metadata={"performative": "inform", "action": "make-reservation"},
                )
                await self.send(reply)
                print(f"Reply sent: {reply}")
            else:
                print("No message received within the timeout period")

        def try_to_resere_parking_spot(self, time_start, time_stop):
            if self.get_available_parking_spots(time_start, time_stop):
                for i in range(time_start, time_stop):
                    self._available_parking_spots[i] -= 1
                return True
            return False

        def get_available_parking_spots(self, time_start, time_stop):
            max_available = self._parking_spots
            for i in range(time_start, time_stop):
                max_available = min(max_available, self._available_parking_spots[i])

            return max_available

        def generate_reservation_id(length=12):
            return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    class ModifyReservation(CyclicBehaviour):
        """Behaviour for answering reservation modification requests"""

        async def run(self):
            msg = await self.receive(timeout=PARKING_AGENT_MESSAGE_TIMEOUT)
            if msg:
                request = ModifyReservation(**json.loads(msg.body))
                # @TODO implement logic and parking spots checking for modification requests
                reservation_status = random.choice([True, False])

                reply_body = ReservationResponse(reservation_status, request.user_id, request.reservation_id)
                reply = Message(
                    to=msg.sender,
                    body=str(reply_body.dict()),
                    thread=msg.thread,
                    metadata={"performative": "inform", "action": "modify-reservation"},
                )
                await self.send(reply)
                print(f"Reply sent: {reply}")
            else:
                print("No message received within the timeout period")

    async def setup(self):
        check_parking_spots_behaviour = self.CheckParkingSpots()
        check_parking_spots_template = self._prepare_check_parking_spots_template()

        make_reservation_behaviour = self.MakeReservation()
        make_reservation_template = self._prepare_make_reservation_template()

        modify_reservation_behaviour = self.ModifyReservation()
        modify_reservation_template = self._prepare_modify_reservation_template()

        self.add_behaviour(check_parking_spots_behaviour, check_parking_spots_template)
        self.add_behaviour(make_reservation_behaviour, make_reservation_template)
        self.add_behaviour(modify_reservation_behaviour, modify_reservation_template)
