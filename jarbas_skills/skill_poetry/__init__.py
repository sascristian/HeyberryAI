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

import random

import os
from adapt.intent import IntentBuilder
from os.path import dirname, realpath

from jarbas_utils.MarkovChains import MarkovChain
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft import MYCROFT_ROOT_PATH

__author__ = 'jarbas'

logger = getLogger(__name__)


class PoetrySkill(MycroftSkill):

    def __init__(self):
        super(PoetrySkill, self).__init__(name="PoetrySkill")
        self.styles = ["blackmetal", "deathmetal","scifi","viking",
                       "shakespeare", "mc_3_w", "mc_5_w", "family", "friends",
                       "inspirational", "love", "life"]
        self.path = dirname(realpath(__file__))
        if not os.path.exists(self.path+"/results"):
            os.mkdir(self.path+"/results")
        self.chain_path = MYCROFT_ROOT_PATH + "/jarbas_models/Markov_Chains/"
        if not os.path.exists(self.chain_path+"/poetry_styles"):
            os.mkdir(self.chain_path+"/poetry_styles")

    def initialize(self):
        # TODO regex style into single intent
        viking_poetry_intent = IntentBuilder("ReciteVikingPoetryIntent") \
            .require("viking").build()
        self.register_intent(viking_poetry_intent,
                             self.handle_viking_poetry_intent)

        gore_poetry_intent = IntentBuilder("ReciteGorePoetryIntent") \
            .require("gore").build()
        self.register_intent(gore_poetry_intent,
                             self.handle_gore_poetry_intent)

        satanic_poetry_intent = IntentBuilder("ReciteSatanicPoetryIntent") \
            .require("satanic").build()
        self.register_intent(satanic_poetry_intent,
                             self.handle_satanic_poetry_intent)

        sci_poetry_intent = IntentBuilder("ReciteSciFiPoetryIntent") \
            .require("science").build()
        self.register_intent(sci_poetry_intent,
                             self.handle_science_poetry_intent)

        poetry_intent = IntentBuilder("RecitePoetryIntent")\
            .require("poetry").optionally("Style").build()
        self.register_intent(poetry_intent,
                             self.handle_poetry_intent)

    def handle_science_poetry_intent(self, message):
        style = "scifi"
        poem = self.poetry(style)
        self.save(style, poem)
        # speak
        self.speak(poem)

    def handle_gore_poetry_intent(self, message):
        style = "deathmetal"
        poem = self.poetry(style)
        self.save(style, poem)
        # speak
        self.speak(poem)

    def handle_viking_poetry_intent(self, message):
        style = "viking"
        poem = self.poetry(style)
        self.save(style, poem)
        # speak
        self.speak(poem)

    def handle_satanic_poetry_intent(self, message):
        style = "blackmetal"
        poem = self.poetry(style)
        self.save(style,poem)
        # speak
        self.speak(poem)

    def handle_poetry_intent(self, message):
        #self.speak_dialog("poetry")
        style = message.data.get("Style", style = random.choice(self.styles))
        poem = self.poetry(style)
        self.save(style, poem)
        # speak
        self.speak(poem)

    def poetry(self, style):
        path = self.chain_path + "/poetry_styles/" + style + ".json"
        i = 2
        # _13_ in name, means order 13
        order = style.find("_")
        if order != -1:
            style = style[order+1:]
            order = style.find("_")
            if order != -1:
                style = style[:order]
        if style.isdigit():
            i = int(style)

        chain = MarkovChain(i, pad=False).load(path)
        generated = chain.generate_sequence()
        poem = ""
        for word in generated:
            poem += word
            if "." in word:
                poem += "\n"
            elif "\n" not in word:
                poem += " "
        # generate poem
        return poem

    def save(self, style, poem):
        # save
        path = self.path + "/results/" + style + "_" + poem[:20] + ".txt"
        wfile = open(path, "w")
        wfile.write(poem)
        wfile.close()

    def stop(self):
        pass


def create_skill():
    return PoetrySkill()