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
from jarbas_utils.objectives_builder import ObjectiveBuilder
from jarbas_utils.skill_tools import DeepDreamQuery
from jarbas_utils.art import psy_art
from os.path import dirname
import random
from adapt.intent import IntentBuilder

__author__ = 'jarbas'


class DreamBotSkill(MycroftSkill):
    def __init__(self):
        super(DreamBotSkill, self).__init__()
        self.time = 60 * 1  # 1 minute
        self.reload_skill = False
        self.external_reload = False
        self.external_shutdown = False
        self.dreamer = None

    def initialize(self):
        # start dreamer
        self.dreamer = DeepDreamQuery(self.name, self.emitter)
        # register intents
        intent = IntentBuilder("DreamBotIntent").require("DreamBotKeyword") \
            .optionally("url").build()
        self.register_intent(intent, self.handle_dream_intent)

        intent = IntentBuilder("RecursiveDreamBotIntent").require(
            "DreamBotKeyword").require("RecursiveKeyword") \
            .optionally("url").build()
        self.register_intent(intent, self.handle_recursive_dream_intent)

        intent = IntentBuilder("PureDreamBotIntent").require(
            "DreamBotKeyword").require("PureKeyword")
        self.register_intent(intent, self.handle_pure_dream_intent)

        # register objective
        self.dream_bot_objective()

    def dream_bot_objective(self):
        objective_name = "DreamBot"
        my_objective = ObjectiveBuilder(objective_name, self.emitter)

        # dream. zoom and dream...
        goal_name = "Recursive Dream"
        intent = "RecursiveDreamBotIntent"
        intent_params = {}
        my_objective.add_way(goal_name, intent, intent_params)

        # dream on random picture
        goal_name = "Dream"
        intent = "DreamBotIntent"
        url = "https://unsplash.it/600/?random"
        intent_params = {"url": url}
        my_objective.add_way(goal_name, intent, intent_params)

        # dream on self generated picture
        goal_name = "PureDream"
        intent = "PureDreamBotIntent"
        intent_params = {}
        my_objective.add_way(goal_name, intent, intent_params)

        keyword = "DreamBotObjectiveKeyword"
        my_objective.require(keyword)
        intent, self.handle_dreambot_objective = my_objective.build()
        self.register_intent(intent, self.handle_dreambot_objective)

        my_objective.add_timer(self.time * 60)  # hours

    def handle_dream_intent(self, message):
        self.speak("dreambot activated")
        url = message.data.get("url", "https://unsplash.it/600/?random")
        file = self.dreamer.dream_from_url(picture_url=url)
        result_dict = self.dreamer.result
        return result_dict

    def handle_recursive_dream_intent(self, message):
        # TODO zoom
        result = self.handle_dream_intent(message)
        message.data["url"] = result.get("dream_url")
        if message.data["url"]:
            self.speak("dreaming on dream")
            result = self.handle_dream_intent(message)
            message.data["url"] = result.get("dream_url")
            if message.data["url"]:
                self.speak("dreaming on dream")
                result = self.handle_dream_intent(message)

    def handle_pure_dream_intent(self, message):
        self.speak("dreaming on my own art")
        pictures = psy_art(path=dirname(__file__), name="dream_seed", numPics=3)
        file = self.dreamer.dream_from_file(
            picture_path=random.choice(pictures))
        result_dict = self.dreamer.result
        return result_dict

    def stop(self):
        pass


def create_skill():
    return DreamBotSkill()
