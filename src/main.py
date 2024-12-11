import time

import spade

from agents.coordinator_agent import RegionalCoordinator
from agents.parking_agent import ParkingAgent
from agents.user_agent import User
from constants import DEFAULT_HOST
from logger import logger

AGENT_PASSWORD = "admin"


async def main():
    parking1 = ParkingAgent(f"parking100@{DEFAULT_HOST}", AGENT_PASSWORD, 1, 1, 100)
    await parking1.start()

    # coordinates from 0,0 to 10,10
    coordinator1 = RegionalCoordinator(f"regional_coordinator1@{DEFAULT_HOST}", AGENT_PASSWORD, 0, 10, 0, 10,
                                       parking_agents_jids=[str(parking1.jid)],
                                       )
    await coordinator1.start()

    # coordinates from 10,0 to 20,10
    coordinator2 = RegionalCoordinator(f"regional_coordinator2@{DEFAULT_HOST}", AGENT_PASSWORD, 10, 20, 0, 10)
    await coordinator2.start()

    # coordinates from 0,10 to 10,20
    coordinator3 = RegionalCoordinator(f"regional_coordinator3@{DEFAULT_HOST}", AGENT_PASSWORD, 0, 10, 10, 20)
    await coordinator3.start()

    # coordinates from 10,10 to 20,20
    coordinator4 = RegionalCoordinator(f"regional_coordinator4@{DEFAULT_HOST}", AGENT_PASSWORD, 10, 20, 10, 20)
    await coordinator4.start()

    logger.info("All parkings and coordinators started")

    user1 = User(f"user1@{DEFAULT_HOST}", AGENT_PASSWORD,
                 coordinators_jids=[str(coordinator1.jid), str(coordinator2.jid), str(coordinator3.jid), str(coordinator4.jid)])
    await user1.start()

    user2 = User(f"user2@{DEFAULT_HOST}", AGENT_PASSWORD,
                 coordinators_jids=[str(coordinator1.jid), str(coordinator2.jid), str(coordinator3.jid), str(coordinator4.jid)])
    await user2.start()

    # simple case
    time.sleep(5)
    logger.info("SIMPLE CASE STARTED")
    user1.submit(user1.request_parking_offers(5, 5, 8, 16))


if __name__ == "__main__":
    time.sleep(20)  # wait for the server to start
    logger.info("Starting")
    spade.run(main())
