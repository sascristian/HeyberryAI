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


from random import randrange

import re
import wikipedia as wiki
import random
import time
from adapt.intent import IntentBuilder
from os.path import dirname
from os import listdir
from threading import Thread
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class KnowledgeSkill(MycroftSkill):
    def __init__(self):
        super(KnowledgeSkill, self).__init__(name="KnowledgeSkill")
        self.max_results = self.config['max_results']
        self.max_phrases = self.config['max_phrases']

        self.savepath = dirname(__file__) +"/saved"

        self.knowledge = []
        self.load_knowledge()

        # auto adquire knowledge using knowledge objective, every 5 mins gets an article
        self.autoadquire = True

        def aquisition():
            start_time = time.time()
            while True:
                if time.time() - start_time >= 5*60: #every 5 min
                    self.emitter.emit(Message("ExecuteObjectiveIntent",{"Objective":"adquire knowledge"}))
                    start_time = time.time()

        if self.autoadquire:
            self.event_thread = Thread(target=aquisition)
            self.event_thread.setDaemon(True)
            self.event_thread.start()

    def initialize(self):

        knowledge_intent = IntentBuilder("KnowledgeIntent").require(
            "KnowledgeKeyword").require("ArticleTitle").optionally("SavePath").build()
        self.register_intent(knowledge_intent, self.handle_knowledge_intent)

        teach_me_intent = IntentBuilder("TeachIntent").require(
            "TeachKeyword").build()
        self.register_intent(teach_me_intent, self.handle_teach_intent)

    def load_knowledge(self):
        for file in listdir(self.savepath):
            path = self.savepath + "/" + file
            try:
                with open(path) as f:
                    words = f.readlines()
                    for word in words:
                        self.knowledge.append(word.replace("\n", ""))
            except:
                pass

    def handle_teach_intent(self, message):
        self.speak(random.choice(self.knowledge))

    def handle_knowledge_intent(self, message):
        title = message.data.get("ArticleTitle")

        savepath = message.data.get("SavePath")
        if savepath is None:
            savepath = self.savepath
        savepath += "/" + title + ".txt"

        try:

            #self.add_result("ArticleTitle",title)
            #self.add_result("SavePath", savepath)
            results = wiki.search(title, self.max_results)
            summary = re.sub(
                r'\([^)]*\)|/[^/]*/', '',
                wiki.summary(results[0], self.max_phrases))

            wfile = open(savepath, "w")
            wfile.write(summary.encode('utf-8'))
            wfile.close()
            #self.speak(summary)
            self.knowledge.append(summary)
            #self.emit_results()

        except wiki.exceptions.DisambiguationError as e:
            options = e.options[:self.max_results]
            LOGGER.debug("Multiple options found: " + ', '.join(options))

            for opt in options:
                savepath = message.data.get("SavePath")
                if savepath is None:
                    savepath = self.savepath
                savepath += "/" + opt + ".txt"

                #self.add_result("ArticleTitle", opt)
                #self.add_result("SavePath", savepath)

                results = wiki.search(opt, self.max_results)
                summary = re.sub(
                    r'\([^)]*\)|/[^/]*/', '',
                    wiki.summary(results[0], self.max_phrases))

                wfile = open(savepath, "w")
                wfile.write(summary.encode('utf-8'))
                wfile.close()
                #self.speak(summary)
                self.knowledge.append(summary)
                #self.emit_results()


        except Exception as e:
            LOGGER.error("Error: {0}".format(e))
            #self.speak("Couldn't find knowledge about " + title + " right now")

    def stop(self):
        pass


def create_skill():
    return KnowledgeSkill()
