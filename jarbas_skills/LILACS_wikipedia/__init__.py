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
from mycroft.skills.displayservice import DisplayService


class LILACSWikipediaSkill(MycroftSkill):
    def __init__(self):
        super(LILACSWikipediaSkill, self).__init__(
            name="LILACS_Wikipedia_Skill")

    def initialize(self):
        self.emitter.on("wikipedia.request", self.handle_ask_wikipedia)
        test_intent = IntentBuilder("TestWikipediaIntent") \
            .require("testp").require("TargetKeyword").build()
        self.register_intent(test_intent, self.handle_test_intent)
        self.display_service = DisplayService(self.emitter, self.name)

    def handle_test_intent(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node).get("wikipedia")
        if not result:
            self.speak("Could not get info about " + node + " from wikipedia")
            return
        url = result.get("url")
        external_links = result.get("external_links", [])
        pics = [result.get("pic")]
        metadata = {}
        if url:
            metadata["url"] = url
        if pics[0]:
            metadata["pictures"] = pics
            self.display_service.display(pics, utterance=message.data.get[
                "utterance"])

        if result.get("description", "") != "":
            self.speak("wikipedia description says ")
            self.speak(result["summary"])

        infobox = result.get("infobox", {})
        if infobox != {}:
            self.speak("wikipedia infobox says ")
            for key in infobox:
                self.speak(key)
                self.speak(infobox[key])

        if result.get("summary", "") != "":
            self.speak("wikipedia summary says ")
            self.speak(result["summary"])

    def handle_ask_wikipedia(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node)
        #self.speak(str(result))
        self.emitter.emit(Message("wikipedia.result", result, self.message_context))

    def adquire(self, subject):
        logger.info('WikipediaKnowledge_Adquire')
        dict = {}
        if subject is None:
            logger.error("No subject to adquire knowledge about")
        else:

            node_data = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                page = wptools.page(subject, silent=True,
                                    verbose=False).get_query()
                node_data["pic"] = page.image('page')['url']
                node_data["name"] = page.label
                node_data["description"] = page.description
                node_data["summary"] = page.extext
                node_data["url"] = page.url
                # parse infobox
                node_data["infobox"] = self.parse_infobox(subject)
                # id info source
                dict["wikipedia"] = node_data
            except Exception as e:
                logger.error(
                    "Could not parse wikipedia for " + str(subject))
        return dict


    def parse_infobox(self, subject):
        page = wptools.page(subject, silent=True, verbose=False).get_parse()
        data = {}
        # TODO decent parsing, info is messy
        for entry in page.infobox:
            # print entry + " : " + page.infobox[entry]
            data[entry] = page.infobox[entry]
        return data


def create_skill():
    return LILACSWikipediaSkill()