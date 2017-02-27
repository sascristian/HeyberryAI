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

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)


class MoodSkill(MycroftSkill):

    def __init__(self):
        super(MoodSkill, self).__init__(name="MoodSkill")

    def initialize(self):
        #self.load_data_files(dirname(__file__))

        complain_intent = IntentBuilder("ComplainIntent")\
            .require("complain").build()
        self.register_intent(complain_intent,
                             self.handle_complain_intent)

        happy_intent = IntentBuilder("HappyIntent") \
            .require("good").build()
        self.register_intent(happy_intent,
                             self.handle_happy_intent)

        lonely_intent = IntentBuilder("LonelyIntent") \
            .require("lonely").build()
        self.register_intent(lonely_intent,
                             self.handle_lonely_intent)

        depressed_intent = IntentBuilder("DepressedIntent") \
            .require("Depressed").build()
        self.register_intent(depressed_intent,
                             self.handle_depressed_intent)

        suggest_intent = IntentBuilder("SuggestIntent") \
            .require("suggestion").build()
        self.register_intent(suggest_intent,
                             self.handle_suggest_intent)

    def handle_suggest_intent(self, message):
        self.speak_dialog("suggestion")
        self.emit_results()

    def handle_depressed_intent(self, message):
        self.speak_dialog("depressed")
        self.emit_results()

    def handle_lonely_intent(self, message):
        self.speak_dialog("lonely")
        self.emit_results()

    def handle_happy_intent(self, message):
        self.speak_dialog("good")
        self.emit_results()

    def handle_complain_intent(self, message):
        self.speak_dialog("complain")
        self.emit_results()

    def stop(self):
        pass


def create_skill():
    return MoodSkill()
