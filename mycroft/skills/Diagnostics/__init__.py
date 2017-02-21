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

from threading import Thread
import random
import os
from time import sleep

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message

__author__ = 'jarbas'

LOGGER = getLogger(__name__)

client = None

class DiagnosticsSkill(MycroftSkill):

    def __init__(self):
        super(DiagnosticsSkill, self).__init__(name="DiagnosticsSkill")

        global client
        client = WebsocketClient()

        # vision
        self.numberfusers = 0
        self.smiling = False
        self.movement = False
        self.master = False

        def vision(message):
            self.numberfusers = message.data.get('number of persons')
            self.smiling = message.data.get('smile detected ')
            self.movement = message.data.get('movement')
            self.master = message.data.get('master')

        #leaks found
        self.leaks = 0
        self.totalleaks = 0

        def leakfound(message):
            self.leaks+=1

        #facebook
        self.agendednum = 0
        def face(message):
            self.agendednum = message.data.get('agended_posts')
            self.faceD = True

        #subcosnciousness
        self.lasttought = "my name is jarbas"
        self.numberoftoughts = 0
        self.innervoice = "do nothing"
        self.mood = "neutral"
        self.serotonine = 0
        self.dopamine = 0
        self.tiredness = 0
        self.activefriends = 0

        def mood(message):
            self.serotonine = message.data.get('serotonine')
            self.dopamine = message.data.get('dopamine')
            self.tiredness = message.data.get('tiredness')
            self.mood = message.data.get('mood')
            self.innervoice = message.data.get('innervoice')
            self.numberoftoughts = message.data.get('entropy_number')
            self.activefriends = message.data.get('active_friends')
            self.lasttought = message.data.get('last_tought')
            self.moodD = True

        def toughts(message):
            self.lasttought = message.data.get('text')

      #  client.emitter.on('sentiment_result', toughts)
        client.emitter.on('context_update', vision)
        client.emitter.on('leak_analisys', leakfound)
        client.emitter.on('face_diagnostics', face)
        client.emitter.on('mood_diagnostics', mood)

        # poems composed
        self.poems = 0
        # number of dreams
        self.dreams = 0
        self.count()


        ###### register as many of these as needed to have some executed skill/service influence something

        def connect():
            client.run_forever()

        self.event_thread = Thread(target=connect)
        self.event_thread.setDaemon(True)
        self.event_thread.start()

        self.timing = 120 #seconds beetween auto_diagnostic update
        def diagnostic_auto_update():
            while True:
                sleep(self.timing)
                self.request_diagnostics_update()
            #LOGGER.info("diagnostics auto update requested")

        self.event_thread = Thread(target=diagnostic_auto_update)
        self.event_thread.setDaemon(True)
        self.event_thread.start()

    def initialize(self):
        self.load_data_files(dirname(__file__))

        diagnostics_intent = IntentBuilder("FullDiagnosticsIntent"). \
            require("fulldiagnostics").build()
        self.register_intent(diagnostics_intent, self.handle_FullDiagnostics_intent)

        vdiagnostics_intent = IntentBuilder("VisionDiagnosticsIntent"). \
            require("visiondiagnostics").build()
        self.register_intent(vdiagnostics_intent, self.handle_VisionDiagnostics_intent)

        fbdiagnostics_intent = IntentBuilder("FBDiagnosticsIntent"). \
            require("fbdiagnostics").build()
        self.register_intent(fbdiagnostics_intent, self.handle_FaceBookDiagnostics_intent)

        mdiagnostics_intent = IntentBuilder("MoodDiagnosticsIntent"). \
            require("mooddiagnostics").build()
        self.register_intent(mdiagnostics_intent, self.handle_MoodDiagnostics_intent)

        cdiagnostics_intent = IntentBuilder("CreativityDiagnosticsIntent"). \
            require("creativitydiagnostics").build()
        self.register_intent(cdiagnostics_intent, self.handle_CreativityDiagnostics_intent)

        ldiagnostics_intent = IntentBuilder("LeakDiagnosticsIntent"). \
            require("leakdiagnostics").build()
        self.register_intent(ldiagnostics_intent, self.handle_LeaksDiagnostics_intent)

        hdiagnostics_intent = IntentBuilder("HardwareDiagnosticsIntent"). \
            require("hardware").build()
        self.register_intent(hdiagnostics_intent, self.handle_hardware_diagnostics)

        ndiagnostics_intent = IntentBuilder("NetworkDiagnosticsIntent"). \
            require("network").build()
        self.register_intent(ndiagnostics_intent, self.handle_network_diagnostics)

    def count(self):
        # poems composed
        self.poems = 0
        for f in os.listdir("/home/user/mycroft-core/mycroft/skills/Poetry/results"):
            self.poems += 1

        # number of dreams
        self.dreams = 0
        for f in os.listdir("/home/user/mycroft-core/mycroft/skills/dreamskill/dream_output"):
            self.dreams += 1

        #leaks found
        self.totalleaks = 0
        for f in os.listdir("/home/user/mycroft-core/mycroft/dumpmon/dumps"):
            self.totalleaks += 1

    def request_diagnostics_update(self):
        LOGGER.info("diagnostics update requested")
        client.emit(
            Message("diagnostics_request"))

    def handle_VisionDiagnostics_intent(self, message):
     #   self.speak("Starting Vision Diagnostics")
        self.speak("Number of faces detected, " + str(self.numberfusers))
        self.speak("Is User smiling, " + str(self.smiling))
        self.speak("Is Master Present, " + str(self.master))
        self.speak("Movement Detected, " + str(self.movement))

    def handle_FaceBookDiagnostics_intent(self, message):
        self.request_diagnostics_update()
     #   self.speak("Starting Face Book Diagnostics")
        self.speak("Number of agended posts, " + str(self.agendednum))

    def handle_MoodDiagnostics_intent(self, message):
        self.request_diagnostics_update()
      #  self.speak("Starting Sub Consciousness Diagnostics")
        self.speak("Mood :" + str(self.mood))
        self.speak("inner voice :" + str(self.innervoice))
        self.speak("last tought :" + str(self.lasttought))
        self.speak("number of toughts :" + str(self.numberoftoughts))
        self.speak("number of active chat friends :" + str(self.activefriends))
        self.speak("dopamine levels :" + str(self.dopamine)[:5])
        self.speak("serotonine levels :" + str(self.serotonine)[:5])
        self.speak("tiredness levels :" + str(self.tiredness)[:5])

    def handle_CreativityDiagnostics_intent(self, message):
      #  self.speak("Starting Creativity Diagnostics")
        self.count()
        self.speak("Number of dreams," + str(self.dreams))
        self.speak("Number of poems composed," + str(self.poems))

    def handle_LeaksDiagnostics_intent(self, message):
       # self.speak("Starting Leak Sniffing Diagnostics")
        self.speak("Number of leaks found since start up," + str(self.leaks))
        self.count()
        self.speak("Number of leaks found since implementation," + str(self.totalleaks))

    def handle_FullDiagnostics_intent(self, message):
        self.speak("Starting Full Diagnostics")
        self.handle_hardware_diagnostics("ignore this")
        sleep(1)
        self.handle_network_diagnostics("ignore this")
        sleep(1)
        self.handle_VisionDiagnostics_intent("ignore this")
        sleep(1)
        self.handle_MoodDiagnostics_intent("ignore this")
        sleep(1)
        self.handle_FaceBookDiagnostics_intent("ignore this")
        sleep(1)
        self.handle_CreativityDiagnostics_intent("ignore this")
        sleep(1)
        self.handle_LeaksDiagnostics_intent("ignore this")

    def handle_hardware_diagnostics(self, message):
       # self.speak("Starting Hardware Diagnostics")
        ### request cpu from the7erm diagnostics skill
        client.emit(
            Message("recognizer_loop:utterance",
                    {'utterances': ["cpu usage"]}))
        ### request disk from the7erm diagnostics skill
        client.emit(
            Message("recognizer_loop:utterance",
                    {'utterances': ["drive space"]}))
        ### request uptime from the7erm diagnostics skill
        client.emit(
            Message("recognizer_loop:utterance",
                    {'utterances': ["uptime"]}))

    def handle_network_diagnostics(self, message):
    #    self.speak("Starting Network Diagnostics")
        ### request ip from the7erm diagnostics skill
        client.emit(
            Message("recognizer_loop:utterance",
                    {'utterances': ["public ip"]}))

    def stop(self):
        pass


def create_skill():
    return DiagnosticsSkill()
