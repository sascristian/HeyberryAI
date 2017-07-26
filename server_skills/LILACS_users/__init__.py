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
        # TODO "self" node
        # TODO user_actions (set an alarm, set a reminder...., add item to
        # todo list)
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
        # TODO process question type and seperate inside node by question type?
        # cousin: name : who
        # cousin : bday : when
        # cousin : favorite animal : what
        # TODO check synonims?
        utterance = message.data.get("utterance", "")
        user = message.context.get("user")
        if not user:
            self.log.error("unknown user")
            self.speak("I dont know who you are")
            return
        key = message.data.get("New_Key")
        data_string = message.data.get("Data_String")
        # categorize # TODO change this lazy mechanism
        qtype = "what"
        if "who" in utterance:
            qtype = "who"
        if "when" in utterance:
            qtype = "when"
        # load user concept
        if not self.connector.load_concept(user):
            self.connector.create_concept(new_concept_name=user, type="user")
        # update user concept
        data_dict = self.connector.get_data(qtype)
        data_dict[key] = data_string
        self.connector.add_data(user, key, data_dict)
        self.connector.add_cousin(user, key)
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
            for qtype in user_data.keys():
                data_string = user_data[qtype].get(key)
                if data_string:
                    break
                else:
                    data_string = "unknown"
            self.speak("Your " + key + " is " + data_string)
        else:
            self.connector.create_concept(new_concept_name=user, type="user")
            self.speak("I don't know what your " + key + " is")

    def stop(self):
        pass


def create_skill():
    return LILACSUserSkill()
