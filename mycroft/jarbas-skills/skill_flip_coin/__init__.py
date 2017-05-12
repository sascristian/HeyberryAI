from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import random

__author__ = 'paul'

LOGGER = getLogger(__name__)

class FlipCoinSkill(MycroftSkill):

    def __init__(self):
        super(FlipCoinSkill, self).__init__(name="FlipCoinSkill")
        self.possibilities = ["heads", "tails"]

    def initialize(self):

        flip_a_coin_intent = IntentBuilder("FlipACoinIntent").\
            require("FlipACoinKeyword").build()
        self.register_intent(flip_a_coin_intent, self.handle_flip_a_coin_intent)

        flip_two_coins_intent = IntentBuilder("FlipTwoCoinsIntent").\
            require("FlipTwoCoinsKeyword").build()
        self.register_intent(flip_two_coins_intent, self.handle_flip_two_coins_intent)

    def handle_flip_a_coin_intent(self, message):
        coin_flip = random.choice(self.possibilities)
        self.speak_dialog("flip.a.coin", {"flip": coin_flip})

    def handle_flip_two_coins_intent(self, message):
        coin_flip1 = random.choice(self.possibilities)
        coin_flip2 = random.choice(self.possibilities)
        self.speak_dialog("flip.two.coins", {"flip1": coin_flip1, "flip2": coin_flip2})

    def stop(self):
        pass


def create_skill():
    return FlipCoinSkill()
