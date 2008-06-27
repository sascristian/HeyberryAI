from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.skills.displayservice import DisplayService

from os.path import dirname

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class DisplayTestSkill(MycroftSkill):

    def __init__(self):
        super(DisplayTestSkill, self).__init__(name="DisplayTestSkill")

    def initialize(self):
        test_display_intent = IntentBuilder("displayTestIntent").\
                require("stKeyword").build()

        self.register_intent(test_display_intent, self.handle_display_test_intent)

        self.display_service = DisplayService(self.emitter)

    def handle_display_test_intent(self, message):
        save_path = dirname(__file__) + "/test_pic.jpg"
        self.speak_dialog("display_test")
        self.display_service.show([save_path])

    def stop(self):
        pass


def create_skill():
    return DisplayTestSkill()
