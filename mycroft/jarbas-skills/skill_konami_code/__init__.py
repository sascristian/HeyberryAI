from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger


from os.path import dirname, exists
from mycroft.skills.intent_service import IntentParser

__author__ = 'jarbas'

logger = getLogger(__name__)

import subprocess


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
        self.speak_dialog("up")
        self.layers.next()

    def handle_down_intent(self, message):
        self.speak_dialog("down")
        self.layers.next()

    def handle_left_intent(self, message):
        self.speak_dialog("left")
        self.layers.next()

    def handle_right_intent(self, message):
        self.speak_dialog("right")
        self.layers.next()

    def handle_b_intent(self, message):
        self.speak_dialog("b")
        self.layers.next()

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
            # execute user script
            # TODO change this lazy mechanism, use subprocess ?
            #import mycroft.skills.konami_code.cheat_code
            subprocess.Popen(self.cheat_code_script, shell=True)
        self.layers.reset()

    def stop(self):
        self.layers.reset()

    def converse(self, transcript, lang="en-us"):
        # check if some of the intents will be handled
        intent, id = self.intent_parser.determine_intent(transcript[0])
        if id != self.skill_id:
            # no longer inside this conversation
            # wrong cheat code entry
            self.layers.reset()
        return False


def create_skill():
    return KonamiCodeSkill()
