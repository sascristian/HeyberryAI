from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'paul'

LOGGER = getLogger(__name__)

class FlipCoinSkill(MycroftSkill):

    def __init__(self):
        super(FlipCoinSkill, self).__init__(name="FlipCoinSkill")

    def initialize(self):
        self.load_data_files(dirname(__file__))

        flip_a_coin_intent = IntentBuilder("FlipACoinIntent").\
            require("FlipACoinKeyword").build()
        self.register_intent(flip_a_coin_intent, self.handle_flip_a_coin_intent)

        flip_two_coins_intent = IntentBuilder("FlipTwoCoinsIntent").\
            require("FlipTwoCoinsKeyword").build()
        self.register_intent(flip_two_coins_intent, self.handle_flip_two_coins_intent)

    def handle_flip_a_coin_intent(self, message):
        self.speak_dialog("flip.a.coin")

    def handle_flip_two_coins_intent(self, message):
        self.speak_dialog("flip.two.coins")

    def stop(self):
        pass


def create_skill():
    return FlipCoinSkill()
