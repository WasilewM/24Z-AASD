import spade

from agents.coordinator_agent import RegionalCoordinator

DEFAULT_HOST = "server_hello"
AGENT_PASSWORD = "admin"


async def main():
    # coordinates from 0,0 to 10,10
    coordinator = RegionalCoordinator(f"regional_coordinator1@{DEFAULT_HOST}", AGENT_PASSWORD, 0, 10, 0, 10)
    await coordinator.start()
    print("Regional Coordinator started")

    # coordinates from 10,0 to 20,10
    coordinator = RegionalCoordinator(f"regional_coordinator2@{DEFAULT_HOST}", AGENT_PASSWORD, 10, 20, 0, 10)
    await coordinator.start()
    print("Regional Coordinator started")

    # coordinates from 0,10 to 10,20
    coordinator = RegionalCoordinator(f"regional_coordinator3@{DEFAULT_HOST}", AGENT_PASSWORD, 0, 10, 10, 20)
    await coordinator.start()
    print("Regional Coordinator started")

    # coordinates from 10,10 to 20,20
    coordinator = RegionalCoordinator(f"regional_coordinator4@{DEFAULT_HOST}", AGENT_PASSWORD, 10, 20, 10, 20)
    await coordinator.start()
    print("Regional Coordinator started")


if __name__ == "__main__":
    spade.run(main())
