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


import aiml
import random
from os import listdir
from os.path import dirname, isfile
from mycroft.skills.core import FallbackSkill
from mycroft.util.log import getLogger
from mycroft.skills.intent_service import IntentParser
from adapt.intent import IntentBuilder

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class AIMLChatbotFallback(FallbackSkill):
    def __init__(self):
        super(AIMLChatbotFallback, self).__init__(name="AIMLFallbackSkill")
        self.reload_skill = False
        self.kernel = aiml.Kernel()
        # TODO read from config maybe?
        self.aiml_path = dirname(__file__) + "/aiml"
        self.brain_path = dirname(__file__) + "/bot_brain.brn"
        self.chat_mode = False
        self.parser = None

    def initialize(self):
        self.load_brain()
        self.parser = IntentParser(self.emitter)
        self.register_fallback(self.handle_fallback, 20)
        off_intent = IntentBuilder("AIMLOffIntent"). \
            require("StopKeyword").require("chatbotKeyword").build()
        on_intent = IntentBuilder("AIMLONIntent"). \
            require("StartKeyword").require("chatbotKeyword").build()
        ask_intent = IntentBuilder("askAIMLIntent"). \
            require("chatbotQuery").build()
        demo_intent = IntentBuilder("chatbotdemoIntent"). \
            require("ChatBotDemo").require("chatbotKeyword").build()
        # register intents
        self.register_intent(off_intent, self.handle_chat_stop_intent)
        self.register_intent(on_intent, self.handle_chat_start_intent)
        self.register_intent(ask_intent, self.handle_ask_aiml_intent)
        self.register_intent(demo_intent, self.handle_talk_to_yourself_intent)

    def handle_ask_aiml_intent(self, message):
        query = message.data.get("chatbotQuery")
        self.speak(self.ask_brain(query))

    def handle_talk_to_yourself_intent(self, message):
        text = random.choice["Hello", "Do you believe in god", "lets chat",
                             "lets play a game", "are you a terminator",
                             "are you human", "are you alive", "do you love me", "are you evil"]
        i = 100
        while i>0:
            text = self.ask_brain(text)
            self.speak(text)
            i -= 1

    def handle_chat_start_intent(self, message):
        self.chat_mode = True
        self.speak_dialog("chatbotON")

    def handle_chat_stop_intent(self, message):
        self.chat_mode = False
        self.speak_dialog("chatbotOFF")

    def load_brain(self):
        if isfile(self.brain_path):
            self.kernel.bootstrap(brainFile=self.brain_path)
        else:
            aimls = listdir(self.aiml_path)
            for aiml in aimls:
                self.kernel.bootstrap(learnFiles=self.aiml_path + "/" + aiml)
            self.kernel.saveBrain(self.brain_path)

    def ask_brain(self, utterance):
        response = self.kernel.respond(utterance)
        return response

    def handle_fallback(self, message):
        utterance = message.data.get("utterance")
        answer = self.ask_brain(utterance)
        if answer != "":
            self.speak(answer)
            return True
        return False

    def converse(self, utterances, lang="en-us"):
        # chat flag over-rides all skills
        if self.chat_mode:
            intent, id = self.parser.determine_intent(utterances[0])
            if id == self.skill_id:
                # some intent from this skill will trigger
                return False
            self.speak(self.ask_brain(utterances[0]), expect_response=True)
            return True
        return False

    def stop(self):
        if self.chat_mode:
            self.chat_mode = False
            self.speak_dialog("chatbotOFF")


def create_skill():
    return AIMLChatbotFallback()
