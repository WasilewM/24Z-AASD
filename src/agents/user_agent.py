import json
from typing import List
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from dataclasses import dataclass
import calendar
import time

from constants import DEFAULT_HOST
from messages.check_offers import CheckOffers
from messages.consolidated_offers import ConsolidatedOffers
from messages.reservation_request import RequestReservation
from messages.response import ReservationResponse

RECEIVE_TIMEOUT=1

class User(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.coordinators_jids = None
        self.pending_reservation = None     
        self.active_reservations = []     

    def _validate_timeslot(self, time_start, time_stop):
        current_time = calendar.timegm(time.gmtime()) # Get current timestamp in UTC timezone
        if not (time_start < time_stop and time_start > current_time):
            raise ValueError("Invalid timeslot")
    
    def _validate_location(self, x, y):
        if not (x >= 0 and y >= 0):
            raise ValueError("Invalid location")
        
    def _prepare_consolidated_offers_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "inform")
        template.set_metadata("action", "consolidated-offers")
        return template
    
    def _prepare_reservation_response_template(self):
        template = Template()
        template.to = f"{self.jid}@{DEFAULT_HOST}"
        template.set_metadata("performative", "inform")
        template.set_metadata("action", "reservation-response")
        return template

    def add_coordinator(self, coordinator_jid):
        self.coordinators_jids.append(coordinator_jid)

    async def request_parking_offers(self, x, y, time_start, time_stop):

        self._validate_location(x, y)
        self._validate_timeslot(time_start, time_stop)

        self.pending_reservation = Reservation(x, y, time_start, time_stop)

        check_offers_msg = CheckOffers(
            x=x,
            y=y,
            time_start=time_start,
            time_stop=time_stop
        )
        for coordinator_jid in self.coordinators_jids:
            to_send = Message(
                to=coordinator_jid,
                body=json.dumps(check_offers_msg.dict()),
                metadata={"performative": "query-ref", "action": "check-offers"}
            )
            await self.send(to_send)

    def choose_parking_offer(self, offers: List[dict]):
        #TODO implement logic of choosing an offer
        return offers[0]["parking_id"] if offers else None

    class MakeReservation(CyclicBehaviour):
        """Behaviour for making a reservation
            After receiving consolidated offers, the user chooses one offer and makes a reservation.
        """
        async def run(self):
            msg = await self.receive(timeout=RECEIVE_TIMEOUT)
            if msg:
                consolidated_offers = ConsolidatedOffers(**json.loads(msg.body))
                chosen_parking_id = self.agent.choose_parking_offer(consolidated_offers.offers)
                if self.agent.pending_reservation:
                    self.agent.pending_reservation.parking_id = chosen_parking_id
                    res = self.agent.pending_reservation
                    reservation_request = RequestReservation(res.time_start, res.time_stop, chosen_parking_id, self.agent.jid)
                    to_send = Message(to=consolidated_offers.sender, body=json.dumps(reservation_request.dict()), metadata={"performative": "request", "action": "make-reservation"})
                    await self.send(to_send)

    class AwaitReservationConfirmation(CyclicBehaviour):
        """Behaviour for waiting for reservation confirmation"""
        async def run(self):
            msg = await self.receive(timeout=RECEIVE_TIMEOUT)
            if msg:
                reservation_response = ReservationResponse(**json.loads(msg.body))
                if reservation_response.success:
                    #TODO What about reservation id?
                    self.agent.active_reservations.append(self.agent.pending_reservation)
                    self.agent.pending_reservation = None
                else:
                    #TODO Implement reservation failue handling
                    print("Reservation failed.")

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
    time_start: int
    time_stop: int
    parking_id: str
    