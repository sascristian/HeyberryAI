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
import re
import os

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from os.path import dirname
import time
__author__ = 'jarbas'

logger = getLogger(__name__)

class MarkovGen():
    def __init__(self):
        self.mode = 1
        self.minsize = 8
        self.maxsize = 20
        self.freqDict = {}
        self.banned = ["coke", " k ", "snort", "ganja", "serotonine", "ketamine", "k-hole","norepinephrine", "dopamine", "reuptake", "psilo", "hallucinating", "bismol", "marijuana", "dxm", "tab", "drug", "chemical", "dope", "kush", "acid", "peyote", "hallucinogen", " m ","smoked", "engine", "tabitha", "mescaline", "harmala", "cevs", "peak", "substance", "smok","trip","psychedelic", "mdma", "phenethylamine", "visual", "cannabis", "weed", "drug", "lsd", "dmt", "mushroom", "maoi", "jurema", "heroin",
                  "stash", "2-cb", "2c-b", "2cb", " mg", "0ug", " g ", "shrooms", "crack"]
        self.replaces = ["memorie", "jon do", "engine", "friend", "computing power", "super-computer", "galactic council","gnome", "pod bay doors", "tricorder", "alien goo", "flux capacitator","dinosaur turd", "space ship", "computer", "bot", "evil", "AI", "synthetic", "alien",
                       "pink-skin human", "data", "metadata", "robo-orc", "time-machine", "medkit", "terminator", "Mark1", "radioactive poop", "waste"]

    def replace_bads(self, text):
        lines = text
        for w in text:
            for word in self.banned:
                lines = lines.replace(word, random.choice(self.replaces))
        return lines.replace("[t+", "").replace("]", "")

    def add_to_dict(self, fileName):
        f = open(fileName, 'r')
        # phrases
        if self.mode == 1:
            lines = re.sub("\n", " \n", f.read()).lower().replace(".", "\n").split('\n')
        else:
            lines = re.sub("\n", " \n", f.read()).lower().split(' ')
        # count frequencies curr -> succ
        for curr, succ in zip(lines[1:], lines[:-1]):
            # check if curr is already in the dict of dicts
            if curr not in self.freqDict:
                self.freqDict[curr] = {succ: 1}
            else:
                # check if the dict associated with curr already has succ
                if succ not in self.freqDict[curr]:
                    self.freqDict[curr][succ] = 1;
                else:
                    self.freqDict[curr][succ] += 1;

        # compute percentages
        probDict = {}
        for curr, currDict in self.freqDict.items():
            probDict[curr] = {}
            currTotal = sum(currDict.values())
            for succ in currDict:
                probDict[curr][succ] = currDict[succ] / currTotal
        self.freqDict = probDict

    def markov_next(self,  curr):
        probDict = self.freqDict
        if curr not in probDict:
            return random.choice(list(probDict.keys()))
        else:
            succProbs = probDict[curr]
            randProb = random.random()
            currProb = 0.0
            for succ in succProbs:
                currProb += succProbs[succ]
                if randProb <= currProb:
                    return succ
            return random.choice(list(probDict.keys()))

    def generate(self, curr):
        if self.mode == 1:
            T = random.choice(range(self.minsize, self.maxsize))
        else:
            T = random.choice(range(self.minsize*20, self.maxsize*5))
        generated = [curr]
        for t in range(T):
            next = self.markov_next(generated[-1])
            if len(next)>3:
                generated.append(next)
                if self.mode == 1:
                    generated.append("\n")
        generated = " ".join(generated)
        return self.replace_bads(generated)

class StorySkill(MycroftSkill):

    def __init__(self):
        super(StorySkill, self).__init__(name="StorySkill")
        self.reload_skill = False
        self.styles = ["lovecraft", "drugs", "sci_fi"]
        self.starts = ["Once upon a time in a place far far away, ",
          "The story im about to tell is unbelievable, ",
          "Everything started like this, ",
          "In the land of fantasy, things are never normal.",
          "These are the voyages of a strange mind."]
        try:
            self.path = self.config_core["database_path"] + "/storys"
        except:
            self.path = self.config["save_path"]
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def initialize(self):
        story_intent = IntentBuilder("StoryIntent")\
            .require("story").build()
        self.register_intent(story_intent,
                             self.handle_story_intent)

    def handle_story_intent(self, message):
        style = random.choice(self.styles)
        Mark = MarkovGen()
        Mark.add_to_dict(dirname(__file__) + "/styles/" + style + ".txt")
        out = Mark.generate(random.choice(self.starts))
        self.save(out)
        # speak
        self.speak(out)

    def save(self, poem):
        # save
        path = self.path + "/" + time.asctime() + ".txt"
        wfile = open(path, "w")
        wfile.write(poem)
        wfile.close()

    def stop(self):
        pass


def create_skill():
    return StorySkill()

