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
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class AgainSkill(MycroftSkill):
    def __init__(self):
        super(AgainSkill, self).__init__()
        self.reload_skill = False
        self.last_skill = 0
        self.last_intent = None
        self.last_intent_data = {}
        self.last_intent_context = {}
        self.context = {"repetition": True}
        self.last_utterance = None

    def initialize(self):
        again_intent = IntentBuilder("AgainIntent"). \
            require("AgainKeyword").build()
        self.register_intent(again_intent, self.handle_again_intent)
        # TODO use intent.execution messages ?
        self.emitter.on("message", self.track_intent)

    def track_intent(self, message):
        message = Message.deserialize(message)
        fmessages = ["padatious"]
        if ":" in message.type:
            skill, intent = message.type.split(":")
            self.context = self.get_message_context(message.context)
            if intent == "utterance":
                utterance = message.data["utterances"][0]
                self.log.info(
                    "Tracking last executed utterance: " + utterance)
                self.last_utterance = utterance
                self.last_skill = "utterance"
                return
            elif skill == str(self.skill_id) or skill in fmessages:
                return
            self.log.info("Tracking last executed intent: " + message.type)
            self.last_skill = skill
            self.last_intent = intent
            self.last_intent_data = message.data

    def handle_again_intent(self, message):
        if self.last_skill == "utterance":
            msg = Message("recognizer_loop:utterance",
                          {"utterance": self.last_utterance},
                          self.context)
            self.log.info("Repeating last sent utterance")
            self.emitter.emit(msg)
        elif self.last_intent is None:
            self.speak_dialog("again.fail")
            return
        msg = Message(str(self.last_skill) + ":" + self.last_intent,
                      self.last_intent_data, self.context)
        # self.speak_dialog("again", {"intent": self.last_intent})
        self.log.info("Repeating last executed intent")
        self.emitter.emit(msg)

    def stop(self):
        pass


def create_skill():
    return AgainSkill()
