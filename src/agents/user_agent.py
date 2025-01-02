from dataclasses import dataclass
from typing import List

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from constants import MESSAGE_TIMEOUT
from logger import logger
from messages.check_offers import CheckOffers
from messages.consolidated_offers import ConsolidatedOffers, Offer
from messages.modify_reservation import ModifyReservation
from messages.reservation_request import RequestReservation
from messages.response import ReservationResponse


class User(Agent):
    def __init__(self, jid, password, coordinators_jids=[]):
        super().__init__(jid, password)
        self.coordinators_jids = coordinators_jids
        self.pending_reservation = None
        # dictionary of active reservations {reservation_id: Reservation}
        self.active_reservations = {}

    def _validate_timeslot(self, time_start, time_stop):
        # TODO: correct time validation
        # current_time = calendar.timegm(time.gmtime())  # Get current timestamp in UTC timezone
        # if not (time_start < time_stop and time_start > current_time):
        #     raise ValueError("Invalid timeslot")
        if not (time_start < time_stop):
            logger.error(f"Invalid timeslot, time_start:{time_start},  time_stop: {time_stop}")
            raise ValueError("Invalid timeslot")
        if time_start < 0 or time_stop > 24:
            logger.error(f"Invalid timeslot, time_start:{time_start},  time_stop: {time_stop}")
            raise ValueError("Invalid timeslot")

    def _validate_location(self, x, y):
        if not (x >= 0 and y >= 0):
            logger.error(f"Invalid location, x:{x}, y: {y}, should be >= 0")
            raise ValueError("Invalid location")

    def _prepare_consolidated_offers_template(self):
        template = Template()
        template.to = f"{self.jid}"
        template.set_metadata("performative", "inform")
        template.set_metadata("action", "consolidated-offers")
        return template

    def _prepare_reservation_response_template(self):
        template = Template()
        template.to = f"{self.jid}"
        template.set_metadata("performative", "inform")
        template.set_metadata("action", "reservation-response")
        return template

    def add_coordinator(self, coordinator_jid):
        self.coordinators_jids.append(coordinator_jid)

    async def request_parking_offers(self, x, y, time_start, time_stop):

        logger.info(
            f"{str(self.jid)}: Requesting parking offers for x:{x}, y:{y}, time_start:{time_start}, time_stop:{time_stop}"
        )

        self._validate_location(x, y)
        self._validate_timeslot(time_start, time_stop)

        self.pending_reservation = Reservation(
            x=x, y=y, id=None, time_start=time_start, time_stop=time_stop, parking_id=None, coordinator_id=None
        )

        check_offers_msg = CheckOffers(x=x, y=y, time_start=time_start, time_stop=time_stop)
        for coordinator_jid in self.coordinators_jids:
            to_send = Message(
                to=coordinator_jid,
                body=check_offers_msg.model_dump_json(),
                metadata={"performative": "query-ref", "action": "check-offers"},
            )
            aioxmpp_msg = to_send.prepare()
            await self.client.send(aioxmpp_msg)
        logger.info(f"Check offers message sent to coordinators: {self.coordinators_jids}")

    async def request_reservation_modification(self, reservation_id, time_start, time_stop):
        self._validate_timeslot(time_start, time_stop)
        if reservation_id in self.active_reservations:
            self.pending_reservation = self.active_reservations[reservation_id]
            self.pending_reservation.time_start = time_start
            self.pending_reservation.time_stop = time_stop
            coordinator_id = self.pending_reservation.coordinator_id
            parking_id = self.pending_reservation.parking_id
            modify_reservation_msg = ModifyReservation(
                reservation_id=reservation_id,
                time_start=time_start,
                time_stop=time_stop,
                user_id=str(self.jid),
                parking_id=parking_id,
            )
            to_send = Message(
                to=f"{coordinator_id}",
                body=modify_reservation_msg.model_dump_json(),
                metadata={"performative": "request", "action": "modify-reservation"},
            )
            aioxmpp_msg = to_send.prepare()
            await self.client.send(aioxmpp_msg)
            logger.info(f"Modify reservation message sent: {modify_reservation_msg.model_dump_json()}")
        else:
            raise Exception("Reservation not found")

    def choose_parking_offer(self, offers: List[Offer]):
        # TODO implement logic of choosing an offer
        try:
            chosen_offer = offers[0].parking_id if offers else ""
            logger.info(f"Chosen parking offer: {chosen_offer}")
            return chosen_offer
        except Exception:
            logger.error(f"Cannot choose a parking offer from: {offers}")
            return ""

    def save_reservation(self, reservation_response: ReservationResponse, coordinator_id):
        if not self.pending_reservation:
            raise Exception("No pending reservation")
        # If reservation id is set -> there was a modification request
        if self.pending_reservation.id:
            # The old reservation will be replaced by the new one with a new id
            self.active_reservations.pop(self.pending_reservation.id)
        self.pending_reservation.id = reservation_response.reservation_id
        self.pending_reservation.coordinator_id = coordinator_id
        self.active_reservations[reservation_response.reservation_id] = self.pending_reservation
        self.pending_reservation = None

    class MakeReservation(CyclicBehaviour):
        """Behaviour for making a reservation
        After receiving consolidated offers, the user chooses one offer and makes a reservation.
        """

        async def run(self):
            msg = await self.receive(timeout=MESSAGE_TIMEOUT)
            if msg:
                consolidated_offers = ConsolidatedOffers.model_validate_json(msg.body)
                logger.info(
                    f"{str(self.agent.jid)}: Received ConsolidatedOffers from {msg.sender}: {consolidated_offers.model_dump_json()}"
                )
                if consolidated_offers.offers == []:
                    logger.error(f"{str(self.agent.jid)}: No parking spots available")
                    return
                
                chosen_parking_id = self.agent.choose_parking_offer(consolidated_offers.offers)
                if self.agent.pending_reservation:
                    self.agent.pending_reservation.parking_id = chosen_parking_id
                    res = self.agent.pending_reservation
                    reservation_request = RequestReservation(
                        time_start=res.time_start,
                        time_stop=res.time_stop,
                        parking_id=chosen_parking_id,
                        user_id=str(self.agent.jid),
                    )
                    to_send = Message(
                        to=str(msg.sender),
                        body=reservation_request.model_dump_json(),
                        metadata={"performative": "request", "action": "make-reservation"},
                    )
                    await self.send(to_send)
                    logger.info(
                        f"{str(self.agent.jid)}: Reservation request to {str(msg.sender)} sent: {reservation_request.model_dump_json()}"
                    )

    class AwaitReservationConfirmation(CyclicBehaviour):
        """Behaviour for waiting for reservation confirmation"""

        async def run(self):
            msg = await self.receive(timeout=MESSAGE_TIMEOUT)
            if msg:
                reservation_response = ReservationResponse.model_validate_json(msg.body)
                logger.info(
                    f"{str(self.agent.jid)}: Received ReservationResponse: {reservation_response.model_dump_json()}"
                )
                if reservation_response.success:
                    self.agent.save_reservation(reservation_response, str(msg.sender))
                    logger.info(
                        f"{str(self.agent.jid)}: Reservation successful. Reservation id: {reservation_response.reservation_id}"
                    )
                else:
                    # TODO Implement reservation failue handling
                    logger.error(f"{str(self.agent.jid)}: Reservation failed.")

    async def setup(self):

        make_reservation_behaviour = self.MakeReservation()
        make_reservation_template = self._prepare_consolidated_offers_template()
        self.add_behaviour(make_reservation_behaviour, make_reservation_template)

        await_reservation_confirmation_behaviour = self.AwaitReservationConfirmation()
        await_reservation_confirmation_template = self._prepare_reservation_response_template()
        self.add_behaviour(await_reservation_confirmation_behaviour, await_reservation_confirmation_template)


@dataclass
class Reservation:
    x: int
    y: int
    id: str
    time_start: int
    time_stop: int
    parking_id: str
    coordinator_id: str
