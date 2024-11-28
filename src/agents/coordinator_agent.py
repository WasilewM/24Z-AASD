import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from constants import DEFAULT_HOST
from messages.check_offers import CheckOffers
from messages.check_parking import CheckParking
from messages.parking_availability import ParkingAvailable


class RegionalCoordinator(Agent):
    def __init__(self, jid, password, x_from, x_to, y_from, y_to, parking_agents_jids):
        super().__init__(jid, password)
        self._x_min = x_from
        self._x_max = x_to
        self._y_min = y_from
        self._y_max = y_to
        self._parking_agents_jids = parking_agents_jids  # list of parking agents jids within the region
        self._per_user_data = {}

    def _prepare_check_offers_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "query-ref")
        template.set_metadata("action", "check-offers")
        return template

    def _prepare_make_reservation_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "request")
        template.set_metadata("action", "make-reservation")
        return template

    def _prepare_modify_reservation_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "request")
        template.set_metadata("action", "modify-reservation")
        return template

    def _prepare_parking_availability_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "query-ref")
        template.set_metadata("action", "parking-availability")
        return template

    def _prepare_reservation_response_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("action", "reservation-response")
        return template

    class CheckParkingOffers(CyclicBehaviour):
        def _check_if_request_is_within_region(self, request_x, request_y):
            return self.agent._x_min <= request_x < self.agent._x_max and self.agent._y_min <= request_y < self.agent._y_max

        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                check_offers_message = CheckOffers(**json.loads(msg.body))
                self.agent._per_user_data[check_offers_message.sender] = []
                if self._check_if_request_is_within_region(check_offers_message.x, check_offers_message.y):
                    check_parking = str(CheckParking(check_offers_message.time_start,
                                        check_offers_message.time_stop).dict())
                    for jid in self.agent._parking_agents_jids:
                        # user_jid@host in message.thread, need in response from parking agent
                        to_send = Message(to=jid, body=check_parking, thread=check_offers_message.sender, metadata={
                                          "performative": "query-ref", "action": "check-parking"})
                        await self.send(to_send)

    class MakeReservation(CyclicBehaviour):
        async def run(self):
            raise NotImplementedError

    class ModifyReservation(CyclicBehaviour):
        async def run(self):
            raise NotImplementedError

    class AwaitParkingAvailability(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                parking_available = ParkingAvailable(**json.loads(msg.body))
                raise NotImplementedError

    class AwaitReservationConfirmation(CyclicBehaviour):
        # while making and modyfing reservation
        async def run(self):
            raise NotImplementedError

    async def setup(self):
        check_offers_behaviour = self.CheckParkingOffers()
        check_offers_template = self._prepare_check_offers_template()

        make_reservation_behaviour = self.MakeReservation()
        make_reservation_template = self._prepare_make_reservation_template()

        modify_reservation_behaviour = self.ModifyReservation()
        modify_reservation_template = self._prepare_modify_reservation_template()

        await_parking_availability_behaviour = self.AwaitParkingAvailability()
        await_parking_availability_template = self._prepare_parking_availability_template()

        await_reservation_confirmation_behaviour = self.AwaitReservationConfirmation()
        await_reservation_confirmation_template = self._prepare_reservation_response_template()

        self.add_behaviour(check_offers_behaviour, check_offers_template)
        self.add_behaviour(make_reservation_behaviour, make_reservation_template)
        self.add_behaviour(modify_reservation_behaviour, modify_reservation_template)
        self.add_behaviour(await_parking_availability_behaviour, await_parking_availability_template)
        self.add_behaviour(await_reservation_confirmation_behaviour, await_reservation_confirmation_template)
