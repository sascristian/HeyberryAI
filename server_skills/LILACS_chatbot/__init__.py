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


from threading import Thread
from time import sleep
import random

from adapt.intent import IntentBuilder
import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))
from mycroft.messagebus.message import Message
from LILACS_core.question_parser import LILACSQuestionParser
from mycroft.util.jarbas_services import KnowledgeService
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.util.markov import MarkovChain
from threading import Timer

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACSChatbotSkill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/19
    def __init__(self):
        super(LILACSChatbotSkill, self).__init__(name="ChatbotSkill")
        # initialize your variables
        self.reload_skill = False
        self.active = False
        self.parser = None
        self.service = None
        self.TIMEOUT = 2
        self.utterance = None
        self.chain = None

    def initialize(self):
        # register intents
        self.parser = LILACSQuestionParser()
        self.service = KnowledgeService(self.emitter)
        self.build_intents()

        # make timer thread to keep active
        self.timer_thread = Timer(60, self.make_active)
        self.timer_thread.setDaemon(True)
        self.timer_thread.start()

        try:
            self.chain = MarkovChain(2).load(dirname(
                __file__)+"/markovbot.json")
        except:
            self.chain = MarkovChain(2)
        self.emitter.on("speak", self.handle_speak)

    def handle_speak(self, message):
        utterance = message.data.get("utterance")
        if self.utterance:
            self.chain.add_tokens([utterance, self.utterance])
            self.chain.save(dirname(
                __file__)+"/markovbot.json")
            self.utterance = None

    def build_intents(self):
        # build intents
        deactivate_intent = IntentBuilder("DeactivateChatbotIntent") \
            .require("deactivateChatBotKeyword").build()
        activate_intent=IntentBuilder("ActivateChatbotIntent") \
            .require("activateChatBotKeyword").build()

        # register intents
        self.register_intent(deactivate_intent, self.handle_deactivate_intent)
        self.register_intent(activate_intent, self.handle_activate_intent)

    def handle_deactivate_intent(self, message):
        self.active = False
        self.speak_dialog("chatbot_off")

    def handle_activate_intent(self, message):
        self.active = True
        self.speak_dialog("chatbot_on")

    def handle_learning(self):
        pass

    def stop(self):
        if self.active:
           self.handle_deactivate_intent("global stop")

    def converse(self, utterances, lang="en-us"):
        # TODO check if intent would be handled by some skill and dont ove-ride

        # capture utterance to markov chain
        self.utterance = utterances[0]

        # HACK -> check manually fo stop while intent is not parsed
        if "stop" in utterances[0] or "off" in utterances[0] or "deactivate" in utterances[0]:
            return False

        # parse 1st utterance for entitys
        if self.active:
            nodes, parents, synonims = self.parser.tag_from_dbpedia(utterances[0])
            self.log.info("nodes: " + str(nodes))
            self.log.info("parents: " + str(parents))
            self.log.info("synonims: " + str(synonims))

            possible_responses = []

            for s in synonims:
                if s not in nodes:
                    nodes.setdefault(s)
                if synonims[s] not in nodes:
                    nodes.setdefault(synonims[s])

            # get concept net , talk
            for node in nodes:
                try:
                    # TODO request/read node from core/storage, so teach skill can be used to input answer
                    # TODO parse concept net for other usefull info about node and update db
                    dict = self.service.adquire(node, "concept net")
                    usages = dict["concept net"]["surfaceText"]
                    for usage in usages:
                        usage = usage.replace("[", "").replace("]", "")
                        self.chain.add_tokens([utterances[0], usage])
                        possible_responses.append(usage)
                    self.chain.save(dirname(
                        __file__) + "/markovbot.json")
                except:
                    self.log.info("could not get reply for node " + node)

            reply = "i don't want to talk anymore"
            try:
                # say something random
                reply = random.choice(possible_responses)
            except:
                reply = ""
                self.log.error("Could not get concept net response for: " +
                               utterances[0])
                words = self.chain.generate_sequence(random.randint(2, 10),
                                                     utterances[0])
                for word in words:
                    reply += " " + word
                self.log.debug("Markov Chain reply: " + reply)
                #return False

            self.speak(reply)
            return True

        # tell intent skill you did not handle intent
        return False


def create_skill():
    return LILACSChatbotSkill()