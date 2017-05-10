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
from mycroft.util.log import getLogger

import os
import random
import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))
from service_objectives import ObjectiveBuilder

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class TrollObjectiveSkill(MycroftSkill):
    def __init__(self):
        super(TrollObjectiveSkill, self).__init__(name="TrollObjectiveSkill")
        self.reload_skill = False

    def initialize(self):
        self.troll_objective()

    def troll_objective(self):
        objective_name = "troll"
        my_objective = ObjectiveBuilder(objective_name, self.emitter)

        goal_name = "TrollWebsite"
        intent = "LaunchWebsiteIntent"
        intent_params = {"Website": "http://www.helpfeedthetroll.com/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://hackertyper.net/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://theonion.github.io/fartscroll.js/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://www.shitexpress.com/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://fakeupdate.net/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://www.mailaspud.com/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "https://shipyourenemiesglitter.com/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://www.greatbigstuff.com/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://www.whatsfakeapp.com/en/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://sexypranky.com/"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "http://nyanit.com/"}
        my_objective.add_way(goal_name, intent, intent_params)

        goal_name = "TrollVideo"
        intent = "SearchWebsiteIntent"
        intent_params = {"Website": "Youtube", "SearchTerms":"Trololo Video"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "Youtube", "SearchTerms": "arnold schwarzenegger quotes"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "Youtube", "SearchTerms": "narwhals 10 hour"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "Youtube", "SearchTerms": "amazing horse 10 hour"}
        my_objective.add_way(goal_name, intent, intent_params)
        intent_params = {"Website": "Youtube", "SearchTerms": "badgers 10 hour"}
        my_objective.add_way(goal_name, intent, intent_params)

        keyword = "TrollObjectiveKeyword"
        my_objective.require(keyword)
        intent, self.handle_troll_objective = my_objective.build()

        self.register_intent(intent, self.handle_troll_objective)

    def stop(self):
        pass


def create_skill():
    return TrollObjectiveSkill()
