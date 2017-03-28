from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.skills.skill_intents import SkillIntents

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

        level2_intent = IntentBuilder("LevelIntent"). \
            require("level2").build()
        self.register_self_intent(level2_intent, self.handle_level2_intent)

        self.disable_intent("LevelIntent")


    def handle_enable2_intent(self, message):
        self.speak("say level 2 to proceed")
        self.enable_self_intent("LevelIntent")

    def handle_level2_intent(self, message):
        self.speak("this is level 2 intent executing")
        self.disable_intent("LevelIntent")

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
            self.speak("level 2 executed from intent parser inside skill")

        return handled

    def stop(self):
        pass

def create_skill():
    return OwnIntentsSkill()
