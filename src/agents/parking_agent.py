import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template


class ParkingAgent(Agent):
    class CheckParkingBehaviour(CyclicBehaviour):
        async def run(self):
            # @TODO to be implemented
            print("Waiting for incoming messages...")
            msg = await self.receive(timeout=10)  # Wait for a message for 10 seconds
            if msg:
                print(f"Message received with content: {msg.body}")
                # Assuming msg.body is requesting the number of available parking spots
                available_spots = self.get_available_parking_spots()
                reply = Message(to=msg.sender)  # Create a reply message
                reply.body = f"Available parking spots: {available_spots}"
                await self.send(reply)
                print(f"Reply sent: {reply.body}")
            else:
                print("No message received within the timeout period")

        def get_available_parking_spots(self):
            # Here you would implement the logic to check the number of available parking spots
            # For now, we'll just return a dummy value
            return 42

    async def setup(self):
        print("Agent starting...")
        behaviour = self.CheckParkingBehaviour()
        self.add_behaviour(behaviour)
