import asyncio
import time
import spade

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.coordinator_agent import RegionalCoordinator
from agents.parking_agent import ParkingAgent
from constants import DEFAULT_HOST
from logger import logger

AGENT_PASSWORD = "admin"


async def main():
    parking1 = ParkingAgent(f"parking100@{DEFAULT_HOST}", AGENT_PASSWORD, 1, 1, 100)
    await parking1.start()

    # coordinates from 0,0 to 10,10
    coordinator1 = RegionalCoordinator(f"regional_coordinator1@{DEFAULT_HOST}", AGENT_PASSWORD, 0, 10, 0, 10,
                                       parking_agents_jids=[str(parking1.jid)])
    await coordinator1.start()
    logger.info(f"Coordinator1 jid: {str(coordinator1.jid)}")

    # coordinates from 10,0 to 20,10
    coordinator2 = RegionalCoordinator(f"regional_coordinator2@{DEFAULT_HOST}", AGENT_PASSWORD, 10, 20, 0, 10)
    await coordinator2.start()
    logger.info(f"Coordinator2 jid: {str(coordinator2.jid)}")

    logger.info("All parkings and coordinators started")

    while True:
        try:
            await asyncio.sleep(10)
        except Exception as exception:
            logger.error(f"Exception: {exception}")
            break


if __name__ == "__main__":
    time.sleep(20) 
    logger.info("Starting")
    spade.run(main())
