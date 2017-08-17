from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from os.path import dirname, exists
import sys
sys.path.append(dirname(__file__))

from mycroft.skills.intent_service import IntentParser, IntentLayers
from mycroft.messagebus.message import Message

__author__ = 'jarbas'

logger = getLogger(__name__)


class KonamiCodeSkill(MycroftSkill):
    def __init__(self):
        super(KonamiCodeSkill, self).__init__(name="KonamiCode")
        # read from config file
        self.cheat_code_script = dirname(__file__)+"/cheat_code.py"
        self.reload_skill = False
        self.active = False
        self.counter = 0
        self.top_fails = 3

    def initialize(self):
        self.emitter.on("recognizer_loop:hotword", self.handle_hot_word)

    def handle_hot_word(self, message):
        # process hotword sequence
        hotword = message.data.get("hotword")
        if hotword == "up":
            self.emitter.emit(Message(str(self.skill_id)+":KonamiUpIntent"))
        elif not self.active:
            return
        elif hotword == "down":
            self.emitter.emit(Message(str(self.skill_id) + ":KonamiDownIntent"))
        elif hotword == "left":
            self.emitter.emit(Message(str(self.skill_id) + ":KonamiLeftIntent"))
        elif hotword == "right":
            self.emitter.emit(Message(str(self.skill_id) + ":KonamiRightIntent"))
        elif hotword == "b":
            self.emitter.emit(Message(str(self.skill_id) + ":KonamiBIntent"))
        elif hotword == "a":
            self.emitter.emit(Message(str(self.skill_id) + ":KonamiAIntent"))

    def build_intents(self):
        # keywords dont really exist, intent is triggered manually
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
        self.active = True
        self.layers.next()

    def handle_down_intent(self, message):
        self.layers.next()

    def handle_left_intent(self, message):
        self.layers.next()

    def handle_right_intent(self, message):
        self.layers.next()

    def handle_b_intent(self, message):
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
            # execute cheat code
            from cheat_code import CheatCode
            cheat = CheatCode(self.emitter)
            cheat.execute_cheat_code()
        self.layers.reset()

    def stop(self):
        if self.active:
            self.layers.reset()
            self.active = False
            self.counter = 0

    def converse(self, utterances, lang="en-us"):
        if self.active:
            self.counter += 1
            if self.counter > self.top_fails:
                # if user spoke reset cheat code ?
                self.log.WARNING("Wrong cheat code entry, reseting layers")
                self.layers.reset()
                self.active = False
                self.counter = 0
        return False


def create_skill():
    return KonamiCodeSkill()
