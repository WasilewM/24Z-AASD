import spade

from agents.coordinator_agent import RegionalCoordinator
from agents.parking_agent import ParkingAgent
from agents.user_agent import User
from constants import DEFAULT_HOST

AGENT_PASSWORD = "admin"


async def main():
    parking = ParkingAgent(f"parking100@{DEFAULT_HOST}", AGENT_PASSWORD, 1, 1, 100)
    await parking.start()
    print("Parking started")

    # coordinates from 0,0 to 10,10
    coordinator = RegionalCoordinator(
        f"regional_coordinator1@{DEFAULT_HOST}",
        AGENT_PASSWORD,
        0,
        10,
        0,
        10,
        parking_agents_jids=[f"parking100@{DEFAULT_HOST}"],
    )
    await coordinator.start()
    print("Regional Coordinator started")

    # commented to simplify tests
    # # coordinates from 10,0 to 20,10
    # coordinator = RegionalCoordinator(f"regional_coordinator2@{DEFAULT_HOST}", AGENT_PASSWORD, 10, 20, 0, 10)
    # await coordinator.start()
    # print("Regional Coordinator started")

    # # coordinates from 0,10 to 10,20
    # coordinator = RegionalCoordinator(f"regional_coordinator3@{DEFAULT_HOST}", AGENT_PASSWORD, 0, 10, 10, 20)
    # await coordinator.start()
    # print("Regional Coordinator started")

    # # coordinates from 10,10 to 20,20
    # coordinator = RegionalCoordinator(f"regional_coordinator4@{DEFAULT_HOST}", AGENT_PASSWORD, 10, 20, 10, 20)
    # await coordinator.start()
    # print("Regional Coordinator started")

    user = User(f"user1@{DEFAULT_HOST}", AGENT_PASSWORD)
    await user.start()
    print("User1 started")

    user = User(f"user2@{DEFAULT_HOST}", AGENT_PASSWORD)
    await user.start()
    print("User2 started")


if __name__ == "__main__":
    spade.run(main())
