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
import time
import os
from mycroft.skills.skill_intents import SkillIntents

__author__ = 'jarbas'

logger = getLogger(__name__)


class DictationSkill(MycroftSkill):

    def __init__(self):
        super(DictationSkill, self).__init__(name="DictationSkill")
        self.dictating = False
        self.words = ""
        self.path = self.config_core["database_path"] + "/dictations"
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.reload_skill = False

        self.name = ""

    def initialize(self):

        # register self intents
        self.intents = SkillIntents(self.emitter)

        stop_dict_intent = IntentBuilder("StopDictationIntent") \
            .require("StopDictationKeyword").build()

        self.register_self_intent(stop_dict_intent,
                                  self.handle_stop_dict_intent)
        # disable until needed
        self.disable_intent("StopDictationIntent")

        # registe global intents
        start_dict_intent = IntentBuilder("StartDictationIntent")\
            .require("StartDictationKeyword").build()

        self.register_intent(start_dict_intent,
                             self.handle_start_dict_intent)

        read_dict_intent = IntentBuilder("ReadDictationIntent") \
            .require("ReadDictationKeyword").build()

        self.register_intent(read_dict_intent,
                             self.handle_read_last_dictation_intent)

    def handle_start_dict_intent(self, message):
        self.dictating = True
        self.speak("Dictation Mode Started")
        self.words = ""
        # enable stop
        self.enable_self_intent("StopDictationIntent")
        self.disable_intent("StartDictationIntent")

    def handle_stop_dict_intent(self, message):
        self.speak("saving")
        self.save()
        self.dictating = False
        self.speak("Dictation Mode Stopped")
        self.disable_intent("StopDictationIntent")
        self.enable_intent("StartDictationIntent")

    def handle_read_last_dictation_intent(self, message):
        self.speak_dialog("dictation")
        self.speak(self.words)

    def handle_set_name(self, message):
        self.name = message.data["name"]
        self.speak("Name set to " + self.name)

    def save(self):
        # save
        if self.name == "":
            self.name = time.asctime()
        path = self.path + "/" + self.name + ".txt"
        wfile = open(path, "w")
        wfile.write(self.words)
        wfile.close()
        self.name = ""

    def stop(self):
        self.handle_stop_dict_intent("dummy")

    def converse(self, transcript, lang="en-us"):
        determined, intent = self.intents.determine_intent(transcript)
        handled = False
        # stop requested
        if determined:
            handled = self.intents.execute_intent()
        # if not stopped
        if not handled:
            # handle dictation
            if self.dictating:
                self.words += (transcript[0]) + "\n"
                # keep listening without wakeword
                self.speak("", expect_response=True)
                return True
        return handled


def create_skill():
    return DictationSkill()