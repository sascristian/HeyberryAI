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

    def initialize(self):
        # register intents
        self.parser = LILACSQuestionParser()
        self.service = KnowledgeService(self.emitter)
        self.build_intents()

        # make thread to keep active
        self.make_bump_thread()

    def ping(self):
        while True:
            i = 0
            if self.active:
                self.emitter.emit(Message("recognizer_loop:utterance", {"source": "LILACS_chatbot_skill",
                                                                    "utterances": [
                                                                        "bump chat to active skill list"]}))
            while i < 60 * self.TIMEOUT:
                i += 1
                sleep(1)
            i = 0

    def make_bump_thread(self):
        timer_thread = Thread(target=self.ping)
        timer_thread.setDaemon(True)
        timer_thread.start()

    def build_intents(self):
        # build intents
        deactivate_intent = IntentBuilder("DeactivateChatbotIntent") \
            .require("deactivateChatBotKeyword").build()
        activate_intent=IntentBuilder("ActivateChatbotIntent") \
            .require("activateChatBotKeyword").build()

        bump_intent = IntentBuilder("BumpChatBotSkillIntent"). \
            require("bumpChatBotKeyword").build()

        # register intents
        self.register_intent(deactivate_intent, self.handle_deactivate_intent)
        self.register_intent(activate_intent, self.handle_activate_intent)
        self.register_intent(bump_intent, self.handle_set_on_top_active_list())

    def handle_set_on_top_active_list(self):
        # dummy intent just to bump curiosity skill to top of active skill list
        # called on a timer in order to always use converse method
        pass

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

    def converse(self, transcript, lang="en-us"):
        # TODO check if intent would be handled by some skill and dont ove-ride

        # HACK -> check manually fo stop while intent is not parsed
        if "stop" in transcript[0] or "off" in transcript[0] or "deactivate" in transcript[0]:
            return False

        # parse 1st utterance for entitys
        if self.active and "bump chat" not in transcript[0] and "bump curiosity" not in transcript[0]:
            nodes, parents, synonims = self.parser.tag_from_dbpedia(transcript[0])
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
                        possible_responses.append(usage.replace("[", "").replace("]", ""))
                except:
                    self.log.info("could not get reply for node " + node)

            reply = "i don't want to talk anymore"
            try:
                # say something random
                reply = random.choice(possible_responses)
            except:
                # dont know what to say
                # TODO consider ask user a question and play dumb / cleverbot / other ? backends everywhere??
                #try:
                #    self.log.info("asking brobot to generate a random response")
                #    reply = broback(transcript[0])
                #except:
                self.log.error("Could not get chatbot response for: " + transcript[0])
                #self.speak("Use teach skill to input correct chatbot answer")
                return False

            self.speak(reply)
            return True

        # tell intent skill you did not handle intent
        return False


def create_skill():
    return LILACSChatbotSkill()