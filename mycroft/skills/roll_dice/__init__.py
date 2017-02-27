from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'paul'

LOGGER = getLogger(__name__)

class RollDiceSkill(MycroftSkill):

    def __init__(self):
        super(RollDiceSkill, self).__init__(name="RollDiceSkill")

    def initialize(self):
       # self.load_data_files(dirname(__file__))

        roll_a_die_intent = IntentBuilder("RollADieIntent").\
            require("RollADieKeyword").build()
        self.register_intent(roll_a_die_intent, self.handle_roll_a_die_intent)

        roll_two_dice_intent = IntentBuilder("RollTwoDiceIntent").\
            require("RollTwoDiceKeyword").build()
        self.register_intent(roll_two_dice_intent, self.handle_roll_two_dice_intent)

    def handle_roll_a_die_intent(self, message):
        self.speak_dialog("roll.a.die")
        self.emit_results()

    def handle_roll_two_dice_intent(self, message):
        self.speak_dialog("roll.two.dice")
        self.emit_results()

    def stop(self):
        pass


def create_skill():
    return RollDiceSkill()
