import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template

DEFAULT_HOST = "server_hello"
AGENT_PASSWORD = "admin"


class NotifierAgent(Agent):
    class NotifyBehaviour(OneShotBehaviour):
        async def run(self):
            print("NotifyBehaviour running")
            msg = Message(to=f"helper@{DEFAULT_HOST}")
            msg.set_metadata("performative", "inform")
            msg.body = "NOTIFICATION!!!!!111!!1!1 You have sent your worki!1!1"

            await self.send(msg)
            print("Notification sent!")

            await self.agent.stop()

    async def setup(self):
        print("NotifierAgent started")
        b = self.NotifyBehaviour()
        self.add_behaviour(b)


class ParkingAgent(Agent):
    class CheckParkingBehaviour(CyclicBehaviour):
        async def run(self):
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


class HelperAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=10)
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not received any message after 10 seconds")

            await self.agent.stop()

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


async def main():
    receiver_agent = HelperAgent(f"receiver@{DEFAULT_HOST}", "receiver_password")
    await receiver_agent.start(auto_register=True)
    print("Receiver started")

    sender_agent = NotifierAgent(f"sender@{DEFAULT_HOST}", "sender_password")
    await sender_agent.start(auto_register=True)
    print("Sender started")

    parking_agent = NotifierAgent(f"sender@{DEFAULT_HOST}", "sender_password")
    await parking_agent.start(auto_register=True)
    print("Sender started")

    await spade.wait_until_finished(receiver_agent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())