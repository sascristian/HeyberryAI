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


import random

from adapt.intent import IntentBuilder
from os.path import dirname

from jarbas_utils.question_parser import LILACSQuestionParser
from jarbas_utils.jarbas_services import KnowledgeService
from mycroft.skills.core import MycroftSkill

__author__ = 'jarbas'

class LILACSRhymesSkill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/19
    def __init__(self):
        super(LILACSRhymesSkill, self).__init__(name="RhymesSkill")

    def initialize(self):
        # register intents
        self.parser = LILACSQuestionParser()
        self.service = KnowledgeService(self.emitter)
        self.build_intents()

    def build_intents(self):
        # build intents
        rhyme_intent = IntentBuilder("RhymeIntent").require("rhyme").build()

        # register intents
        self.register_intent(rhyme_intent, self.handle_rhyme_intent)

    def handle_rhyme_intent(self, message):
        utterance = message.data["utterance"]
        nodes, parents, synonims = self.parser.tag_from_dbpedia(utterance)
        if nodes == {}:
            node = utterance
            vocab = ["what rhymes with ", "rhyme off ", "rhymes off ", "rhyme of ", "rhymes of "]
            for u in vocab:
                node = node.replace(u, "")
            nodes = {node: 2}
        self.log.info("nodes: " + str(nodes))
        try:
            rhymes = self.service.adquire(nodes.keys()[0], "wordnik")["wordnik"]["relations"]["rhyme"]
            self.speak_dialog("rhyme", {"subject":nodes.keys()[0], "word": random.choice(rhymes)})
        except:
            self.speak("i dont know...")

    def stop(self):
        pass


def create_skill():
    return LILACSRhymesSkill()