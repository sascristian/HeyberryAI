from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.skills.displayservice import DisplayService

from mycroft.intent_tree.skill_intents import SkillIntents

import time

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class OwnIntentsSkill(MycroftSkill):

    def __init__(self):
        super(OwnIntentsSkill, self).__init__(name="OwnIntentsSkill")

    def initialize(self):
        self.intents = SkillIntents(self.emitter)

        enable2_intent = IntentBuilder("EnableLevel2Intent").\
                require("enable2Keyword").build()

        self.register_intent(enable2_intent, self.handle_enable2_intent)

        self.display_service = DisplayService(self.emitter)

    def handle_enable2_intent(self, message):
        self.speak("say level 2 to proceed")

        level2_intent = IntentBuilder("LevelIntent"). \
            require("level2").build()
        self.register_self_intent(level2_intent, self.handle_level2_intent)

    def handle_level2_intent(self, message):
        self.speak("this is level 2 intent executing")

    def converse(self, transcript, lang="en-us"):
        det, intent = self.intents.determine_intent(transcript)
        handled = False
        if det:
            try:
                intent_name = intent.get('intent_type')
                self.speak("trying to handle intent " + intent_name)
                handled = self.intents.execute_intent()
            except:
                pass
        if handled:
            # de-register
            time.sleep(5)
            self.disable_intent(intent_name)
            self.speak("disabling level 2 and going back to level 1")

        return handled

    def stop(self):
        pass

def create_skill():
    return AdaptSkill()
