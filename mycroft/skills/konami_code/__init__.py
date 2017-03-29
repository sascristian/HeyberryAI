from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger


from os.path import dirname, exists
__author__ = 'jarbas'

logger = getLogger(__name__)

from mycroft.skills.intent_parser import IntentParser, IntentTree

class KonamiCodeSkill(MycroftSkill):
    def __init__(self):
        super(KonamiCodeSkill, self).__init__(name="KonamiCode")
        # TODO use this path instead of importing default script and read from config file
        self.cheat_code_script = dirname(__file__)+"/cheat_code.py"
        self.reload_skill = False

    def initialize(self):
        self.intent_parser = IntentParser(self.emitter)
        self.build_intents()
        self.build_intent_tree()

    def build_intents(self):

        # build intent
        up_intent = IntentBuilder('KonamiUpIntent'). \
            require("KonamiUpKeyword").build()
        # register intent
        self.register_intent(up_intent, self.handle_up_intent)
        # register in self-intent parser
        self.intent_parser.register_intent(up_intent.__dict__)


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

        self.register_intent(down_intent, self.handle_down_intent)
        self.register_intent(left_intent, self.handle_left_intent)
        self.register_intent(right_intent, self.handle_right_intent)
        self.register_intent(b_intent, self.handle_b_intent)
        self.register_intent(a_intent, self.handle_a_intent)

        self.intent_parser.register_intent(down_intent.__dict__)
        self.intent_parser.register_intent(left_intent.__dict__)
        self.intent_parser.register_intent(right_intent.__dict__)
        self.intent_parser.register_intent(b_intent.__dict__)
        self.intent_parser.register_intent(a_intent.__dict__)

    def build_intent_tree(self):
        layers = [["KonamiUpIntent"], ["KonamiUpIntent"], ["KonamiDownIntent"], ["KonamiDownIntent"],
                    ["KonamiLeftIntent"], ["KonamiRightIntent"], ["KonamiLeftIntent"], ["KonamiRightIntent"],
                    ["KonamiBIntent"], ["KonamiAIntent"]]
        self.tree = IntentTree(self.emitter, layers, 60)
        self.emitter.on('enable_intent', self.handle_enable_intent)

    def handle_up_intent(self, message):
        self.speak_dialog("up")
        self.tree.next()

    def handle_down_intent(self, message):
        self.speak_dialog("down")
        self.tree.next()

    def handle_left_intent(self, message):
        self.speak_dialog("left")
        self.tree.next()

    def handle_right_intent(self, message):
        self.speak_dialog("right")
        self.tree.next()

    def handle_b_intent(self, message):
        self.speak_dialog("b")
        self.tree.next()

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
            import mycroft.skills.konami_code.cheat_code
        self.tree.reset()

    def stop(self):
        self.tree.reset()

    def converse(self, transcript, lang="en-us"):
        # check if some of the intents will be handled
        determined, intent = self.intent_parser.determine_intent(transcript)
        if not determined:
            # wrong cheat code entry
            self.tree.reset()
        return False

def create_skill():
    return KonamiCodeSkill()
