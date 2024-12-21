import uuid
from datetime import datetime

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from constants import PARKING_AGENT_MESSAGE_TIMEOUT
from logger import logger
from messages.check_parking import CheckParking
from messages.modify_reservation import ModifyReservation
from messages.parking_availability import ParkingAvailable
from messages.reservation_request import RequestReservation
from messages.response import ReservationResponse


class ParkingAgent(Agent):
    def __init__(self, jid, password, x, y, parking_spots, parking_price=40):
        super().__init__(jid, password)
        self._x = x
        self._y = y
        self._parking_spots = parking_spots
        self._available_parking_spots = [
            parking_spots for _ in range(24)
        ]  # a list with number of free/available spots at a given hour
        self._parking_price = parking_price
        self._users_reservations = {}  # {user_jid: {reservation_id: [time_start, time_stop]}}

    def _prepare_check_parking_spots_template(self):
        template = Template()
        template.to = f"{self.jid}"
        template.set_metadata("performative", "query-ref")
        template.set_metadata("action", "check-parking")
        return template

    def _prepare_make_reservation_template(self):
        template = Template()
        template.to = f"{self.jid}"
        template.set_metadata("performative", "request")
        template.set_metadata("action", "make-reservation")
        return template

    def _prepare_modify_reservation_template(self):
        template = Template()
        template.to = f"{self.jid}"
        template.set_metadata("performative", "request")
        template.set_metadata("action", "modify-reservation")
        return template

    def get_available_parking_spots(self, time_start, time_stop):
        max_available = self._parking_spots
        for i in range(time_start, time_stop):
            max_available = min(max_available, self._available_parking_spots[i])
        return max_available

    def try_to_reserve_parking_spot(self, time_start, time_stop):
        if self.get_available_parking_spots(time_start, time_stop):
            for i in range(time_start, time_stop):
                self._available_parking_spots[i] -= 1

            logger.info({i:self._available_parking_spots[i] for i in range(len(self._available_parking_spots))})
            return True
        return False

    def free_parking_spots(self, time_start, time_stop):
        for i in range(time_start, time_stop):
            self._available_parking_spots[i] += 1

    @staticmethod
    def generate_reservation_id(user_jid):
        # without the time part each request from the same user gets the same uuid
        res_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_jid}{datetime.now()}")
        return str(res_id)

    def store_parking_info_for_user(self, user_jid, reservation_id, time_start, time_stop):
        if user_jid not in self._users_reservations:
            self._users_reservations[user_jid] = {}
        self._users_reservations[user_jid][reservation_id] = [time_start, time_stop]

    def user_is_reservation_owner(self, user_jid, reservation_id):
        return True if reservation_id in self._users_reservations.get(user_jid, []) else False

    class CheckParkingSpots(CyclicBehaviour):
        """Behaviour for answering requests for parking spots"""

        async def run(self):
            msg = await self.receive(timeout=PARKING_AGENT_MESSAGE_TIMEOUT)
            if msg:
                check_parking_message = CheckParking.model_validate_json(msg.body)
                logger.info(
                    f"{str(self.agent.jid)}: Received CheckParking message: {check_parking_message.model_dump_json()}"
                )
                available_spots = self.agent.get_available_parking_spots(
                    check_parking_message.time_start, check_parking_message.time_stop
                )
                reply_body = ParkingAvailable(
                    parking_id=str(self.agent.jid),
                    parking_price=self.agent._parking_price,
                    parking_x=self.agent._x,
                    parking_y=self.agent._y,
                    available=True if available_spots else False,
                )
                reply = Message(
                    to=str(msg.sender),
                    body=reply_body.model_dump_json(),
                    thread=msg.thread,
                    metadata={"performative": "inform", "action": "parking-availability"},
                )
                await self.send(reply)
                logger.info(f"{str(self.agent.jid)}: Reply to {msg.sender} sent: {reply_body.model_dump_json()}")

    class MakeReservation(CyclicBehaviour):
        """Behaviour for answering reservation requests"""

        async def run(self):
            msg = await self.receive(timeout=PARKING_AGENT_MESSAGE_TIMEOUT)
            if msg:
                request = RequestReservation.model_validate_json(msg.body)
                reservation_status = self.agent.try_to_reserve_parking_spot(request.time_start, request.time_stop)
                reservation_id = ParkingAgent.generate_reservation_id(request.user_id) if reservation_status else ""
                self.agent.store_parking_info_for_user(
                    request.user_id, reservation_id, request.time_start, request.time_stop
                )

                reply_body = ReservationResponse(
                    success=reservation_status, user_id=request.user_id, reservation_id=reservation_id
                )
                reply = Message(
                    to=str(msg.sender),
                    body=reply_body.model_dump_json(),
                    thread=msg.thread,
                    metadata={"performative": "inform", "action": "reservation-response"},
                )
                await self.send(reply)
                logger.info(f"{str(self.agent.jid)}: Reply to {msg.sender} sent: {reply_body.model_dump_json()}")

    class ModifyReservation(CyclicBehaviour):
        """Behaviour for answering reservation modification requests"""

        async def run(self):
            msg = await self.receive(timeout=PARKING_AGENT_MESSAGE_TIMEOUT)
            if msg:
                request = ModifyReservation.model_validate_json(msg.body)
                logger.info(f"{str(self.agent.jid)}: Received ModifyReservation: {str(request.dict())}")
                if not self.agent.user_is_reservation_owner(request.user_id, request.reservation_id):
                    reservation_status = False
                else:
                    reservation_status = self.agent.try_to_reserve_parking_spot(request.time_start, request.time_stop)
                    if reservation_status:
                        new_reservation_id = (
                            ParkingAgent.generate_reservation_id(request.user_id) if reservation_status else ""
                        )
                        logger.info(
                            f"{str(self.agent.jid)}: New reservation id has been generated: {new_reservation_id}, {request.reservation_id}"
                        )
                        request.reservation_id = new_reservation_id
                        self.agent.store_parking_info_for_user(
                            request.user_id, request.reservation_id, request.time_start, request.time_stop
                        )
                        self.agent.free_parking_spots(request.time_start, request.time_stop)

                reply_body = ReservationResponse(
                    success=reservation_status, user_id=request.user_id, reservation_id=request.reservation_id
                )
                reply = Message(
                    to=str(msg.sender),
                    body=reply_body.model_dump_json(),
                    thread=msg.thread,
                    metadata={"performative": "inform", "action": "reservation-response"},
                )
                await self.send(reply)
                logger.info(f"{str(self.agent.jid)}: Reply to {msg.sender} sent: {reply_body.model_dump_json()}")

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
