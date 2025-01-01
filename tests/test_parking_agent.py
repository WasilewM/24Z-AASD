from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import NAMESPACE_DNS, uuid5

import pytest
from spade.message import Message

from agents.parking_agent import ParkingAgent
from messages.check_parking import CheckParking
from messages.modify_reservation import ModifyReservation
from messages.parking_availability import ParkingAvailable
from messages.reservation_request import RequestReservation
from messages.response import ReservationResponse


def language_map_to_json(language_map):
    language_map_dict = list(language_map.values())
    return language_map_dict[0]


@pytest.fixture
def parking_agent():
    agent = ParkingAgent(
        jid="parking@domain",
        password="password",
        x=5,
        y=10,
        parking_spots=10,
        parking_price=50
    )
    agent.client = AsyncMock()  # Mock client to avoid actual network communication
    return agent


@pytest.mark.asyncio
async def test_get_available_parking_spots(parking_agent):
    parking_agent._available_parking_spots = [5] * 24
    available = parking_agent.get_available_parking_spots(2, 5)
    assert available == 5


@pytest.mark.asyncio
async def test_get_available_parking_spots_limited(parking_agent):
    parking_agent._available_parking_spots[3] = 3
    available = parking_agent.get_available_parking_spots(2, 5)
    assert available == 3


@pytest.mark.asyncio
async def test_try_to_reserve_parking_spot_available(parking_agent):
    parking_agent._available_parking_spots = [5] * 24
    reserved = parking_agent.try_to_reserve_parking_spot(2, 5)
    assert reserved is True
    assert parking_agent._available_parking_spots[2] == 4
    assert parking_agent._available_parking_spots[3] == 4
    assert parking_agent._available_parking_spots[4] == 4

    
@pytest.mark.asyncio
async def test_try_to_reserve_parking_spot_no_available(parking_agent):
    parking_agent._available_parking_spots[3] = 0
    reserved = parking_agent.try_to_reserve_parking_spot(2, 5)
    assert reserved is False


@pytest.mark.asyncio
async def test_check_parking_spots_behaviour(parking_agent):
    behaviour = parking_agent.CheckParkingSpots()
    parking_agent.add_behaviour(behaviour)
    behaviour.agent = parking_agent

    check_parking_msg = CheckParking(time_start=2, time_stop=5)
    msg = Message()
    msg.body = check_parking_msg.model_dump_json()
    msg.sender = "coordinator@domain"
    msg.thread = "user@domain"

    behaviour.receive = AsyncMock(return_value=msg)

    await behaviour.run()

    parking_agent.client.send.assert_called()
    sent_msg = parking_agent.client.send.call_args[0][0]
    body = language_map_to_json(sent_msg.body)
    response = ParkingAvailable.model_validate_json(body)
    assert response.available is True
    assert response.parking_price == parking_agent._parking_price


@pytest.mark.asyncio
async def test_make_reservation_behaviour(parking_agent):
    behaviour = parking_agent.MakeReservation()
    parking_agent.add_behaviour(behaviour)
    behaviour.agent = parking_agent

    reservation_request = RequestReservation(time_start=2, time_stop=5, user_id="user@domain", parking_id="parking@domain")
    msg = Message()
    msg.body = reservation_request.model_dump_json()
    msg.sender = "coordinator@domain"

    behaviour.receive = AsyncMock(return_value=msg)
    parking_agent.try_to_reserve_parking_spot = MagicMock(return_value=True)

    await behaviour.run()

    parking_agent.client.send.assert_called()
    sent_msg = parking_agent.client.send.call_args[0][0]
    body = language_map_to_json(sent_msg.body)
    response = ReservationResponse.model_validate_json(body)
    assert response.success is True
    assert response.user_id == "user@domain"
    assert response.reservation_id is not None


@pytest.mark.asyncio
async def test_modify_reservation_behaviour(parking_agent):
    behaviour = parking_agent.ModifyReservation()
    parking_agent.add_behaviour(behaviour)
    behaviour.agent = parking_agent

    user_id = "user@domain"
    reservation_id = str(uuid5(NAMESPACE_DNS, f"{user_id}{datetime.now()}"))
    parking_agent.store_parking_info_for_user(user_id, reservation_id, 2, 5)

    modify_request = ModifyReservation(
        user_id=user_id, reservation_id=reservation_id, time_start=6, time_stop=8, parking_id="parking@domain"
    )
    msg = Message()
    msg.body = modify_request.model_dump_json()
    msg.sender = "coordinator@domain"

    behaviour.receive = AsyncMock(return_value=msg)
    parking_agent.try_to_reserve_parking_spot = MagicMock(return_value=True)

    await behaviour.run()

    sent_msg = parking_agent.client.send.call_args[0][0]
    body = language_map_to_json(sent_msg.body)
    response = ReservationResponse.model_validate_json(body)
    assert response.success is True
    assert response.user_id == user_id
    assert response.reservation_id != reservation_id


@pytest.mark.asyncio
async def test_generate_reservation_id_unique(parking_agent):
    user_id = "user@domain"
    reservation_id1 = parking_agent.generate_reservation_id(user_id)
    reservation_id2 = parking_agent.generate_reservation_id(user_id)
    assert reservation_id1 != reservation_id2
