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


from mycroft.skills.core import MycroftSkill

import os
import random

from jarbas_utils.objectives_builder import ObjectiveBuilder

__author__ = 'jarbas'


class WikiObjectiveSkill(MycroftSkill):
    def __init__(self):
        super(WikiObjectiveSkill, self).__init__(name="WikiObjectiveSkill")
        self.word_bank = []
        self.load_word_bank()

    def initialize(self):
        self.wiki_objective()

    def wiki_objective(self):
        objective_name = "wiki"
        my_objective = ObjectiveBuilder(objective_name, self.emitter)

        goal_name = "Search_Wikipedia"
        intent = "WikipediaIntent"
        i = 0
        while i < 1000:
            word = random.choice(self.word_bank)
            intent_params = {"ArticleTitle": word}
            my_objective.add_way(goal_name, intent, intent_params)
            i+=1

        keyword = "WikiObjectiveKeyword"
        my_objective.require(keyword)
        intent, self.handle_wiki_objective = my_objective.build()
        self.register_intent(intent, self.handle_wiki_objective)

    def load_word_bank(self):
        word_bank = []
        path = os.path.dirname(__file__) + '/wordbank.txt'
        with open(path) as f:
            words = f.readlines()
            for word in words:
                word_bank.append(word.replace("\n", ""))

        self.word_bank = word_bank

    def stop(self):
        pass


def create_skill():
    return WikiObjectiveSkill()
