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

from jarbas_utils.LILACS.question_parser import LILACSQuestionParser
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

    def initialize(self):
        # register intents
        self.parser = LILACSQuestionParser()
        self.service = KnowledgeQuery(self.name, self.emitter)
        self.build_intents()

    def build_intents(self):
        self.emitter.on("speak", self.handle_speak)
        self.emitter.on("recognizer_loop:utterance", self.handle_utterance)
        # build intents
        deactivate_intent = IntentBuilder("DeactivateCuriosityIntent") \
            .require("deactivateCuriosityKeyword").build()
        activate_intent = IntentBuilder("ActivateCuriosityIntent") \
            .require("activateCuriosityKeyword").build()

        # register intents
        self.register_intent(deactivate_intent, self.handle_deactivate_intent)
        self.register_intent(activate_intent, self.handle_activate_intent)

    def handle_utterance(self, message):
        utterances = message.data.get("utterances")
        self.curiosity(utterances[0])

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
        if self.active:
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

        # if flag get info for nodes, these will be loaded into lilacs_core
        #  memory
        if self.get_node_info:
            backend = "dbpedia"
            for node in nodes:
                node_dict = self.service._adquire(node, backend)
                print node_dict

        return True


def create_skill():
    return LILACSCuriositySkill()
