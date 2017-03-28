# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.skills.skill_intents import SkillIntents

__author__ = 'jarbas'

logger = getLogger(__name__)


class ParrotSkill(MycroftSkill):

    def __init__(self):
        super(ParrotSkill, self).__init__(name="ParrotSkill")
        self.parroting = False

    def initialize(self):
        # register self intents
        self.intents = SkillIntents(self.emitter)

        stop_parrot_intent = IntentBuilder("StopParrotIntent") \
            .require("StopParrotKeyword").build()

        self.register_self_intent(stop_parrot_intent,
                                  self.handle_stop_parrot_intent)
        # disable until needed
        self.disable_intent("StopParrotIntent")

        # global intents
        start_parrot_intent = IntentBuilder("StartParrotIntent")\
            .require("StartParrotKeyword").build()

        self.register_intent(start_parrot_intent,
                             self.handle_start_parrot_intent)

    def handle_start_parrot_intent(self, message):
        self.parroting = True
        self.speak("Parrot Mode Started")
        self.enable_self_intent("StopParrotIntent")
        # disable until needed
        self.disable_intent("StartParrotIntent")

    def handle_stop_parrot_intent(self, message):
        self.parroting = False
        self.speak("Parrot Mode Stopped")
        self.disable_intent("StopParrotIntent")
        self.enable_intent("StartParrotIntent")

    def stop(self):
        self.handle_stop_parrot_intent("dummy")

    def converse(self, transcript, lang="en-us"):
        determined, intent = self.intents.determine_intent(transcript)
        handled = False
        # stop requested
        if determined:
            handled = self.intents.execute_intent()
        # if not stopped
        if not handled:
            # in here handle the utterance if it doesnt trigger a self intent
            # handle parrot
            if self.parroting:
                # keep listening without wakeword
                self.speak(transcript[0], expect_response=True)
                return True
        return handled



def create_skill():
    return ParrotSkill()