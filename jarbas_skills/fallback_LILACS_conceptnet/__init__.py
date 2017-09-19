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

import requests
from mycroft.skills.LILACS_fallback import LILACSFallback


class LILACSConceptNetSkill(LILACSFallback):
    def __init__(self):
        super(LILACSConceptNetSkill, self).__init__(
            name="conceptnet")

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
        if len(result.get("connections").get("parents", {}).keys()):
            self.speak("concept net says " + node + " is")
            for thing in result.get("connections").get("parents", {}).keys():
                self.speak(thing)

        if len(result.get("connections").get("cousins", {}).keys()):
            self.speak("concept net says " + node + " is related to")
            for thing in result.get("connections").get("cousins", {}).keys():
                self.speak(thing)

        result = result.get("data", {})
        if len(result.get("CapableOf", [])):
            self.speak("concept net says " + node + " is capable of")
            for thing in result["CapableOf"]:
                self.speak(thing)

        if len(result.get("HasA", [])):
            self.speak("concept net says " + node + " has ")
            for thing in result["HasA"]:
                self.speak(thing)

        if len(result.get("Desires", [])):
            self.speak("concept net says " + node + " desires")
            for thing in result["Desires"]:
                self.speak(thing)

        if len(result.get("UsedFor", [])):
            self.speak("concept net says " + node + " is used for")
            for thing in result["UsedFor"]:
                self.speak(thing)

        if len(result.get("AtLocation", [])):
            self.speak("concept net says " + node + " can be found at")
            for thing in result["AtLocation"]:
                self.speak(thing)

    def get_connections(self, subject):
        ''' implement getting a dict of parsed connections here '''
        node_cons = {"parents": {}, "cousins": {}}
        obj = requests.get(
            'http://api.conceptnet.io/c/en/' + subject).json()
        for edge in obj["edges"]:
            rel = edge["rel"]["label"]
            node = edge["end"]["label"]
            start = edge["start"]["label"]
            if start != node and start not in node_cons["cousins"]:
                node_cons["cousins"][start] = 5
            if rel == "IsA":
                node = node.replace("a ", "").replace("an ", "")
                if node not in node_cons["parents"]:
                    node_cons["parents"][node] = 5
            elif rel == "RelatedTo":
                if node not in node_cons["cousins"]:
                    node_cons["cousins"][node] = 5
        return node_cons

    def get_data(self, subject):
        ''' implement parsing of data here '''
        node_data = {}
        # get knowledge about
        try:
            capable = []
            has = []
            desires = []
            used = []
            examples = []
            location = []
            obj = requests.get(
                'http://api.conceptnet.io/c/en/' + subject).json()
            for edge in obj["edges"]:
                rel = edge["rel"]["label"]
                node = edge["end"]["label"]
                if rel == "IsA":
                    continue
                elif rel == "RelatedTo":
                    continue
                elif rel == "CapableOf":
                    if node not in capable:
                        capable.append(node)
                elif rel == "HasA":
                    if node not in has:
                        has.append(node)
                elif rel == "Desires":
                    if node not in desires:
                        desires.append(node)
                elif rel == "UsedFor":
                    if node not in used:
                        used.append(node)
                elif rel == "AtLocation":
                    if node not in location:
                        location.append(node)
                usage = edge["surfaceText"]
                if usage is not None:
                    examples.append(usage)
            # id info source
            node_data = {"CapableOf": capable, "HasA": has,
                         "Desires": desires, "UsedFor": used,
                         "AtLocation": location,
                         "surfaceText": examples}
        except:
            self.log.error("Failed to retrieve data from " + self.name)
        return node_data


def create_skill():
    return LILACSConceptNetSkill()
