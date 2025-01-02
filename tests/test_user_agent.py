from unittest.mock import AsyncMock, MagicMock

import pytest
from spade.message import Message

from agents.user_agent import Reservation, User
from messages.consolidated_offers import ConsolidatedOffers, Offer
from messages.response import ReservationResponse


@pytest.fixture
def user_agent():
    agent = User("user@domain", "password")
    agent.pending_reservation = Reservation(x=1, y=1, time_start=5, time_stop=10, id=None, parking_id=None, coordinator_id=None)
    agent.client = AsyncMock()  # Mock the client to avoid actual network calls
    return agent


def test_validate_location_valid(user_agent):
    user_agent._validate_location(1, 1)


def test_validate_location_invalid(user_agent):
    with pytest.raises(ValueError):
        user_agent._validate_location(-1, 1)

    with pytest.raises(ValueError):
        user_agent._validate_location(1, -1)


def test_validate_timeslot_valid(user_agent):
    user_agent._validate_timeslot(5, 10)


def test_validate_timeslot_invalid(user_agent):
    with pytest.raises(ValueError):
        user_agent._validate_timeslot(10, 5)
    with pytest.raises(ValueError):
        user_agent._validate_timeslot(-1, 25)


@pytest.mark.asyncio
async def test_request_parking_offers(user_agent):
    user_agent.coordinators_jids = ["coordinator1@domain", "coordinator2@domain"]

    await user_agent.request_parking_offers(1, 1, 5, 10)

    user_agent.client.send.assert_called()
    assert len(user_agent.client.send.call_args_list) == 2


@pytest.mark.asyncio
async def test_make_reservation(user_agent):
    behaviour = user_agent.MakeReservation()
    user_agent.add_behaviour(behaviour)
    behaviour.agent = user_agent

    offer = Offer(parking_id="parking1", price=40, distance=1)
    consolidated_offers = ConsolidatedOffers(offers=[offer])

    msg = Message()
    msg.body = consolidated_offers.model_dump_json()
    msg.sender = "coordinator1@domain"

    behaviour.receive = AsyncMock(return_value=msg)
    user_agent.choose_parking_offer = MagicMock(return_value="parking1")

    await behaviour.run()

    user_agent.client.send.assert_called()


@pytest.mark.asyncio
async def test_make_reservation_no_offers(user_agent, caplog):
    behaviour = user_agent.MakeReservation()
    behaviour.agent = user_agent

    consolidated_offers = ConsolidatedOffers(offers=[])

    msg = Message()
    msg.body = consolidated_offers.model_dump_json()
    msg.sender = "coordinator1@domain"

    behaviour.receive = AsyncMock(return_value=msg)
    user_agent.choose_parking_offer = MagicMock(return_value="parking1")

    await behaviour.run()

    assert "No parking spots available" in caplog.text


@pytest.mark.asyncio
async def test_await_reservation_confirmation_success(user_agent):
    behaviour = user_agent.AwaitReservationConfirmation()
    behaviour.agent = user_agent

    reservation_response = ReservationResponse(success=True, reservation_id="res1", user_id="user@domain")

    msg = Message()
    msg.body = reservation_response.model_dump_json()

    behaviour.receive = AsyncMock(return_value=msg)
    user_agent.save_reservation = MagicMock()

    await behaviour.run()

    user_agent.save_reservation.assert_called_with(reservation_response, str(msg.sender))


@pytest.mark.asyncio
async def test_await_reservation_confirmation_failure(user_agent, caplog):
    behaviour = user_agent.AwaitReservationConfirmation()
    behaviour.agent = user_agent

    reservation_response = ReservationResponse(success=False, reservation_id="res1", user_id="user@domain")

    msg = Message()
    msg.body = reservation_response.model_dump_json()

    behaviour.receive = AsyncMock(return_value=msg)

    await behaviour.run()

    assert "Reservation failed" in caplog.text