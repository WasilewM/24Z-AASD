import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from constants import MESSAGE_TIMEOUT, OFFERS_TO_RETURN
from logger import logger
from messages.check_offers import CheckOffers
from messages.check_parking import CheckParking
from messages.consolidated_offers import ConsolidatedOffers, Offer
from messages.modify_reservation import ModifyReservation
from messages.parking_availability import ParkingAvailable
from messages.reservation_request import RequestReservation
from messages.response import ReservationResponse


class RegionalCoordinator(Agent):
    def __init__(self, jid, password, x_from, x_to, y_from, y_to, parking_agents_jids=list()):
        super().__init__(jid, password)
        self._x_min = x_from
        self._x_max = x_to
        self._y_min = y_from
        self._y_max = y_to
        self._parking_agents_jids = parking_agents_jids  # list of parking agents jids within the region
        # {user_jid: {parkings: [parking_available, ...], destination: (x, y)}}
        self._per_user_data = {}

    def _prepare_check_offers_template(self):
        template = Template()
        template.to = f"{self.jid}"
        template.set_metadata("performative", "query-ref")
        template.set_metadata("action", "check-offers")
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

    def _prepare_parking_availability_template(self):
        template = Template()
        template.to = f"{self.jid}"
        template.set_metadata("performative", "inform")
        template.set_metadata("action", "parking-availability")
        return template

    def _prepare_reservation_response_template(self):
        template = Template()
        template.to = f"{self.jid}"
        template.set_metadata("performative", "inform")
        template.set_metadata("action", "reservation-response")
        return template

    def _calculate_distance(self, x_user, y_user, x_parking, y_parking):
        return round(((x_user - x_parking) ** 2 + (y_user - y_parking) ** 2) ** 0.5, 2)

    def _consolidate_offers_per_user(self, user) -> ConsolidatedOffers:
        dest_x, dest_y = self._per_user_data[user]["destination"]
        free_parkings = [parking for parking in self._per_user_data[user]["parkings"] if parking.available]
        offers = []
        for parking in free_parkings:
            offer = Offer(
                parking_id=parking.parking_id,
                price=parking.parking_price,
                distance=self._calculate_distance(dest_x, dest_y, parking.parking_x, parking.parking_y),
            )
            offers.append(offer)
        offers = sorted(offers, key=lambda x: x.distance)
        offers = offers[:OFFERS_TO_RETURN]
        return ConsolidatedOffers(offers=offers)

    class CheckParkingOffers(CyclicBehaviour):
        """Behaviour for checking parking offers"""

        def _check_if_request_is_within_region(self, request_x, request_y):
            return (
                self.agent._x_min <= request_x < self.agent._x_max
                and self.agent._y_min <= request_y < self.agent._y_max
            )

        async def run(self):
            msg = await self.receive(timeout=MESSAGE_TIMEOUT)
            if msg:
                check_offers_message = CheckOffers.model_validate_json(msg.body)
                if self._check_if_request_is_within_region(int(check_offers_message.x), int(check_offers_message.y)):
                    user_id = str(msg.sender).split("/")[0]
                    logger.info(f"{str(self.agent.jid)}: CheckOffers message received from {user_id}")
                    self.agent._per_user_data[str(user_id)] = {
                        "parkings": [],
                        "destination": (check_offers_message.x, check_offers_message.y),
                    }
                    check_parking = CheckParking(
                        time_start=check_offers_message.time_start, time_stop=check_offers_message.time_stop
                    ).model_dump_json()
                    for jid in self.agent._parking_agents_jids:
                        logger.info(f"{str(self.agent.jid)}: Sending to jid: {jid}")
                        # user_jid@host in message.thread, need in response from parking agent
                        to_send = Message(
                            to=jid,
                            body=check_parking,
                            thread=f"{user_id}",
                            metadata={"performative": "query-ref", "action": "check-parking"},
                        )
                        await self.send(to_send)
                        logger.info(f"{str(self.agent.jid)}: CheckParking message sent to {to_send.to}")

    class MakeReservation(CyclicBehaviour):
        """Behaviour for making reservation"""

        async def run(self):
            msg = await self.receive(timeout=MESSAGE_TIMEOUT)
            if msg:
                reservation_request = RequestReservation.model_validate_json(msg.body)
                logger.info(f"{str(self.agent.jid)}: RequestReservation received from {msg.sender}")
                request_to_parking = Message(
                    to=reservation_request.parking_id,
                    body=msg.body,
                    metadata={"performative": "request", "action": "make-reservation"},
                )
                await self.send(request_to_parking)
                logger.info(f"{str(self.agent.jid)}: RequestReservation sent to {request_to_parking.to}")

    class ModifyReservation(CyclicBehaviour):
        """Behaviour for modifying reservation"""

        async def run(self):
            msg = await self.receive(timeout=MESSAGE_TIMEOUT)
            if msg:
                modification_request = ModifyReservation.model_validate_json(msg.body)
                logger.info(f"{str(self.agent.jid)}: ModifyReservation received from {msg.sender}")
                request_to_parking = Message(
                    to=modification_request.parking_id,
                    body=msg.body,
                    metadata={"performative": "request", "action": "modify-reservation"},
                )
                await self.send(request_to_parking)
                logger.info(f"{str(self.agent.jid)}: ModifyReservation sent to {request_to_parking.to}")

    class AwaitParkingAvailability(CyclicBehaviour):
        """Behaviour for waiting for parking availability, when all parkings are checked
        then consolidated offers are sent to user"""

        async def run(self):
            msg = await self.receive(timeout=MESSAGE_TIMEOUT)
            if msg:
                parking_available = ParkingAvailable.model_validate_json(msg.body)
                logger.info(f"{str(self.agent.jid)}: ParkingAvailable received from {msg.sender}")
                user = msg.thread
                self.agent._per_user_data[user]["parkings"].append(parking_available)

                if len(self.agent._per_user_data[user]["parkings"]) == len(self.agent._parking_agents_jids):
                    logger.info(f"{str(self.agent.jid)}: All parkings Data received.")
                    consolidated_offers = self.agent._consolidate_offers_per_user(user)
                    consolidated_offers = consolidated_offers.model_dump_json()
                    self.agent._per_user_data.pop(user)
                    to_send = Message(
                        to=user,
                        body=consolidated_offers,
                        metadata={"performative": "inform", "action": "consolidated-offers"},
                    )
                    await self.send(to_send)
                    logger.info(f"{str(self.agent.jid)}: ConsolidatedOffers sent to {to_send.to}")

    class AwaitReservationConfirmation(CyclicBehaviour):
        """Behaviour for waiting for reservation making or changing confirmation"""

        async def run(self):
            msg = await self.receive(timeout=MESSAGE_TIMEOUT)
            if msg:
                reservation_response = ReservationResponse.model_validate_json(msg.body)
                logger.info(f"{str(self.agent.jid)}: ReservationResponse received from {msg.sender}")
                to_send = Message(
                    to=reservation_response.user_id,
                    body=msg.body,
                    metadata={"performative": "inform", "action": "reservation-response"},
                )
                await self.send(to_send)
                logger.info(f"{str(self.agent.jid)}: ReservationResponse sent to {to_send.to}")

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
