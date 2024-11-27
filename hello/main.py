import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
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
    receiveragent = HelperAgent(f"receiver@{DEFAULT_HOST}", "receiver_password")
    await receiveragent.start(auto_register=True)
    print("Receiver started")

    senderagent = NotifierAgent(f"sender@{DEFAULT_HOST}", "sender_password")
    await senderagent.start(auto_register=True)
    print("Sender started")

    await spade.wait_until_finished(receiveragent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())