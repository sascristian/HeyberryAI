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

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from adapt.context import ContextManager
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from time import sleep

__author__ = 'jarbas'

logger = getLogger(__name__)

client = None

class ContextSkill(MycroftSkill):

    def __init__(self):
        super(ContextSkill, self).__init__(name="ContextSkill")
        #self.context_dict = {}

    def initialize(self):
        self.load_data_files(dirname(__file__))

        context_intent = IntentBuilder("ContextTestIntent")\
            .require("contextKeyword").build()
        self.register_intent(context_intent,
                             self.handle_context_intent)

        self.emitter.on("context_result", self.handle_context_result)   ### only thing you need to have context in your skill!

    def handle_context_intent(self, message):
        self.emitter.emit(Message("context_request"))
        while not self.context_flag:
            pass #wait results response
        self.speak_dialog("ctxt")

        contexts = self.manager.get_context()

        #adapt way
        for ctxt in contexts:
            if ctxt["data"] is not None:
                self.speak(ctxt["key"])
                self.speak(ctxt["data"])

        # old school way
        #for ctxt in self.context_dict:
        #    if self.context_dict[ctxt] is not None:
        #        self.speak(ctxt)
        #        self.speak(self.context_dict[ctxt])
        self.context_flag = False


    def stop(self):
        pass


def create_skill():
    return ContextSkill()
