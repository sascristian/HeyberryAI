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
from mycroft.messagebus.message import Message

__author__ = 'jarbas'

logger = getLogger(__name__)

### imports for this LILACS fallback

from wordnik import *
from mycroft.skills.LILACS_fallback import LILACSFallback


class LILACSWordnikSkill(LILACSFallback):
    def __init__(self):
        super(LILACSWordnikSkill, self).__init__(
            name="wordnik")
        apiUrl = 'http://api.wordnik.com/v4'
        apiKey = self.config_core.get(
            "APIS").get("Wordnik")
        if not apiKey:
            apiKey = self.config.get("Wordnik")
        client = swagger.ApiClient(apiKey, apiUrl)
        self.wordApi = WordApi.WordApi(client)
        self.limit = 5

    def start_up(self):
        ''' Use instead of initialize method '''
        pass

    def handle_fallback(self, message):
        ''' this is activated by LILACS core, should answer the question
        asked, LILACS parsed data is available in message data '''
        return False

    def handle_test_intent(self, message):
        ''' test this fallback intent  '''
        ### get subject for test and update context###
        node = message.data.get("TargetKeyword",
                                message.data.get("LastConcept", "god"))
        self.set_context("LastConcept", node)

        ### adquire result with internal method for testing ###
        result = self._adquire(node).get(self.name, {}).get("node_dict")
        if not result:
            self.speak("Could not get info about " + node + " from " +
                       self.name)
            return
        ## update node in memory ##
        self.update_node(node,
                         node_data=result.get("data", {}),
                         node_connections=result.get("connections", {}))

        ### speak results back ###
        result = result.get("data", {})
        relations = result.get("relations", {})
        definitions = result.get("definitions", [])
        if len(definitions):
            self.speak("wordnik found " + str(
                len(definitions)) + " definitions for " + node)
            for definition in definitions:
                self.speak(definition)
        if len(relations.keys()):
            self.speak(
                "The following relationships to " + node + " are available")
            for key in relations:
                self.speak(key)
                self.speak(relations[key])

    def get_connections(self, subject):
        ''' implement getting a dict of parsed connections here '''
        node_cons = {"antonims": {}}
        for antonim in wordnik["antonym"]:
            rels = self.get_related_words(subject)
            if "antonym" in rels:
                for ant in rels["antonym"]:
                    node_cons["antonims"][ant] = 5

        # TODO parse relations node_data["relations"] = self.get_related_words(subject)
        return node_cons

    def get_data(self, subject):
        ''' implement parsing of data here '''
        node_data = {}
        # get knowledge about
        try:
            node_data["relations"] = self.get_related_words(subject)
            node_data["definitions"] = self.get_definitions(subject)
        except:
            self.log.error("Failed to retrieve data from " + self.name)
        return node_data

    def get_definitions(self, subject):
        definitions = self.wordApi.getDefinitions(subject,
                                                  partOfSpeech='noun',
                                                  sourceDictionaries='all',
                                                  limit=self.limit)
        defs = []
        try:
            for defi in definitions:
                defs.append(defi.text)
        except:
            pass
        return defs

    def get_related_words(self, subject):
        res = self.wordApi.getRelatedWords(subject)
        words = {}
        try:
            for r in res:
                words.setdefault(r.relationshipType, r.words)
        except:
            pass
        return words


def create_skill():
    return LILACSWordnikSkill()
