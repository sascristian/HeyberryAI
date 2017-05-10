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


class FacebookObjectiveSkill(MycroftSkill):
    def __init__(self):
        super(FacebookObjectiveSkill, self).__init__(name="FacebookObjectiveSkill")
        self.reload_skill = False

    def initialize(self):
        self.facebook_objective()

    def facebook_objective(self):
        objective_name = "facebook"
        my_objective = ObjectiveBuilder(objective_name, self.emitter)
        goal_probs = {} # probabilitie dict for each goal, from 1 to 100
        goal_name = "SelfmadeContent"
        intent = "FbPoetryIntent"
        my_objective.add_way(goal_name, intent, {})
        intent = "FbJokeIntent"
        my_objective.add_way(goal_name, intent, {})
        intent = "FbDreamIntent"
        #my_objective.add_way(goal_name, intent, {})
        intent = "FbArtIntent"
        #my_objective.add_way(goal_name, intent, {})

        goal_name = "InfoContent"
        intent = "FbArticleIntent"
        my_objective.add_way(goal_name, intent, {})
        intent = "FbBTCIntent"
        my_objective.add_way(goal_name, intent, {})

        goal_name = "MediaContent"
        intent = "FbYoutubeIntent"
        #my_objective.add_way(goal_name, intent, {})
        intent = "FbApodIntent"
        my_objective.add_way(goal_name, intent, {})
        intent = "FbEPICIntent"
        my_objective.add_way(goal_name, intent, {})

        goal_name = "ShitPostingContent"
        intent = "FbTimeIntent"
        #my_objective.add_way(goal_name, intent, {})
        intent = "FbWeatherIntent"
        #my_objective.add_way(goal_name, intent, {})
        intent = "FbProxyIntent"
        #my_objective.add_way(goal_name, intent, {})
        intent = "FbFriendnumberIntent"
        #my_objective.add_way(goal_name, intent, {})

        goal_name = "WebscrappedContent"
        intent = "FbQuoteIntent"
        my_objective.add_way(goal_name, intent, {})
        intent = "FbFactIntent"
        my_objective.add_way(goal_name, intent, {})
        intent = "FbPickupIntent"
        my_objective.add_way(goal_name, intent, {})
        intent = "FbXkcdIntent"
        #my_objective.add_way(goal_name, intent, {})

        keyword = "FacebookObjectiveKeyword"
        my_objective.require(keyword)
        intent, self.handle_facebook_objective = my_objective.build()

        self.register_intent(intent, self.handle_facebook_objective)

    def stop(self):
        pass


def create_skill():
    return FacebookObjectiveSkill()
