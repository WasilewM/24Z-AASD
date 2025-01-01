import asyncio
import os
import sys
import time

import spade

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.coordinator_agent import RegionalCoordinator
from agents.parking_agent import ParkingAgent
from agents.user_agent import User
from constants import DEFAULT_HOST
from logger import logger

AGENT_PASSWORD = "admin"


async def main():
    parking1 = ParkingAgent(f"parking100@{DEFAULT_HOST}", AGENT_PASSWORD, 1, 1, 1)
    await parking1.start()

    # coordinates from 0,0 to 10,10
    coordinator1 = RegionalCoordinator(
        f"regional_coordinator1@{DEFAULT_HOST}",
        AGENT_PASSWORD,
        0,
        10,
        0,
        10,
        parking_agents_jids=[str(parking1.jid)],
    )
    await coordinator1.start()

    # coordinates from 10,0 to 20,10
    coordinator2 = RegionalCoordinator(f"regional_coordinator2@{DEFAULT_HOST}", AGENT_PASSWORD, 10, 20, 0, 10)
    await coordinator2.start()

    logger.info("All parkings and coordinators started")

    coordinators_jids = ["regional_coordinator1@server_hello", "regional_coordinator2@server_hello"]
    user1 = User(f"user1@{DEFAULT_HOST}", AGENT_PASSWORD, coordinators_jids=coordinators_jids)
    await user1.start()

    user2 = User(f"user2@{DEFAULT_HOST}", AGENT_PASSWORD, coordinators_jids=coordinators_jids)
    await user2.start()

    logger.info("All users started")

    time.sleep(5)
    logger.info("NO AVAILABLE PARKING SPOTS TEST CASE")

    await user1.request_parking_offers(5, 5, 8, 16)
    await asyncio.sleep(5)
    await user2.request_parking_offers(5, 5, 12, 16)

    while user1.active_reservations == {}:
        logger.info("Waiting for reservation")
        await asyncio.sleep(5)

    logger.info(f"Active reservations: {user1.active_reservations}")

    while True:
        try:
            await asyncio.sleep(10)
        except Exception as exception:
            logger.error(f"Exception: {exception}")
            break


if __name__ == "__main__":
    time.sleep(10)
    logger.info("Starting")
    spade.run(main())
