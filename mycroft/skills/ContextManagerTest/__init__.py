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
        self.manager = ContextManager()
        self.flag = False #results received flag
        #self.context_dict = {}

    def initialize(self):
        self.load_data_files(dirname(__file__))

        self.emitter.on("context_result", self.handle_context_result)
        #### receives the following data
        #  Message("context_result", {'full_dictionary': self.context_dict,'bluetooth': self.bluetooth_dict, 'abstract': self.abstract_dict, 'signals': self.signals_dict, 'results': self.results_dict, 'intents': self.intents_dict,'regex': self.regex_dict,'skills': self.skills_dict})

        context_intent = IntentBuilder("ContextTestIntent")\
            .require("contextKeyword").build()
        self.register_intent(context_intent,
                             self.handle_context_intent)

    def handle_context_result(self, message):
        dict = message.data["regex"]
        for key in dict:
            #adapt way
            if dict[key] is not None:
                entity = {'key': key, 'data': dict[key], 'confidence': 1.0}
                #check for duplicates before injecting,  shouldnt this be auto-handled by adapt?
                contexts = self.manager.get_context()
                flag = False
                for ctxt in contexts:
                    if ctxt["key"] == key and ctxt["data"] == dict[key]:
                        flag = True #its duplicate!
                if not flag:
                    self.manager.inject_context(entity)
                    print "injecting " + str(entity)


            #old school way
            #    if key not in self.context_dict:
            #        self.context_dict.setdefault(key)
            #    self.context_dict[key] = dict[key]

        self.flag = True

    def handle_context_intent(self, message):
        self.emitter.emit(Message("context_request"))
        while not self.flag:
            pass #wait results response
        self.speak_dialog("ctxt")

        contexts = self.manager.get_context()

        #adapt way
        for ctxt in contexts:
            #print ctxt
            if ctxt["data"] is not None:
                self.speak(ctxt["key"])
                self.speak(ctxt["data"])

        # old school way
        #for ctxt in self.context_dict:
        #    if self.context_dict[ctxt] is not None:
        #        self.speak(ctxt)
        #        self.speak(self.context_dict[ctxt])
        self.flag = False

    def stop(self):
        pass


def create_skill():
    return ContextSkill()
