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
from mycroft.skills.intent_parser import IntentParser

__author__ = 'jarbas'

logger = getLogger(__name__)


class ParrotSkill(MycroftSkill):

    def __init__(self):
        super(ParrotSkill, self).__init__(name="ParrotSkill")
        self.parroting = False
        self.reload_skill = False

    def initialize(self):
        self.intent_parser = IntentParser(self.emitter)

        stop_parrot_intent = IntentBuilder("StopParrotIntent") \
            .require("StopParrotKeyword").build()

        self.register_intent(stop_parrot_intent,
                                  self.handle_stop_parrot_intent)

        self.intent_parser.register_intent(stop_parrot_intent.__dict__)

        start_parrot_intent = IntentBuilder("StartParrotIntent")\
            .require("StartParrotKeyword").build()

        self.register_intent(start_parrot_intent,
                             self.handle_start_parrot_intent)

    def handle_start_parrot_intent(self, message):
        self.parroting = True
        self.speak("Parrot Mode Started")

    def handle_stop_parrot_intent(self, message):
        self.parroting = False
        self.speak("Parrot Mode Stopped")

    def stop(self):
        self.handle_stop_parrot_intent("dummy")

    def converse(self, transcript, lang="en-us"):
        determined, intent = self.intent_parser.determine_intent(transcript)
        # stop requested
        if determined:
            # stop intent will be handled in intent skill
            return False
        # if not stopped
        if self.parroting:
            # keep listening without wakeword
            self.speak(transcript[0], expect_response=True)
            return True
        return False



def create_skill():
    return ParrotSkill()