import spade

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.user_agent import User
import time
from constants import DEFAULT_HOST
from logger import logger   
import asyncio 

AGENT_PASSWORD = "admin"

async def main():
    coordinators_jids = ["regional_coordinator1@server_hello", "regional_coordinator2@server_hello"]
    user1 = User(f"user1@{DEFAULT_HOST}", AGENT_PASSWORD,
                    coordinators_jids=coordinators_jids)
    
    await user1.start()
    logger.info("User 1 started")
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

    # while True:
    #     action = input("Enter 'r' to request parking, 's' to monitor status, 'q' to quit, and 'w' to wait: ")
    #     if action == 'q':
    #         break
    #     elif action == 'r':
    #         x = int(input("Enter X coordinate: "))
    #         y = int(input("Enter Y coordinate: "))
    #         start_time = int(input("Enter start time: "))
    #         end_time = int(input("Enter end time: "))
    #         await user1.request_parking_offers(x, y, start_time, end_time)
    #     elif action == 's':
    #         logger.info(f"Active reservations: {user1.active_reservations}")
    #         reservation_id = int(input("Enter reservation id for modification: "))
    #         #TODO Add error handling when reservation id is not present
    #         start_time = int(input("Enter new start time: "))
    #         end_time = int(input("Enter new end time: "))
    #         await user1.request_reservation_modification(reservation_id, start_time, end_time)
    #     elif action == 'w':
    #         await asyncio.sleep(10)

if __name__ == "__main__":
    logger.info("Starting")
    spade.run(main())
