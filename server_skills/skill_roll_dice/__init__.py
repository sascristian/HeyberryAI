import random

from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'paul'

LOGGER = getLogger(__name__)


class RollDiceSkill(MycroftSkill):
    def __init__(self):
        super(RollDiceSkill, self).__init__(name="RollDiceSkill")
        self.possibilities = ["1", "2", "3", "4", "5", "6"]

    def initialize(self):
        roll_a_dice_intent = IntentBuilder("RollADiceIntent"). \
            require("RollADiceKeyword").build()
        self.register_intent(roll_a_dice_intent, self.handle_roll_a_dice_intent)

        roll_two_dice_intent = IntentBuilder("RollTwoDiceIntent"). \
            require("RollTwoDiceKeyword").build()
        self.register_intent(roll_two_dice_intent, self.handle_roll_two_dice_intent)

    def handle_roll_a_dice_intent(self, message):
        roll = random.choice(self.possibilities)
        self.speak_dialog("roll.a.dice", {"roll": roll})

    def handle_roll_two_dice_intent(self, message):
        roll1 = random.choice(self.possibilities)
        roll2 = random.choice(self.possibilities)
        self.speak_dialog("roll.two.dice", {"roll1": roll1, "roll2": roll2})

    def stop(self):
        pass


def create_skill():
    return RollDiceSkill()
