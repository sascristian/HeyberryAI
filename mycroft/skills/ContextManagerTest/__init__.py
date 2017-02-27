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

import thread

__author__ = 'jarbas'

logger = getLogger(__name__)

client = None

class ContextSkill(MycroftSkill):

    def __init__(self):
        super(ContextSkill, self).__init__(name="ContextSkill")
        self.manager = ContextManager()
        self.flag = False #results received flag
        ##### messagebus
        global client
        client = WebsocketClient()

        client.emitter.on("context_result", self.handle_context_result)
        #### receives the following data
        #  Message("context_result", {'full_dictionary': self.context_dict,'bluetooth': self.bluetooth_dict, 'abstract': self.abstract_dict, 'signals': self.signals_dict, 'results': self.results_dict, 'intents': self.intents_dict,'regex': self.regex_dict,'skills': self.skills_dict})

        def connect():
            client.run_forever()

        thread.start_new_thread(connect, ())

    def initialize(self):
        self.load_data_files(dirname(__file__))

        context_intent = IntentBuilder("ContextTestIntent")\
            .require("contextKeyword").build()
        self.register_intent(context_intent,
                             self.handle_context_intent)

    def handle_context_result(self, message):
        dict = message.data["regex"]
        for key in dict:
            entity = {'key': key, 'data': dict[key], 'confidence': 1.0}
            self.manager.inject_context(entity)
        self.flag = True

    def handle_context_intent(self, message):
        client.emit(Message("context_request"))
        while not self.flag:
            pass
        self.speak_dialog("ctxt")
        contexts = self.manager.get_context()
        for ctxt in contexts:
            if ctxt["data"] is not None:
                self.speak(ctxt["key"])
                self.speak(ctxt["data"])
                print ctxt
        self.flag = False

    def stop(self):
        pass


def create_skill():
    return ContextSkill()
