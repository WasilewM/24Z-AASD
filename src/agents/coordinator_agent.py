from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template


class RegionalCoordinator(Agent):
    def __init__(self, jid, password, x_from, x_to, y_from, y_to):
        super().__init__(jid, password)
        self._x_min = x_from
        self._x_max = x_to
        self._y_min = y_from
        self._y_max = y_to

    def _prepare_check_offers_template(self):
        template = Template()
        template.to = self.jid
        template.set_metadata("performative", "query-ref")
        template.set_metadata("action", "check-offers")
        return template

    def _prepare_make_reservation_template(self):
        template = Template()
        template.to = self.jid
        template.set_metadata("performative", "request")
        template.set_metadata("action", "make-reservation")
        return template

    def _prepare_modify_reservation_template(self):
        template = Template()
        template.to = self.jid
        template.set_metadata("performative", "request")
        template.set_metadata("action", "modify-reservation")
        return template

    class CheckParkingOffers(CyclicBehaviour):
        async def run(self):
            raise NotImplementedError

    class MakeReservation(CyclicBehaviour):
        async def run(self):
            raise NotImplementedError

    class ModifyReservation(CyclicBehaviour):
        async def run(self):
            raise NotImplementedError

    async def setup(self):
        check_offers_behaviour = self.CheckParkingOffers()
        check_offers_template = self._prepare_check_offers_template()

        make_reservation_behaviour = self.MakeReservation()
        make_reservation_template = self._prepare_make_reservation_template()

        modify_reservation_behaviour = self.ModifyReservation()
        modify_reservation_template = self._prepare_modify_reservation_template()

        self.add_behaviour(check_offers_behaviour, check_offers_template)
        self.add_behaviour(make_reservation_behaviour, make_reservation_template)
        self.add_behaviour(modify_reservation_behaviour, modify_reservation_template)
