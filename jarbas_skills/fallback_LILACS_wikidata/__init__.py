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
from mycroft.skills.LILACS_fallback import LILACSFallback


class LILACSwikidataSkill(LILACSFallback):
    def __init__(self):
        super(LILACSwikidataSkill, self).__init__(
            name="wikidata")

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
        self.speak("parsing for conceptnet speech not yet implemented")
        result = str(result).replace("[", " ").replace("]", " ") \
            .replace("(", " ").replace(")", " ").replace(":", ",") \
            .replace(";", ".").replace("{", " ").replace("}", " ")
        self.speak(result)

    def get_connections(self, subject):
        ''' implement getting a dict of parsed connections here '''
        node_cons = {"parents": {}}
        # get knowledge about
        try:
            page = wptools.page(subject, silent=True,
                                verbose=False).get_wikidata()
            # direct child of
            for parent in page.what:
                node_cons["parents"][parent] = 5
            # related to
            # TODO parse and make cousin/child/parent
            props = page.props
        except:
            self.log.error("Failed to retrieve data from " + self.name)
        return node_cons

    def get_data(self, subject):
        ''' implement parsing of data here '''
        node_data = {}
        # get knowledge about
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
        except:
            self.log.error("Failed to retrieve data from " + self.name)
        return node_data


def create_skill():
    return LILACSwikidataSkill()
