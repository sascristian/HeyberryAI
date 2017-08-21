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


from cleverwrap import CleverWrap
import random
from mycroft.skills.core import FallbackSkill
from mycroft.util.log import getLogger
from mycroft.skills.intent_service import IntentParser
from adapt.intent import IntentBuilder

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class CleverbotFallback(FallbackSkill):
    def __init__(self):
        super(CleverbotFallback, self).__init__()
        self.reload_skill = False
        self.chat_mode = False
        self.parser = None
        try:
            api_key = self.config_core.get("APIS")["Cleverbot"]
        except:
            api_key = self.config.get("CleverbotAPI")
        self.cleverbot = CleverWrap(api_key)

    def initialize(self):
        self.parser = IntentParser(self.emitter)
        self.register_fallback(self.handle_fallback, 50)
        off_intent = IntentBuilder("CleverbotOffIntent"). \
            require("StopKeyword").require("CleverbotKeyword").build()
        on_intent = IntentBuilder("CleverbotOnIntent"). \
            require("StartKeyword").require("CleverbotKeyword").build()
        ask_intent = IntentBuilder("askCleverbotIntent"). \
            require("chatbotQuery").build()
        demo_intent = IntentBuilder("CleverbotdemoIntent"). \
            require("ChatBotDemo").require("CleverbotKeyword").build()
        # register intents
        self.register_intent(off_intent, self.handle_chat_stop_intent)
        self.register_intent(on_intent, self.handle_chat_start_intent)
        # using browser service for this (free)
        #self.register_intent(ask_intent, self.handle_ask_Cleverbot_intent)
        self.register_intent(demo_intent, self.handle_talk_to_Cleverbot_intent)

    def handle_ask_Cleverbot_intent(self, message):
        query = message.data.get("chatbotQuery")
        self.speak(self.ask_cleverbot(query))

    def handle_talk_to_Cleverbot_intent(self, message):
        text = random.choice["Hello", "Do you believe in god", "lets chat",
                             "lets play a game", "are you a terminator",
                             "are you human", "are you alive", "do you love me", "are you evil"]
        for i in range(0, 100):
            text = self.ask_cleverbot(text)
            self.speak(text)

    def handle_chat_start_intent(self, message):
        self.chat_mode = True
        self.speak_dialog("chatbotON")

    def handle_chat_stop_intent(self, message):
        self.chat_mode = False
        self.speak_dialog("chatbotOFF")

    def ask_cleverbot(self, utterance):
        response = self.cleverbot.say(utterance)
        return response

    def handle_fallback(self, message):
        utterance = message.data.get("utterance")
        answer = self.ask_cleverbot(utterance)
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
            self.speak(self.ask_cleverbot(utterances[0]), expect_response=True)
            return True
        return False

    def stop(self):
        self.cleverbot.reset()
        if self.chat_mode:
            self.chat_mode = False
            self.speak_dialog("chatbotOFF")


def create_skill():
    return CleverbotFallback()
