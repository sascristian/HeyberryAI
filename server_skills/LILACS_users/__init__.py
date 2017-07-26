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
import random
sys.path.append(dirname(dirname(__file__)))
from LILACS_core.concept import ConceptConnector
from mycroft.util.parse import normalize
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

    def is_person(self, data, key):
        # TODO think of a way to see if data is a name?
        ## use key, check for cousin /father etc. keywords
        family = ["parent", "child", "cousin", "mom", "dad",
                  "mother", "sibling", "aunt", "uncle", "father", "friend",
                  "husband", "fiance", "wife", "daughter", "lover", "maker",
                  "builder", "creator"]
        for word in family:
            if word in key:
                return True
        return False

    def classify(self, text, key, data):
        # a date
        data = normalize(data)
        months = ["january",  "february",  "march", "april", "may",  "june",  "july", "august",
                   "september", "october", "november", "december",
                  "jan", "feb","mar","apr","jun","jul","aug", "sep", "oct",
                  "nov", "dec", " "]
        for month in months:
            data = data.replace(month, "")
        print data
        if data.isdigit():
            return "date"
        # a person
        if self.is_person(data, key):

            return "person"
        # a thing
        return "description"

    def handle_set_user_data(self, message):
        # TODO check synonims?
        utterance = message.data.get("utterance", "")
        user = message.context.get("user")
        if not user:
            self.log.error("unknown user")
            self.speak("I dont know who you are")
            return
        key = message.data.get("New_Key")
        data_string = message.data.get("Data_String")
        bads = ["/", "(", ")", ".", "_", "-", "?", "!", ",", ";", "[",
                "]"]
        for w in bads:
            key = key.replace(w, "")
            data_string = data_string.replace(w, "")

        # categorize # TODO change this lazy mechanism
        qtype = self.classify(utterance, key, data_string)
        # load user concept
        if not self.connector.load_concept(user):
            self.connector.create_concept(new_concept_name=user, type="user")
        # update user concept
        data_dict = self.connector.get_data(user).get(key, {})
        if qtype not in data_dict:
            data_dict[qtype] = {}

        if data_string not in data_dict[qtype]:
            data_dict[qtype][data_string] = 5

        self.connector.add_data(user, key, data_dict)
        self.connector.add_cousin(user, key)
        # save
        self.connector.save_concept(user, "user")
        self.speak("Your " + key + " is " + data_string)
        self.connector.reset_connector()

    def handle_get_user_data(self, message):
        user = message.context.get("user")
        if not user:
            self.log.error("unknown user")
            self.speak("I dont know who you are")
            return
        bads = ["/", "(",")",".","_","-", "?", "!",",",";"]
        key = message.data.get("Key")
        for w in bads:
            key = key.replace(w, "")
        # load user concept
        if self.connector.load_concept(user):
            # get user data
            data_dict = self.connector.get_data(user).get(key, {})
            data_list = {"unknown" : 5}
            # check all relation types what/who/when
            for qtype in data_dict.keys():
                # get data for that relation
                ndata_list = data_dict.get(qtype, {})
                if len(ndata_list) > 0:
                    # if data found use it
                    data_list = ndata_list
                    break
            self.speak("Your " + key + " is " + random.choice(data_list.keys()))
        else:
            self.connector.create_concept(new_concept_name=user, type="user")
            self.connector.save_concept(user, "user")
            self.speak("I don't know what your " + key + " is")
        self.connector.reset_connector()

    def stop(self):
        pass


def create_skill():
    return LILACSUserSkill()
