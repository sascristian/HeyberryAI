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


import sys
from threading import Timer

from adapt.intent import IntentBuilder
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from mycroft.messagebus.message import Message
from jarbas_utils.question_parser import LILACSQuestionParser
from jarbas_utils.skill_tools import KnowledgeQuery
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACSCuriositySkill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/19
    def __init__(self):
        super(LILACSCuriositySkill, self).__init__(name="CuriositySkill")
        # initialize your variables
        self.reload_skill = False
        self.active = False
        self.get_node_info = False
        self.parser = None
        self.service = None
        self.TIMEOUT = 2

    def initialize(self):
        # register intents
        self.parser = LILACSQuestionParser()
        self.service = KnowledgeQuery(self.name, self.emitter)
        self.build_intents()

        timer_thread = Timer(60, self.make_active)
        timer_thread.setDaemon(True)
        timer_thread.start()

    def build_intents(self):
        self.emitter.on("speak", self.handle_speak)

        # build intents
        deactivate_intent = IntentBuilder("DeactivateCuriosityIntent") \
            .require("deactivateCuriosityKeyword").build()
        activate_intent=IntentBuilder("ActivateCuriosityIntent") \
            .require("activateCuriosityKeyword").build()

        # register intents
        self.register_intent(deactivate_intent, self.handle_deactivate_intent)
        self.register_intent(activate_intent, self.handle_activate_intent)

    def handle_speak(self, message):
        utterance = message.data["utterance"]
        self.curiosity(utterance)

    def handle_deactivate_intent(self, message):
        self.active = False
        self.speak_dialog("curiosity_off")

    def handle_activate_intent(self, message):
        self.active = True
        self.speak_dialog("curiosity_on")

    def stop(self):
        self.handle_deactivate_intent("global stop")

    def curiosity(self, utterance):
        if not self.active:
            return False
        # parse all utterances for entitys
        try:
            nodes, parents, synonims = self.parser.tag_from_dbpedia(utterance)
        except Exception as e:
            self.log.error(e)
            return False
        self.message_context["source"] = "LILACS_curiosity"
        self.log.info("nodes: " + str(nodes))
        self.log.info("parents: " + str(parents))
        self.log.info("synonims: " + str(synonims))
        # if flag get info for nodes
        # TODO use appropriate backends fo each field
        if self.get_node_info:
            backend = "dbpedia"
            for node in nodes:
                node_info = self.service.adquire(node, backend)
                print node_info

        #signal core to create nodes
        for node in nodes:
            node_dict = {}
            node_dict["name"] = node
            connections = {}
            connections["parents"] = {}
            connections["childs"] = {}
            connections["synonims"] = {}
            connections["antonims"] = {}
            node_dict["connections"] = connections
            node_dict["data"] = {}

            self.emitter.emit(Message("new_node", node_dict, self.message_context))
        for node in parents:
            node_dict = {}
            node_dict["name"] = node
            connections = {}
            connections["parents"] = {}
            for p in parents[node]:
                connections["parents"][p] = 5
            connections["childs"] = {}
            connections["synonims"] = {}
            connections["antonims"] = {}
            node_dict["connections"] = connections
            node_dict["data"] = {}
            self.emitter.emit(Message("new_node", node_dict, self.message_context))
        for node in synonims:
            node_dict = {}
            node_dict["name"] = node
            connections = {}
            connections["parents"] = {}
            connections["childs"] = {}
            connections["synonims"] = {synonims[node]: 5}
            connections["antonims"] = {}
            node_dict["connections"] = connections
            node_dict["data"] = {}
            self.emitter.emit(Message("new_node", node_dict, self.message_context))

    def converse(self, utterances, lang="en-us"):
        self.curiosity(utterances[0])
        # tell intent skill you did not handle intent
        return False


def create_skill():
    return LILACSCuriositySkill()