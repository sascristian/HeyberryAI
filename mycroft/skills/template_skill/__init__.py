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

from mycroft.skills.intent_parser import IntentParser, IntentTree
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
        self.intent_parser = IntentParser(self.emitter)
        # register intents
        self.build_intents()
        # register objectives
        self.build_objectives()
        # make tree
        self.build_intent_tree()

    def build_intent_tree(self):
        layers = [["FirstIntent"], ["SecondIntent"]]
        timer_timeout_in_seconds = 60
        self.tree = IntentTree(self.emitter, layers, timer_timeout_in_seconds)
        # not sure where to put this in core, should be in initialize of every skill
        self.emitter.on('enable_intent', self.handle_enable_intent)

    def build_intents(self):
        # build
        enable_second_intent = IntentBuilder("FirstIntent") \
            .require("FirstKeyword").build()
        second_intent = IntentBuilder("SecondIntent") \
            .require("SecondKeyword").build()

        # register in intent skill
        self.register_intent(enable_second_intent,
                             self.handle_enable_second_intent)
        self.register_intent(second_intent,
                             self.handle_second_intent)

        #register in self-parser
        self.intent_parser.register_intent(enable_second_intent.__dict__)
        self.intent_parser.register_intent(second_intent.__dict__)

    def build_objectives(self):
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
        # if wanted register in self-parser
        self.intent_parser.register_intent(intent.__dict__)

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
        utterance = "used for backend name parsing, get from message or spoof"
        self.display_service.show(pic_path, utterance)

    def handle_sound_intent(self, message):
        sound_path = "path to sound file"
        sound_path_two = "path to sound file 2"
        # list of sound files / playlist
        playlist = [sound_path, sound_path_two]
        utterance = "used for backend name parsing, get from message or spoof"
        self.audio_service.play(playlist, utterance)

    def handle_enable_second_intent(self, message):
        # do stuff
        # climb intent tree
        self.tree.next()

    def handle_second_intent(self, message):
        # do stuff
        # go back to level one or next or previous...
        self.tree.reset()

    def stop(self):
        # reset intents to start-up state if desired
        self.tree.reset()

    def converse(self, transcript, lang="en-us"):
        # determine self intent from transcript
        determined, intent = self.intent_parser.determine_intent(transcript)
        if not determined:
            # check for any conditions
            # wrong sequence entry
            self.tree.reset()
            # in here handle the utterance if it doesnt trigger a self intent
            if self.flag:
                # keep listening without wakeword
                self.speak("handle utterance manually here", expect_response=True)
                return True

        # tell intent skill if you handled intent
        return False

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