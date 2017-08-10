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
from mycroft.messagebus.message import Message
__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class LILACSPersonalSkill(MycroftSkill):
    def __init__(self):
        super(LILACSPersonalSkill, self).__init__(name="LILACSPersonalSkill")
        self.reload_skill = False

    def initialize(self):
        # TODO who made you
        self.connector = ConceptConnector(emitter=self.emitter)

        self.create_user()

        # what is your "X" intent
        get_intent = IntentBuilder("GetSelfPreferenceIntent").require(
            "Self_Key").build()
        self.register_intent(get_intent, self.handle_get_self_data)

        # your "X" is "Y" intent
        set_intent = IntentBuilder("SetSelfPreferenceIntent").require(
            "Self_New_Key").require("Self_Data_String").build()
        self.register_intent(set_intent, self.handle_set_self_data)

        # you are "Y" intent
        set_info_intent = IntentBuilder("SetSelfInfoIntent").require(
            "Self_Description").build()
        self.register_intent(set_info_intent, self.handle_set_self_info)

    def create_user(self):
        # load self concept
        if not self.connector.load_concept("self"):
            self.connector.create_concept(new_concept_name="self", type="user")
            name = self.config_core.get("listener", {}).get("wake_word",
                                                            "jarbas").replace("hey ", "")
            maker = ["The wonderful Mycroft A.I. community and team.", "Everyone in the Mycroft A.I. community and team."]
            description = ["an open source artificial intelligence.", "an intelligent piece of software for communicating with machines"]
            birthday = "2015"
            born = "2015"
            birth = "2015"
            father = "Mycroft"
            data = {"Self_New_Key": "name", "Self_Data_String":name}
            message = Message("gra", data)
            self.handle_set_self_data(message)
            data = {"Self_New_Key": "maker", "Self_Data_String": maker[0]}
            message = Message("gra", data)
            self.handle_set_self_data(message)
            #data = {"Self_New_Key": "born", "Self_Data_String": born}
            #message = Message("gra", data)
            #self.handle_set_self_data(message)
            data = {"Self_New_Key": "birthday", "Self_Data_String": birthday}
            message = Message("gra", data)
            self.handle_set_self_data(message)
            #data = {"Self_New_Key": "birth", "Self_Data_String": birth}
            #message = Message("gra", data)
            #self.handle_set_self_data(message)
            data = {"Self_New_Key": "father", "Self_Data_String": father}
            message = Message("gra", data)
            self.handle_set_self_data(message)
            data = {"Self_Description": description[0]}
            message = Message("gra", data)
            self.handle_set_self_info(message)
            data = {"Self_Description": description[1]}
            message = Message("gra", data)
            self.handle_set_self_info(message)

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
        return "info"

    def handle_set_self_data(self, message):
        self.connector.load_concept("self")
        utterance = message.data.get("utterance", "")
        key = message.data.get("Self_New_Key")
        data_string = message.data.get("Self_Data_String")
        bads = ["/", "(", ")", ".", "_", "-", "?", "!", ",", ";", "[",
                "]"]
        for w in bads:
            key = key.replace(w, "")
            data_string = data_string.replace(w, "")

        # categorize # TODO change this lazy mechanism
        qtype = self.classify(utterance, key, data_string)
        # load user concept
        if "self" not in self.connector.get_concept_names("user"):
            self.connector.create_concept(new_concept_name="self", type="user")
        # update user concept
        data_dict = self.connector.get_data("self").get(key, {})
        if qtype not in data_dict:
            data_dict[qtype] = {}

        if data_string not in data_dict[qtype]:
            data_dict[qtype][data_string] = 5

        self.connector.add_data("self", key, data_dict)
        self.connector.add_cousin("self", key)
        # save
        self.connector.save_concept("self", "user")
        self.speak("My " + key + " is " + data_string)

    def handle_set_self_info(self, message):
        self.connector.load_concept("self")
        description = message.data.get("Self_Description")
        bads = ["/", "(", ")", ".", "_", "-", "?", "!", ",", ";", "[",
                "]"]
        for w in bads:
            description = description.replace(w, "")

        # load user concept
        if "self" not in self.connector.get_concept_names("user"):
            self.connector.create_concept(new_concept_name="self", type="user")

        # update user concept
        data_list = self.connector.get_data("self").get("description", [])

        if description not in data_list:
            data_list.append(description)

        self.connector.add_data("self", "description", data_list)
        # save
        self.connector.save_concept("self", "user")
        self.speak("I am " + description)

    def handle_get_self_data(self, message):
        self.connector.load_concept("self")
        bads = ["/", "(",")",".","_","-", "?", "!",",",";"]
        key = message.data.get("Self_Key")
        for w in bads:
            key = key.replace(w, "")
        # load user concept
        data_list = {}
        if "self" in self.connector.get_concept_names("user"):
            # get user data
            data_dict = self.connector.get_data("self").get(key, {})
            # check all relation types what/who/when
            for qtype in data_dict.keys():
                # get data for that relation
                ndata_list = data_dict.get(qtype, {})
                if len(ndata_list) > 0:
                    # if data found use it
                    data_list = ndata_list
                    break
        else:
            self.connector.create_concept(new_concept_name="self", type="user")
            self.connector.save_concept("self", "user")

        if len(data_list.keys()) == 0:
            self.speak("I haven't decided what my " + key + " is yet")
        else:
            this = random.choice(data_list.keys())
            self.speak("My " + key + " is " + this)

    def stop(self):
        pass


def create_skill():
    return LILACSPersonalSkill()
