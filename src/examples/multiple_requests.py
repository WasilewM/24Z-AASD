import time
import spade
import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.coordinator_agent import RegionalCoordinator
from agents.parking_agent import ParkingAgent
from agents.user_agent import User
from constants import DEFAULT_HOST
from logger import logger

AGENT_PASSWORD = "admin"


async def main():
    parking1 = ParkingAgent(f"parking100@{DEFAULT_HOST}", AGENT_PASSWORD, 1, 1, 10)
    await parking1.start()
    parking2 = ParkingAgent(f"parking200@{DEFAULT_HOST}", AGENT_PASSWORD, 5, 1, 5, 5)
    await parking2.start()

    # coordinates from 0,0 to 10,10
    coordinator1 = RegionalCoordinator(
        f"regional_coordinator1@{DEFAULT_HOST}",
        AGENT_PASSWORD,
        0,
        10,
        0,
        10,
        parking_agents_jids=[str(parking1.jid), str(parking2.jid)],
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

    user3 = User(f"user3@{DEFAULT_HOST}", AGENT_PASSWORD, coordinators_jids=coordinators_jids)
    await user3.start()

    user4 = User(f"user4@{DEFAULT_HOST}", AGENT_PASSWORD, coordinators_jids=coordinators_jids)
    await user4.start()

    logger.info("All users started")

    time.sleep(5)
    logger.info("MULTIPLE REQUESTS TEST CASE")

    logger.info("\n\nExpected 2 requests acceptance")
    await user1.request_parking_offers(5, 5, 8, 16)
    await user2.request_parking_offers(5, 5, 16, 17)
    
    while not user1.active_reservations and not user2.active_reservations:    # wait for the first round of requests to complete
        logger.info("Waiting for reservation")
        await asyncio.sleep(5)

    logger.info(f"Active reservations: {user1.active_reservations}")
    logger.info(f"Active reservations: {user2.active_reservations}")

    logger.info("\n\nExpected 2 requests acceptance")
    await user3.request_parking_offers(5, 5, 9, 15)
    await user4.request_parking_offers(5, 5, 13, 14)

    while not user3.active_reservations and not user4.active_reservations:    # wait for the first round of requests to complete
        logger.info("Waiting for reservation")
        await asyncio.sleep(5)

    logger.info(f"Active reservations: {user3.active_reservations}")
    logger.info(f"Active reservations: {user4.active_reservations}")

    logger.info("\n\nExpected 2 denials - no parking in chosen location")
    await user3.request_parking_offers(15, 5, 17, 19)
    await user4.request_parking_offers(11, 5, 16, 17)

    while not user3.active_reservations and not user4.active_reservations:    # wait for the first round of requests to complete
        logger.info("Waiting for reservation")
        await asyncio.sleep(5)

    logger.info(f"Active reservations: {user3.active_reservations}")
    logger.info(f"Active reservations: {user4.active_reservations}")

    logger.info("TEST HAS FINISHED")
    
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
