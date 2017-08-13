from mycroft.skills.core import MycroftSkill
from adapt.intent import IntentBuilder
from mycroft.util.log import getLogger

from jarbas_utils.objectives_builder import ObjectivesManager
from mycroft.skills.intent_service import IntentParser


logger = getLogger("Objectives Skill")

__author__ = 'jarbas'


class ObjectivesSkill(MycroftSkill):
    def __init__(self):
        super(ObjectivesSkill, self).__init__(name='ObjectivesSkill')
        self.reload_skill = False
        # reward on feedback messages, from 0 to 100
        # TODO read from config
        self.way_reward = 4
        self.goal_reward = 1

    def initialize(self):

        self.manager = ObjectivesManager(self.emitter)
        self.parser = IntentParser(self.emitter)
        self.emitter.on("register_objective", self.register_objective)
        self.emitter.on("execute_objective", self.handle_execute_objective_intent)
        self.emitter.on("objective.executed",
                        self.handle_set_on_top_active_list)
        prefixes = [
            'Objective', 'obj']
        self.__register_prefixed_regex(prefixes, "(?P<Objective>.*)")

        execute_objective_intent = IntentBuilder("ExecuteObjectiveIntent"). \
            require("Objective").build()

        self.register_intent(execute_objective_intent, self.handle_execute_objective_intent)

        available_objectives_intent = IntentBuilder("AvailableObjectivesIntent"). \
            require("ObjectiveKeyword").build()

        self.register_intent(available_objectives_intent, self.handle_available_objectives)

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    def save_weights(self, objective_name=None):
        if objective_name is not None:
            for objective in self.manager.objectives:
                if objective.name == objective_name:
                    # save probs
                    goal_weights = objective.goal_weights
                    way_weights = objective.way_weights
                    self.settings[objective.name] = {"goal_weights": goal_weights, "way_weights": way_weights}
                    self.settings.store()
                    return True
        else: # save all
            for objective in self.manager.objectives:
                # save probs
                goal_weights = objective.goal_weights
                way_weights = objective.way_weights
                self.settings[objective.name] = {"goal_weights": goal_weights, "way_weights": way_weights}
                self.settings.store()
            return True
        return False

    def handle_execute_objective_intent(self, message):
        objective = message.data.get("Objective")
        try:
            self.manager.execute_objective(objective)
        except:
            # TODO id error
            self.speak("No such objective")

    def handle_available_objectives(self, message):
        self.speak_dialog("available_objectives")
        for obj in self.manager.objectives:
            self.speak(obj.name)

    def handle_set_on_top_active_list(self):
        # all objectives registered will be taken as coming from objective skill
        # this is because of feedback messages
        # dummy intent just to bump objectives to top of active skill list
        # called in execute objective function
        self.make_active()

    def register_objective(self, message):
        name = message.data["name"]
        goals = message.data["goals"]
        ways = message.data["ways"]
        try:
            goal_weights = self.settings[name]["goal_weights"]
        except:
            goal_weights = message.data["goal_weights"]
        try:
            way_weights = self.settings[name]["way_weights"]
        except:
            way_weights = message.data["way_weights"]
        self.manager.register_objective(name, goals, ways, goal_weights, way_weights)
        self.save_weights(name)

    def feedback(self, feedback):
        if feedback == "positive":
            if self.manager.adjust_goal_weight(ammount= self.goal_reward, increase=True):
                self.speak("Increasing weight of last executed goal by " + str(self.goal_reward))
            if self.manager.adjust_way_weight(ammount=self.way_reward, increase = True):
                self.speak("Increasing weight of last executed way by " + str(self.way_reward))
        elif feedback == "negative":
            if self.manager.adjust_goal_weight(ammount=self.goal_reward, increase=False):
                self.speak("Decreasing weight of last executed goal by " + str(self.goal_reward))
            if self.manager.adjust_way_weight(ammount=self.way_reward, increase = False):
                self.speak("Decreasing weight of last executed way by " + str(self.way_reward))
        self.save_weights()

    def converse(self, utterances, lang="en-us"):
        # check if some of the intents will be handled
        intent, id = self.parser.determine_intent(utterances[0])
        if intent == "PositiveFeedbackIntent":
            self.feedback("positive")
            return True
        elif intent == "NegativeFeedbackIntent":
            self.feedback("negative")
            return True
        return False

    def stop(self):
        pass


def create_skill():
    return ObjectivesSkill()
