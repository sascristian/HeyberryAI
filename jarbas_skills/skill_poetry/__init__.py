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

from os.path import dirname, realpath
import random
import json
import time
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import os

__author__ = 'jarbas'

logger = getLogger(__name__)


class PoetrySkill(MycroftSkill):

    def __init__(self):
        super(PoetrySkill, self).__init__(name="PoetrySkill")
        self.styles = ["blackmetal", "deathmetal","scifi","viking", "shakespeare", "camoes", "family", "friends", "inspirational", "love", "life"]
        self.path = dirname(realpath(__file__))
        if not os.path.exists(self.path+"/results"):
            os.mkdir(self.path+"/results")

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
        path = self.path + "/styles/" + style + ".json"
        chain = MarkovChain(1, pad=False).load(path)
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


START_OF_SEQ = "~"
END_OF_SEQ = "[END]"


class MarkovChain:
    """
    Simple Markov Chain Class
    """

    def __init__(self, order=1, pad=True, records=None):
        """
        Initialise Markov chain
        :param order: int - number of tokens to consider a state
        :param pad: bool - whether to pad training strings with start/end tokens
        """
        self.order = order
        self.pad = pad
        self.records = {} if records is None else records

    def add_tokens(self, tokens):
        """
        Adds a list of tokens to the markov chain

        :param tokens: list of tokens
        :return: None
        """
        if self.pad:
            tokens = [START_OF_SEQ] * self.order + tokens + [END_OF_SEQ]

        for i in range(len(tokens) - self.order):
            current_state = tuple(tokens[i:i + self.order])
            next_state = tokens[i + self.order]
            self.add_state(current_state, next_state)

    def add_state(self, current_state, next_state):
        """
        Updates the weight of the transition from current_state to next_state
        with a single observation.

        :param current_state: tuple - current state
        :param next_state: token - the next observed token
        :return: None
        """
        if current_state not in self.records.keys():
            self.records[current_state] = dict()

        if next_state not in self.records[current_state].keys():
            self.records[current_state][next_state] = 0

        self.records[current_state][next_state] += 1

    def generate_sequence(self, n=100, initial_state=None):
        """
        Generates a sequence of tokens from the markov chain, starting from
        initial_state. If initial state is empty, and pad is false it chooses an
        initial state at random. If pad is true,

        :param n: int - The number of tokens to generate
        :param initial_state: starting state of the generator
        :return: list of generated tokens
        """

        if initial_state is None:
            if self.pad:
                sequence = [START_OF_SEQ] * self.order
            else:
                sequence = list(random.choice(self.records.keys()))
        else:
            sequence = initial_state[:]

        for i in range(n):
            current_state = tuple(sequence[-self.order:])
            next_token = self.sample(current_state)
            sequence.append(next_token)

            if next_token == END_OF_SEQ:
                return sequence

        return sequence

    def sample(self, current_state):
        """
        Generates a random next token, given current_state
        :param current_state: tuple - current_state
        :return: token
        """
        if current_state not in self.records.keys():
            current_state = random.choice(self.records.keys())

        possible_next = self.records[current_state]
        n = sum(possible_next.values())

        m = random.randint(0, n)
        count = 0
        for k, v in possible_next.items():
            count += v
            if m <= count:
                return k

    def save(self, filename):
        """
        Saves Markov chain to filename

        :param filename: string - where to save chain
        :return: None
        """
        with open(filename, "w") as f:
            m = {
                "order": self.order,
                "pad": self.pad,
                "records": {str(k): v for k, v in self.records.items()}
            }
            json.dump(m, f)

    @staticmethod
    def load(filename):
        """
        Loads Markov chain from json file

        DUE TO USE OF EVAL
        DO NOT RUN THIS ON UNTRUSTED FILES

        :param filename:
        :return: MarkovChain
        """
        with open(filename, "r") as f:
            raw = json.load(f)

        mc = MarkovChain(
            raw["order"],
            raw["pad"],
            {eval(k): v for k, v in raw["records"].items()}
        )

        return mc
