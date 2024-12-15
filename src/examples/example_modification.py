import time

import spade
import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.user_agent import User
from constants import DEFAULT_HOST
from logger import logger

AGENT_PASSWORD = "admin"


async def main():

    coordinators_jids = ["regional_coordinator1@server_hello", "regional_coordinator2@server_hello"]
    user1 = User(f"user1@{DEFAULT_HOST}", AGENT_PASSWORD,
                 coordinators_jids=coordinators_jids)
    await user1.start()

    logger.info("User 1 started")

    time.sleep(5)
    logger.info("MODIFICATION TEST CASE")

    await user1.request_parking_offers(5, 5, 8, 16)

    while not user1.active_reservations:
        logger.info("Waiting for reservation")
        await asyncio.sleep(5)

    logger.info(f"Active reservations: {user1.active_reservations}")
    reservation_id = list(user1.active_reservations.keys())[0]

    await user1.request_reservation_modification(reservation_id, 18, 20)

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
