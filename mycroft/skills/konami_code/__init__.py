from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from os.path import dirname, exists

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class KonamiCodeSkill(MycroftSkill):
    def __init__(self):
        super(KonamiCodeSkill, self).__init__(name="KonamiCode")
        # TODO use this path instead of importing default script and read from config file
        self.cheat_code_script = dirname(__file__)+"/cheat_code.py"

    def initialize(self):
        self.build_intents()
        self.build_intent_tree()
        self.tree_reset()

    def build_intents(self):
        # build intents
        up_intent = IntentBuilder('KonamiUpIntent'). \
            require("KonamiUpKeyword").build()

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

        # register intents
        self.register_intent(up_intent, self.handle_up_intent)
        self.register_intent(down_intent, self.handle_down_intent)
        self.register_intent(left_intent, self.handle_left_intent)
        self.register_intent(right_intent, self.handle_right_intent)
        self.register_intent(b_intent, self.handle_b_intent)
        self.register_intent(a_intent, self.handle_a_intent)

    def build_intent_tree(self):
        # make intent tree for N layers
        self.tree = []
        sequence = ["KonamiUpIntent", "KonamiUpIntent", "KonamiDownIntent", "KonamiDownIntent",
                    "KonamiLeftIntent", "KonamiRightIntent", "KonamiLeftIntent", "KonamiRightIntent",
                    "KonamiBIntent", "KonamiAIntent", ]
        for intent_name in sequence:
            self.add_layer([intent_name])

        self.current_layer = 0

    def tree_set_timer(self):
        # TODO set a timer to reset tree
        pass

    def tree_reset(self):
        self.log.info("Reseting Tree")
        self.activate_layer(0)

    def tree_next(self):
        self.log.info("Going to next Tree Layer")
        self.current_layer += 1
        if self.current_layer > len(self.tree):
            self.log.info("Already in last layer, going to layer 0")
            self.current_layer = 0
        self.activate_layer(self.current_layer)

    def tree_previous(self):
        self.log.info("Going to previous Tree Layer")
        self.current_layer -= 1
        if self.current_layer < 0:
            self.current_layer = len(self.tree)
            self.log.info("Already in layer 0, going to last layer")
        self.activate_layer(self.current_layer)

    def add_layer(self, intent_list=[]):
        self.tree.append(intent_list)
        self.log.info("Adding layer to tree " + str(intent_list))

    def activate_layer(self, layer_num):
        # error check
        if layer_num < 0 or layer_num > len(self.tree):
            self.log.error("invalid layer number")
            return
        # disable other layers
        self.log.info("Deactivating active layers")
        i = 0
        for layer in self.tree:
            self.deactivate_layer(i)
            i+= 1

        # enable layer
        self.log.info("Activating Layer " + str(layer_num))
        for intent_name in self.tree[layer_num]:
            self.enable_intent(intent_name)

    def deactivate_layer(self, layer_num):
        # error check
        if layer_num < 0 or layer_num > len(self.tree):
            self.log.error("invalid layer number")
            return
        self.log.info("Deactivating Layer " + str(layer_num))
        for intent_name in self.tree[layer_num]:
            self.disable_intent(intent_name)

    def handle_up_intent(self, message):
        self.speak_dialog("up")
        self.tree_next()

    def handle_down_intent(self, message):
        self.speak_dialog("down")
        self.tree_next()

    def handle_left_intent(self, message):
        self.speak_dialog("left")
        self.tree_next()

    def handle_right_intent(self, message):
        self.speak_dialog("right")
        self.tree_next()

    def handle_b_intent(self, message):
        self.speak_dialog("b")
        self.tree_next()

    def handle_a_intent(self, message):
        # check for script
        if not self.cheat_code_script:
            self.speak_dialog("no.script")
            self.tree_reset()
            return

        if not exists(self.cheat_code_script):
            data = {
                "script": self.cheat_code_script
            }
            self.speak_dialog("missing.script", data)
            self.tree_reset()
            return

        self.speak_dialog("cheat_code")
        # execute user script
        # TODO change this lazy mechanism, use subprocess ?
        import mycroft.skills.konami_code.cheat_code

        self.tree_reset()

    def stop(self):
        pass

    def converse(self, transcript, lang="en-us"):
        # reset sequence
        self.tree_reset()
        return False


def create_skill():
    return KonamiCodeSkill()
