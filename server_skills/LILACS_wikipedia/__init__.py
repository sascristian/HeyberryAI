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
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message
from random import randrange

import re
import wikipedia as wiki
from os.path import join, dirname

from mycroft.skills.core import MycroftSkill
from mycroft.util import read_stripped_lines
import wptools


__author__ = 'jarbas'

logger = getLogger(__name__)



class LILACSWikipediaSkill(MycroftSkill):
    def __init__(self):
        super(LILACSWikipediaSkill, self).__init__(
            name="LILACS_Wikipedia_Skill")
        self.max_results = self.config['max_results']
        self.max_phrases = self.config['max_phrases']
        self.question = 'Would you like to know more about '  # TODO - i10n
        self.feedback_prefix = read_stripped_lines(
            join(dirname(__file__), 'dialog', self.lang,
                 'FeedbackPrefix.dialog'))
        self.feedback_search = read_stripped_lines(
            join(dirname(__file__), 'dialog', self.lang,
                 'FeedbackSearch.dialog'))

    def initialize(self):
        intent = IntentBuilder("WikipediaIntent").require(
            "WikipediaKeyword").require("ArticleTitle").build()
        self.register_intent(intent, self.handle_intent)
        self.emitter.on("wikipedia.request", self.handle_ask_wikipedia)
        test_intent = IntentBuilder("TestWikipediaIntent") \
            .require("testp").require("Subject").build()
        self.register_intent(test_intent, self.handle_ask_wikipedia)

    def handle_intent(self, message):
        try:
            title = message.data.get("ArticleTitle")
            self.__feedback_search(title)
            results = wiki.search(title, self.max_results)
            summary = re.sub(
                r'\([^)]*\)|/[^/]*/', '',
                wiki.summary(results[0], self.max_phrases))
            self.speak(summary)

        except wiki.exceptions.DisambiguationError as e:
            options = e.options[:self.max_results]
            self.log.debug("Multiple options found: " + ', '.join(options))
            self.__ask_more_about(options)

        except Exception as e:
            self.log.error("Error: {0}".format(e))

    def __feedback_search(self, title):
        prefix = self.feedback_prefix[randrange(len(self.feedback_prefix))]
        feedback = self.feedback_search[randrange(len(self.feedback_search))]
        sentence = feedback.replace('<prefix>', prefix).replace(
            '<title>', title)
        self.context["more_speech"] = True
        self.speak(sentence)

    def __ask_more_about(self, opts):
        sentence = self.question
        size = len(opts)

        for idx, opt in enumerate(opts):
            sentence += opt

            if idx < size - 2:
                sentence += ', '
            elif idx < size - 1:
                sentence += ' or '  # TODO - i10n

        self.speak(sentence)

    def handle_ask_wikipedia(self, message):
        node = message.data.get("Subject")
        result = self.adquire(node)
        self.speak(str(result))
        self.emitter.emit(Message("wikipedia.result", result, self.context))

    def adquire(self, subject):
        logger.info('WikipediaKnowledge_Adquire')
        dict = {}
        if subject is None:
            logger.error("No subject to adquire knowledge about")
        else:

            node_data = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                page = wptools.page(subject, silent=True,
                                    verbose=False).get_query()
                node_data["pic"] = page.image('page')['url']
                node_data["name"] = page.label
                node_data["description"] = page.description
                node_data["summary"] = page.extext
                node_data["url"] = page.url
                # parse infobox
                node_data["infobox"] = self.parse_infobox(subject)
                # id info source
                dict["wikipedia"] = node_data
            except Exception as e:
                try:
                    self.__feedback_search(subject)
                    results = wiki.search(subject, self.max_results)
                    node_data["summay"] = re.sub(
                        r'\([^)]*\)|/[^/]*/', '',
                        wiki.summary(results[0], self.max_phrases))
                    # id info source
                    dict["wikipedia"] = node_data
                except:
                    logger.error(
                        "Could not parse wikipedia for " + str(subject))
        return dict

    def parse_infobox(self, subject):
        page = wptools.page(subject, silent=True, verbose=False).get_parse()
        data = {}
        # TODO decent parsing, info is messy
        for entry in page.infobox:
            # print entry + " : " + page.infobox[entry]
            data[entry] = page.infobox[entry]
        return data


def create_skill():
    return LILACSWikipediaSkill()