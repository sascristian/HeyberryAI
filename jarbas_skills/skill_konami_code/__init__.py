from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from os.path import dirname, exists
import sys
sys.path.append(dirname(__file__))

from mycroft.skills.intent_service import IntentParser, IntentLayers

__author__ = 'jarbas'

logger = getLogger(__name__)


class KonamiCodeSkill(MycroftSkill):
    def __init__(self):
        super(KonamiCodeSkill, self).__init__(name="KonamiCode")
        # TODO use this path instead of importing default script and read from config file
        self.cheat_code_script = dirname(__file__)+"/cheat_code.py"
        self.reload_skill = False

    def initialize(self):
        self.intent_parser = IntentParser(self.emitter)
        self.build_intents()
        self.build_intent_layers()

    def build_intents(self):

        up_intent = IntentBuilder('KonamiUpIntent'). \
            require("KonamiUpKeyword").build()
        # register intent

        down_intent = IntentBuilder('KonamiDownIntent'). \
            require("KonamiDownKeyword").build()

        left_intent = IntentBuilder('KonamiLeftIntent'). \
            require("KonamiLeftKeyword").build()

        right_intent = IntentBuilder('KonamiRightIntent'). \
            require("KonamiRightKeyword").build()

        b_intent = IntentBuilder('KonamiBIntent'). \
            require("KonamiBKeyword").build()

        a_intent = IntentBuilder('KonamiAIntent'). \
            require("KonamiAKeyword").build()

        self.register_intent(up_intent, self.handle_up_intent)
        self.register_intent(down_intent, self.handle_down_intent)
        self.register_intent(left_intent, self.handle_left_intent)
        self.register_intent(right_intent, self.handle_right_intent)
        self.register_intent(b_intent, self.handle_b_intent)
        self.register_intent(a_intent, self.handle_a_intent)

    def build_intent_layers(self):
        layers = [["KonamiUpIntent"], ["KonamiUpIntent"], ["KonamiDownIntent"], ["KonamiDownIntent"],
                    ["KonamiLeftIntent"], ["KonamiRightIntent"], ["KonamiLeftIntent"], ["KonamiRightIntent"],
                    ["KonamiBIntent"], ["KonamiAIntent"]]
        self.layers = IntentLayers(self.emitter, layers, 60)

    def handle_up_intent(self, message):
        self.layers.next()
        self.speak_dialog("up", expect_response=True)

    def handle_down_intent(self, message):
        self.layers.next()
        self.speak_dialog("down", expect_response=True)

    def handle_left_intent(self, message):
        self.layers.next()
        self.speak_dialog("left", expect_response=True)

    def handle_right_intent(self, message):
        self.layers.next()
        self.speak_dialog("right", expect_response=True)

    def handle_b_intent(self, message):
        self.layers.next()
        self.speak_dialog("b", expect_response=True)

    def handle_a_intent(self, message):
        # check for script
        if not self.cheat_code_script:
            self.speak_dialog("no.script")
        elif not exists(self.cheat_code_script):
            data = {
                "script": self.cheat_code_script
            }
            self.speak_dialog("missing.script", data)
        else:
            self.speak_dialog("cheat_code")
            # execute cheat code
            from cheat_code import CheatCode
            cheat = CheatCode(self.emitter)
            cheat.execute_cheat_code()
        self.layers.reset()

    def stop(self):
        self.layers.reset()

    def converse(self, utterances, lang="en-us"):
        # check if some of the intents will be handled
        intent, id = self.intent_parser.determine_intent(utterances[0])
        if id != self.skill_id:
            # no longer inside this conversation
            # wrong cheat code entry
            self.log.info("Wrong cheat code entry, reseting layers")
            self.layers.reset()
        return False


def create_skill():
    return KonamiCodeSkill()
