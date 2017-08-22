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

import wptools


class LILACSWikidataSkill(MycroftSkill):
    def __init__(self):
        super(LILACSWikidataSkill, self).__init__(
            name="LILACS_Wikidata_Skill")

    def initialize(self):
        self.emitter.on("wikidata.request", self.handle_ask_wikidata)
        test_intent = IntentBuilder("TestWikidataIntent") \
            .require("test").require("TargetKeyword").build()
        self.register_intent(test_intent, self.handle_test_intent)

    def handle_test_intent(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node).get("wikidata")
        if not result:
            self.speak("Could not get info about " + node + " from wikidata")
            return
        self.speak("parsing for speech not yet implemented")
        result = str(result).replace("[", " ").replace("]", " ")\
            .replace("(", " ").replace(")", " ").replace(":", ",")\
            .replace(";", ".").replace("{", " ").replace("}", " ")
        self.speak(result)

    def handle_ask_wikidata(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node)
        #self.speak(str(result))
        self.emitter.emit(Message("wikidata.result", result, self.message_context))

    def adquire(self, subject):
        logger.info('WikidataKnowledge_Adquire')
        dict = {}
        if subject is None:
            logger.error("No subject to adquire knowledge about")
        else:

            node_data = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                page = wptools.page(subject, silent=True,
                                    verbose=False).get_wikidata()
                # parse for distant child of
                node_data["description"] = page.description
                # direct child of
                node_data["what"] = page.what
                # data fields
                node_data["data"] = page.wikidata
                # related to
                # TODO parse and make cousin/child/parent
                node_data["properties"] = page.props
                # id info source
                dict["wikidata"] = node_data
            except Exception as e:
                logger.error(
                    "Could not parse wikidata for " + str(subject))
        return dict


def create_skill():
    return LILACSWikidataSkill()