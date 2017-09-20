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

import wptools
from mycroft.skills.displayservice import DisplayService
from mycroft.skills.LILACS_fallback import LILACSFallback


class LILACSWikipediaSkill(LILACSFallback):
    def __init__(self):
        super(LILACSWikipediaSkill, self).__init__(
            name="wikipedia")

    def start_up(self):
        ''' Use instead of initialize method '''
        self.display_service = DisplayService(self.emitter, self.name)

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
        result = self._adquire(node).get(self.name).get("node_dict")
        if not result:
            self.speak("Could not get info about " + node + " from " +
                       self.name)
            return
        ## update node in memory ##
        result = result.get("data", {})
        self.update_node(node, node_data=result)

        ### speak results back ###
        url = result.get("url")
        external_links = result.get("external_links", [])
        pics = [result.get("pic")]
        metadata = {}
        if url:
            metadata["url"] = url
        if pics[0]:
            metadata["picture"] = pics[0]
            self.display_service.display(pics, utterance=message.data.get(
                "utterance", ""))

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

    def get_connections(self, subject):
        ''' implement getting a dict of parsed connections here '''
        node_cons = {}
        return node_cons

    def get_data(self, subject):
        ''' implement parsing of data here '''
        node_data = {}
        # get knowledge about
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
        except:
            self.log.error("Failed to retrieve data from " + self.name)
        return node_data

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