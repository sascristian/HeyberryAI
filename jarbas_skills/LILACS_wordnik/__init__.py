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

from wordnik import *

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACSWordnikSkill(MycroftSkill):
    def __init__(self):
        super(LILACSWordnikSkill, self).__init__(
            name="LILACS_Wordnik_Skill")
        apiUrl = 'http://api.wordnik.com/v4'
        apiKey = self.config_core.get(
            "APIS").get("Wordnik")
        if not apiKey:
            apiKey = self.config.get("Wordnik")
        client = swagger.ApiClient(apiKey, apiUrl)
        self.wordApi = WordApi.WordApi(client)
        self.limit = 5

    def initialize(self):
        self.emitter.on("wordnik.request", self.handle_ask_wordnik)
        test_intent = IntentBuilder("TestWordnikIntent") \
            .require("testn").require("TargetKeyword").build()
        self.register_intent(test_intent, self.handle_test_intent)

    def handle_test_intent(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node).get("wordnik")
        if not result:
            self.speak("Could not get info about " + node + " from wordnik")
            return
        relations = result.get("relations", {})
        definitions = result.get("definitions", [])
        if len(definitions):
            self.speak("wordnik found " + str(len(definitions)) + " definitions for " + node)
            for definition in definitions:
                self.speak(definition)
        if len(relations.keys()):
            self.speak("The following relationships to " + node + " are available")
            for key in relations:
                self.speak(key)
                self.speak(relations[key])

    def handle_ask_wordnik(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node)
        #self.speak(str(result))
        self.emitter.emit(Message("wordnik.result", result, self.message_context))

    def adquire(self, subject):
        logger.info('WordnikKnowledge_Adquire')
        dict = {}
        if subject is None:
            logger.error("No subject to adquire knowledge about")
        else:

            node_data = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                node_data["relations"] = self.get_related_words(subject)
                node_data["definitions"] = self.get_definitions(subject)
                # id info source
                dict["wordnik"] = node_data
            except Exception as e:
                logger.error(
                    "Could not parse wordnik for " + str(subject))
        return dict

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