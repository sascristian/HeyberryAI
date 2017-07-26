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

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from adapt.intent import IntentBuilder
from os.path import dirname
import sys
sys.path.append(dirname(dirname(__file__)))
from LILACS_core.concept import ConceptConnector

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class LILACSUserSkill(MycroftSkill):
    def __init__(self):
        super(LILACSUserSkill, self).__init__(name="LILACSUserSkill")
        self.reload_skill = False

    def initialize(self):
        self.connector = ConceptConnector(emitter=self.emitter)
        # what is my "X" intent
        get_intent = IntentBuilder("GetUserPreferenceIntent").require(
            "Key").build()
        self.register_intent(get_intent, self.handle_get_user_data)
        # my "X" is "Y" intent
        set_intent = IntentBuilder("SetUserPreferenceIntent").require(
            "New_Key").require("Data_String").build()
        self.register_intent(set_intent, self.handle_set_user_data)

    def handle_set_user_data(self, message):
        user = message.context.get("user")
        if not user:
            self.log.error("unknown user")
            self.speak("I dont know who you are")
            return
        key = message.data.get("New_Key")
        data_string = message.data.get("Data_String")
        # load user concept
        self.connector.load_concept(user)
        # update user concept
        self.connector.add_data(user, key, data_string)
        # save
        self.connector.save_concept(user, "user")
        self.speak("Your " + key + " is " + data_string)

    def handle_get_user_data(self, message):
        user = message.context.get("user")
        if not user:
            self.log.error("unknown user")
            self.speak("I dont know who you are")
            return
        key = message.data.get("Key")
        # load user concept
        if self.connector.load_concept(user):
            # get user data
            user_data = self.connector.get_data(user)
            data_string = user_data.get(key, "unknown")
            self.speak("Your " + key + " is " + data_string)
        else:
            self.speak("I don't know what your " + key + " is")

    def stop(self):
        pass


def create_skill():
    return LILACSUserSkill()
