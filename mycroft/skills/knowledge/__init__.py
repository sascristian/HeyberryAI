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
from adapt.intent import IntentBuilder
from os.path import join, dirname

from mycroft.skills.core import MycroftSkill
from mycroft.util import read_stripped_lines
from mycroft.util.log import getLogger

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class KnowledgeSkill(MycroftSkill):
    def __init__(self):
        super(KnowledgeSkill, self).__init__(name="KnowledgeSkill")
        self.max_results = self.config['max_results']
        self.max_phrases = self.config['max_phrases']

        self.savepath = dirname(__file__) +"/saved"

    def initialize(self):

        knowledge_intent = IntentBuilder("KnowledgeIntent").require(
            "KnowledgeKeyword").require("ArticleTitle").optionally("SavePath").build()
        self.register_intent(knowledge_intent, self.handle_knowledge_intent)

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
            wfile.write(summary)
            wfile.close()
            self.speak(summary)
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
                wfile.write(summary)
                wfile.close()
                self.speak(summary)
                #self.emit_results()


        except Exception as e:
            LOGGER.error("Error: {0}".format(e))
            self.speak("Couldn't find knowledge about " + title + " right now")

    def stop(self):
        pass


def create_skill():
    return KnowledgeSkill()
