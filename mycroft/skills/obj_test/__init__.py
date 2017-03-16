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
from mycroft.skills.objective_skill import ObjectiveBuilder


__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class TestRegisterObjectiveSkill(MycroftSkill):
    def __init__(self):
        super(TestRegisterObjectiveSkill, self).__init__(name="TestRegisterObjectiveSkill")

    def initialize(self):

        # objective name
        name = "test"
        my_objective = ObjectiveBuilder(name, self.emitter)

        # create way
        goal = "test this shit"
        intent = "speak"
        intent_params = {"utterance":"this is test"}
        # register way for goal
        # if goal doesnt exist its created
        my_objective.add_way(goal, intent, intent_params)

        # do my_objective.add_way() as many times as needed for as many goals as desired
        intent = "speak"
        intent_params = {"utterance": "testing alright"}
        my_objective.add_way(goal, intent, intent_params)
        # if you dont register any way you will always get a no such objective error
        # if you register too much ways (10) adapt seems to crash and no utterance is handled in intent skill

        # get objective intent and handler

        # get an intent to execute this objective by its name
        # intent , self.handler = my_objective.get_objective_intent()

        # instead of name to trigger objective lets register a keyword from voc
        keyword = "TestKeyword" # same as doing .require(keyword) in intent
        intent, self.handler = my_objective.get_objective_intent(keyword)

        # objective can still be executed without registering intent by saying
        # objective objective_name and directly using objective skill

        self.register_intent(intent, self.handler)

    def stop(self):
        pass


def create_skill():
    return TestRegisterObjectiveSkill()
