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
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.skills.skill_intents import SkillIntents
from mycroft.skills.displayservice import DisplayService
from mycroft.skills.audioservice import AudioService
from mycroft.skills.objectives import ObjectiveBuilder


__author__ = 'jarbas'

logger = getLogger(__name__)


class TemplateSkill(MycroftSkill):

    def __init__(self):
        super(TemplateSkill, self).__init__(name="TemplateSkill")
        # initialize your variables
        self.flag = False

    def initialize(self):
        # initialize display service
        self.display_service = DisplayService(self.emitter)

        # initialize audio service
        self.audio_service = AudioService(self.emitter)

        # initialize self intent parser
        self.intents = SkillIntents(self.emitter)

        # register global intents
        enable_second_intent = IntentBuilder("FirstIntent")\
            .require("FirstKeyword").build()

        self.register_intent(enable_second_intent,
                             self.handle_enable_second_intent)

        # register self-intents
        self_intent = IntentBuilder("SecondIntent") \
            .require("SecondKeyword").build()

        self.register_self_intent(self_intent,
                                  self.handle_second_intent)
        # disable until needed
        self.disable_intent("SelfIntent")

        # build objectives
        name = "test objective"
        my_objective = ObjectiveBuilder(name)

        # create goals and ways
        goal = "test this shit"
        intent = "SpeakIntent"
        intent_params = {"Words": "this is test"}
        # register way for goal
        # do my_objective.add_way() as many times as needed for as many goals as desired
        my_objective.add_way(goal, intent, intent_params)

        # get objective intent and handler
        # required keywords same as doing .require(keyword) in intent
        # no keyword uses objective name as keyword
        keyword = "TestKeyword"
        intent, self.handler = my_objective.get_objective_intent(keyword)
        # register intent to execute objective by keyword
        self.register_intent(intent, self.handler)

    def handle_result_intent(self, message):
        # do stuff and get results
        result = "Sucess string"
        # prepare data to be emitted to message bus to be consumed somewhere else
        self.add_result("String", result)
        # this emits a message for listeners to register messages of the type {"String_result": data} message
        # saves results as data to emit when asked
        # Do more stuff
        result2 = "Evil String"
        self.add_result("Evil_String", result2)
        # emit results from the skills when finished doing stuff
        # this emits and clears results list
        self.emit_results()
        # in this case emits
        #{"String_result": "Sucess string"}
        #{"Evil_String_result": "Evil string}





    def handle_pic_intent(self, message):
        pic_path = "path to picture"
        utterance = "used for backend name parsing"
        self.display_service.show(pic_path, utterance)

    def handle_sound_intent(self, message):
        sound_path = "path to sound file"
        utterance = "used for backend name parsing"
        # list of soundtracks
        self.audio_service.play([sound_path], utterance)

    def handle_enable_second_intent(self, message):
        # do stuff
        # enable secondary intent
        self.enable_self_intent("SecondIntent")
        # disable self until needed
        self.disable_intent("FirstIntent")

    def handle_second_intent(self, message):
        # do stuff
        # disable self after executing
        self.disable_intent("SecondIntent")
        # enable parent intent again
        self.enable_intent("FirstIntent")

    def stop(self):
        # disable secondary intents
        self.disable_intent("SecondIntent")
        # re-enable global intents
        self.enable_intent("FirstIntent")

    def converse(self, transcript, lang="en-us"):
        # determine self intent from transcript
        determined, intent = self.intents.determine_intent(transcript)
        handled = False
        # try to handle intent if it was sucefully determined
        if determined:
            handled = self.intents.execute_intent()

        # check if it was handled
        if not handled:
            # de-register secondary intents here if you want a conditional chain
            self.disable_intent("SecondIntent")
            # in here handle the utterance if it doesnt trigger a self intent
            if self.flag:
                # keep listening without wakeword
                self.speak("handle utterance manually here", expect_response=True)
                return True

        # tell intent skill if you handled intent
        return handled

    def feedback(self, feedback, lang):
        if feedback == "positive":
            # do stuff on positive reinforcement words intent
            # objectives use this to adjust probabilities
            pass
        elif feedback == "negative":
            # do stuff on negative reinforcement words intent
            # objectives use this to adjust probabilities
            pass


def create_skill():
    return TemplateSkill()