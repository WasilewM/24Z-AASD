import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template


class User(Agent):
    class CheckUserBehaviour(CyclicBehaviour):
        async def run(self):
            # @TODO to be implemented
            pass
