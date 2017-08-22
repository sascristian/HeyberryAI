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

import requests


class LILACSConceptNetSkill(MycroftSkill):
    def __init__(self):
        super(LILACSConceptNetSkill, self).__init__(
            name="LILACS_ConceptNet_Skill")

    def initialize(self):
        self.emitter.on("conceptnet.request", self.handle_ask_conceptnet)
        test_intent = IntentBuilder("TestconceptnetIntent") \
            .require("testc").require("TargetKeyword").build()
        self.register_intent(test_intent, self.handle_test_intent)

    def handle_test_intent(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node).get("concept net")
        if not result:
            self.speak("Could not get info about " + node + " from concept net")
            return

        if len(result.get("IsA", [])):
            self.speak("concept net says " + node + " is")
            for thing in result["IsA"]:
                self.speak(thing)

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

        if len(result.get("RelatedTo", [])):
            self.speak("concept net says " + node + " is related to")
            for thing in result["RelatedTo"]:
                self.speak(thing)

        if len(result.get("RelatedNodes", [])):
            self.speak("concept net says these things are related to " + node)
            for thing in result["RelatedNodes"]:
                self.speak(thing)

    def handle_ask_conceptnet(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node)
        #self.speak(str(result))
        self.emitter.emit(Message("conceptnet.result", result, self.message_context))

    def adquire(self, subject):
        logger.info('ConceptNetKnowledge_Adquire')
        dict = {}
        if subject is None:
            logger.error("No subject to adquire knowledge about")
        else:

            node_data = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                parents = []
                capable = []
                has = []
                desires = []
                used = []
                related = []
                examples = []
                location = []
                other = []

                obj = requests.get(
                    'http://api.conceptnet.io/c/en/' + subject).json()
                for edge in obj["edges"]:
                    rel = edge["rel"]["label"]
                    node = edge["end"]["label"]
                    start = edge["start"]["label"]
                    if start != node and start not in other:
                        other.append(start)
                    if rel == "IsA":
                        node = node.replace("a ", "").replace("an ", "")
                        if node not in parents:
                            parents.append(node)
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
                    elif rel == "RelatedTo":
                        if node not in related:
                            related.append(node)
                    elif rel == "AtLocation":
                        if node not in location:
                            location.append(node)
                    usage = edge["surfaceText"]
                    if usage is not None:
                        examples.append(usage)
                # id info source
                dict.setdefault("concept net",
                                {"RelatedNodes": other, "IsA": parents,
                                 "CapableOf": capable, "HasA": has,
                                 "Desires": desires, "UsedFor": used,
                                 "RelatedTo": related,
                                 "AtLocation": location,
                                 "surfaceText": examples})

            except Exception as e:
                logger.error(
                    "Could not parse conceptnet for " + str(subject))
        return dict


def create_skill():
    return LILACSConceptNetSkill()