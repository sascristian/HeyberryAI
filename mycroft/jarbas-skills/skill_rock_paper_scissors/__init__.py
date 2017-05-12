import random

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'paul'

LOGGER = getLogger(__name__)

class RockPaperScissorsSkill(MycroftSkill):

    def __init__(self):
        super(RockPaperScissorsSkill, self).__init__(name="RockPaperScissorsSkill")
        self.possibilities = ["rock", "paper", "scissors"]

    def initialize(self):

        rock_paper_scissors_intent = IntentBuilder("RockPaperScissorsIntent").\
            require("RockPaperScissorsKeyword").build()
        self.register_intent(rock_paper_scissors_intent, self.handle_rock_paper_scissors_intent) 

    def handle_rock_paper_scissors_intent(self, message):
        choice = random.choice(self.possibilities)
        self.speak_dialog("rock.paper.scissors", {"choice": choice})

    def stop(self):
        pass


def create_skill():
    return RockPaperScissorsSkill()
