from unittest.mock import AsyncMock

import pytest
from spade.message import Message

from agents.coordinator_agent import RegionalCoordinator
from messages.check_offers import CheckOffers
from messages.consolidated_offers import ConsolidatedOffers
from messages.modify_reservation import ModifyReservation
from messages.parking_availability import ParkingAvailable
from messages.reservation_request import RequestReservation


def language_map_to_json(language_map):
    language_map_dict = list(language_map.values())
    return language_map_dict[0]


@pytest.fixture
def regional_coordinator():
    agent = RegionalCoordinator(
        jid="coordinator@domain",
        password="password",
        x_from=0,
        x_to=10,
        y_from=0,
        y_to=10,
        parking_agents_jids=["parking1@domain", "parking2@domain"],
    )
    agent.client = AsyncMock()  # Mock client to avoid actual network communication
    return agent


@pytest.mark.asyncio
async def test_check_offers_behaviour_within_region(regional_coordinator):
    behaviour = regional_coordinator.CheckParkingOffers()
    behaviour.agent = regional_coordinator

    check_offers_msg = CheckOffers(x=5, y=5, time_start=2, time_stop=5)
    msg = Message()
    msg.body = check_offers_msg.model_dump_json()
    msg.sender = "user@domain"

    behaviour.receive = AsyncMock(return_value=msg)

    await behaviour.run()

    assert regional_coordinator.client.send.call_count == len(regional_coordinator._parking_agents_jids)


@pytest.mark.asyncio
async def test_check_offers_behaviour_outside_region(regional_coordinator):
    behaviour = regional_coordinator.CheckParkingOffers()
    behaviour.agent = regional_coordinator

    check_offers_msg = CheckOffers(x=15, y=15, time_start=2, time_stop=5)
    msg = Message()
    msg.body = check_offers_msg.model_dump_json()
    msg.sender = "user@domain"

    behaviour.receive = AsyncMock(return_value=msg)
    regional_coordinator.send = AsyncMock()

    await behaviour.run()

    regional_coordinator.send.assert_not_called()


@pytest.mark.asyncio
async def test_await_parking_availability_behaviour(regional_coordinator):
    behaviour = regional_coordinator.AwaitParkingAvailability()
    behaviour.agent = regional_coordinator

    user_id = "user@domain"
    regional_coordinator._per_user_data[user_id] = {
        "parkings": [],
        "destination": (5, 5),
    }

    parking_msg = ParkingAvailable(
        parking_id="parking1@domain",
        parking_price=10,
        parking_x=4,
        parking_y=4,
        available=True,
    )
    msg = Message()
    msg.body = parking_msg.model_dump_json()
    msg.sender = "parking1@domain"
    msg.thread = user_id

    behaviour.receive = AsyncMock(return_value=msg)

    await behaviour.run()
    
    parking_msg.parking_id = "parking2@domain"
    msg = Message()
    msg.body = parking_msg.model_dump_json()
    msg.sender = "parking2@domain"
    msg.thread = user_id
    
    behaviour.receive = AsyncMock(return_value=msg)
    
    await behaviour.run()

    consolidated_msg = regional_coordinator.client.send.call_args[0][0]
    assert str(consolidated_msg.to) == user_id
    response = ConsolidatedOffers.model_validate_json(language_map_to_json(consolidated_msg.body))
    assert len(response.offers) > 0


@pytest.mark.asyncio
async def test_make_reservation_behaviour(regional_coordinator):
    behaviour = regional_coordinator.MakeReservation()
    behaviour.agent = regional_coordinator

    reservation_request = RequestReservation(
        parking_id="parking1@domain",
        time_start=2,
        time_stop=5,
        user_id="user@domain"
    )
    msg = Message()
    msg.body = reservation_request.model_dump_json()
    msg.sender = "user@domain"

    behaviour.receive = AsyncMock(return_value=msg)

    await behaviour.run()

    sent_msg = regional_coordinator.client.send.call_args[0][0]
    assert str(sent_msg.to) == reservation_request.parking_id


@pytest.mark.asyncio
async def test_modify_reservation_behaviour(regional_coordinator):
    behaviour = regional_coordinator.ModifyReservation()
    behaviour.agent = regional_coordinator

    modification_request = ModifyReservation(
        parking_id="parking1@domain",
        time_start=3,
        time_stop=6,
        reservation_id="reservation1",
        user_id="user@domain"
    )
    msg = Message()
    msg.body = modification_request.model_dump_json()
    msg.sender = "user@domain"

    behaviour.receive = AsyncMock(return_value=msg)

    await behaviour.run()

    sent_msg = regional_coordinator.client.send.call_args[0][0]
    assert str(sent_msg.to) == modification_request.parking_id
