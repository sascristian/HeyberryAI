from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'paul'

LOGGER = getLogger(__name__)

class RockPaperScissorsSkill(MycroftSkill):

    def __init__(self):
        super(RockPaperScissorsSkill, self).__init__(name="RockPaperScissorsSkill")

    def initialize(self):
      #  self.load_data_files(dirname(__file__))

        rock_paper_scissors_intent = IntentBuilder("RockPaperScissorsIntent").\
            require("RockPaperScissorsKeyword").build()
        self.register_intent(rock_paper_scissors_intent, self.handle_rock_paper_scissors_intent) 

    def handle_rock_paper_scissors_intent(self, message):
        self.speak_dialog("rock.paper.scissors")
        self.emit_results()

    def stop(self):
        pass


def create_skill():
    return RockPaperScissorsSkill()
