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

import urllib
import json

from adapt.intent import IntentBuilder
from mycroft.skills.intent_service import IntentParser
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)


class Cleverbot:

    def __init__(self, apikey):

        self.URL = 'https://www.cleverbot.com/getreply'
        self.apiUrl = "{}?key={}&wrapper=python-wrapper".format(self.URL, apikey)
        self.ERRORS = {401: 'Cleverbot API key not valid',
                       404: 'Cleverbot API not found',
                       413: 'Cleverbot API request too large. Please limit requests to 8KB',
                       502: 'Unable to get reply from API server, please contact Cleverbot Support',
                       503: 'Cleverbot API: Too many requests from client',
                       504: 'Unable to get reply from API server, please contact Cleverbot Support'}

        try:
                self.request = urllib.urlopen(self.apiUrl)


        except urllib.HTTPError as err:
                if err.code in self.ERRORS:
                        print self.ERRORS[err.code]
                else:
                        raise

        self.response = json.loads(self.request.read())
        self.cs = self.response['cs']
        self.log = []

    def ask(self, question):
        self.log.append(question)
        question = urllib.quote_plus(question.encode('utf8'))
        qUrl = "{}&input={}&cs={}".format(self.apiUrl, question, self.cs)
        response = json.loads(urllib.urlopen(qUrl).read())
        self.cs = response['cs']
        self.log.append(response['output'])
        return response['output']


class CleverbotSkill(MycroftSkill):
    def __init__(self):
        super(CleverbotSkill, self).__init__(name="CleverbotSkill")
        # initialize your variables
        try:
            self.api = self.config_apis["CleverbotAPI"]
        except:
            try:
                self.api = self.config["CleverbotAPI"]
            except:
                self.api = "CC27mJvsulNAByg3_QZ5-kOGTjA"
        self.active = False
        self.parser = None
        self.service = None
        self.TIMEOUT = 2
        self.cb = Cleverbot(self.api)

    def initialize(self):
        # register intents
        self.intent_parser = IntentParser(self.emitter)
        self.build_intents()

    def build_intents(self):
        # build intents
        deactivate_intent = IntentBuilder("DeactivateCleverBotIntent") \
            .require("deactivateCleverBotKeyword").build()
        activate_intent=IntentBuilder("ActivateCleverbotIntent") \
            .require("activateCleverBotKeyword").build()
        talk_yourself_intent = IntentBuilder("TalkSelfCleverbotIntent") \
            .require("SelfChatCleverBotKeyword").build()

        # register intents
        self.register_intent(deactivate_intent, self.handle_deactivate_intent)
        self.register_intent(activate_intent, self.handle_activate_intent)
        self.register_intent(talk_yourself_intent, self.handle_talk_to_yourself_intent)

    def handle_deactivate_intent(self, message):
        self.active = False
        self.speak_dialog("cleverbot_off")

    def handle_activate_intent(self, message):
        self.active = True
        self.speak_dialog("cleverbot_on")

    def handle_talk_to_yourself_intent(self, message):
        text = "hello"
        self.speak(text)
        for i in range(0, 50):
            text = self.cb.ask(text)
            self.speak(text)

    def stop(self):
        if self.active:
           self.handle_deactivate_intent("global stop")

    def converse(self, transcript, lang="en-us"):
        if not self.active:
            return False
        # check if some of the intents will be handled
        intent, id = self.intent_parser.determine_intent(transcript[0])
        if id == self.skill_id:
            # some intent will be triggered inside this skill (off)
            return False
        else:
            answer = self.cb.ask(transcript[0])
            self.speak(answer)
        # tell intent skill you handled utterance
        return True


def create_skill():
    return CleverbotSkill()