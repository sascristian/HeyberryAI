
# TODO make reward configurable per objective
# TODO make probs readable from config

import shelve

import sys
from os.path import abspath

from mycroft.skills.core import MycroftSkill
from adapt.intent import IntentBuilder
from mycroft.configuration import ConfigurationManager

import random

from os.path import dirname
from mycroft.util.log import getLogger

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message

from threading import Thread

from time import sleep

sys.path.append(abspath(dirname(__file__)))

logger = getLogger(abspath(__file__).split('/')[-2])

__author__ = 'jarbas'

client = None


def connect():
    global client
    client.run_forever()

class ObjectiveBuilder():
    def __init__(self, objective_name, emitter = None):
        self.goals = {}
        self.objective_name = objective_name
        self.objective = self.objective_name , self.goals

        global client
        if emitter is None:
            client = WebsocketClient()
            event_thread = Thread(target=connect)
            event_thread.setDaemon(True)
            event_thread.start()
            sleep(1)  # wait for connectr
        else:
            client = emitter

    def add_goal(self, goal_name):
        for goal in self.goals:
            if goal == goal_name:
                return
        self.goals.setdefault(goal_name, [])

    def add_way(self, goal_name, intent_name, params=None):
        # add goal if it doesnt exist
        self.add_goal(goal_name)

        # build way
        if params is None:
            params = {}
        goal_way = {intent_name: params}

        # update goal
        for way in self.goals[goal_name]:
            if way == goal_way:
                #way already registered
                return
        self.goals[goal_name].append(goal_way)

    def build(self):
        self.objective = self.objective_name, self.goals

    def reset(self, objective_name):
        self.goals = {}
        self.objective_name = objective_name
        self.objective = self.objective_name, self.goals

    def get_objective_intent(self, keyword = None):
        self.build()
        objective_name , goals = self.objective
        objective_keyword = objective_name + "ObjectiveKeyword"
        objective_intent_name = objective_name + "ObjectiveIntent"

        # Register_Objective
        client.emit(Message("Register_Objective", {"name": objective_name, "goals": goals}))

        # Register intent
        objective_intent = IntentBuilder(objective_intent_name)
        if keyword is None:
            # register vocab for objective intent with objective name
            client.emit(Message("register_vocab", {'start': objective_name, 'end': objective_keyword}))
            # Create intent for objective
            objective_intent.require(objective_keyword)
        else:
            objective_intent.require(keyword)
        objective_intent.build()

        # return objective intent and handler
        return objective_intent, self.execute_objective

    # handler to execute objective
    def execute_objective(self, message):
        client.emit(Message("Execute_Objective", {"Objective": self.objective_name}))


class Goal():
    def __init__(self, name, ways, probs = None):

        self.path = dirname(__file__)+"/probs/"+name+".goalprob"
        self.name = name#"knowledge"
        self.ways = ways#[{"wikipedia":{"ArticleTitle":article}}]

        # build id_to way dict
        self.id_to_way = {} #id:way_dict
        id = 0
        for way in self.ways:
            id+=1
            self.id_to_way.setdefault(id, way)

        # build way probability dict
        self.way_prob_dict = {}  # way_id : prob from 0 to 100

        if probs is None:
            self.set_default_probs()
        else:
            self.way_prob_dict = probs

        # last executed way
        self.last_way = None

    def way_selector(self, function=None):
        if function is not None:
            return function(self.ways)
        else:
            return self.default_way_selector(self.ways)

    def set_default_probs(self):
        try:
            self.read_probs_from_disk()
        except:
            num_ways = len(self.ways)
            prob = 100 / num_ways
            if prob == 0:
                prob = 1
            for id in self.id_to_way:
                self.way_prob_dict.setdefault(id, prob)
            self.save_probs_to_disk()

    def adjust_way_prob(self, ammount = 0, increase = True, way_id=None):

        if ammount > 100 or ammount <=0:
            # TODO logs
            return

        if way_id is None:
            way_id = self.last_way

        size = len(self.way_prob_dict)
        if size == 1 or size == 0:
            size = 2
        # distribute ammount for all other way probabilities
        ammount_to_distribute = ammount / (size - 1)

        # calculate new prob for way_id
        if increase:
            ammount = self.way_prob_dict[way_id] + ammount
        else:
            ammount = self.way_prob_dict[way_id] - ammount

        # set new probability for all
        for id in self.way_prob_dict:
            if increase:
                self.way_prob_dict[id] -= ammount_to_distribute
            else:
                self.way_prob_dict[id] += ammount_to_distribute

        # set new probability for way_id
        if ammount > 100:
            ammount = 100
        elif ammount < 0:
            ammount = 0
        self.way_prob_dict[way_id] = ammount
        self.save_probs_to_disk()

    def read_probs_from_disk(self):
        save = shelve.open(self.path, writeback=True)
        self.way_prob_dict = save["way_prob_dict"]
        save.close()

    def save_probs_to_disk(self):
        save = shelve.open(self.path, writeback=True)
        save["way_prob_dict"] = self.way_prob_dict
        save.sync()
        save.close()

    def default_way_selector(self, ways):

        # produce a list with weighted ocurrences of ways
        list = [k for k in self.way_prob_dict for dummy in range(self.way_prob_dict[k])]

        # get a random way from weighted list
        selected_way_id = random.choice(list)
        selected_way = self.id_to_way[selected_way_id]

        key = None
        data = None
        for key in selected_way:
            data = selected_way[key]
            key = key
        # TODO error handling if key / data is none

        self.last_way = selected_way_id
        way_prob = self.way_prob_dict[selected_way_id]

        return selected_way , data, key, selected_way_id, way_prob

    def print_ways(self):
        i = 0
        if len(self.ways)>20:
            print "Warning, lots of ways, printing first 20"
        for way in self.ways:
            print way
            i+=1
            if i>= 20:
                break



class Objectives():
    def __init__(self, client):
        self.objectives = {} #name : [Goals]
        self.client = client
        self.last_way = None
        self.last_goal = None

        # build way probability dict
        self.goal_prob_dict = {}  # obj name - goal_name : prob from 0 to 100
        self.id_to_goal = {} #goal_id : goal

        self.counter = 0

    def register_objective(self, objective_name, goals=None, probs = None):
        try:  # if key exists in dict
            old_goals = self.objectives[objective_name]
            for goal in old_goals:
                goals.append(goal)  # load previously defined goals
            self.objectives[objective_name] = goals
        except:#doesnt exit, register
            self.objectives.setdefault(objective_name, goals)

        data = []
        for goal in goals:
            data.append(goal.name)
            # build id_to goal dict
            self.counter += 1
            self.id_to_goal.setdefault(self.counter,goal)
            #self.id_to_goal[self.counter] = goal  # id:goal


        data = {"Name":objective_name,"Goals":data}

        if probs is None:
            try:
                self.read_probs_from_disk(objective_name)
            except:
                self.set_default_probs(objective_name)
        else:
            self.goal_prob_dict = probs

        self.client.emit(Message("Objective_Registered", data))

    def execute_objective(self, name, selectfunction=None):
        if selectfunction is None:
            selectfunction = self.default_select
        intent , data, key, goal, way_id, way_prob = selectfunction(self.objectives[name], name)

        print "\n"
        print "objective: "+name
        print "goal: " + goal
        print "goal probability: " + str(self.goal_prob_dict[name][goal])
        print "way_id: " + str(way_id)
        print "way_probability: " + str(way_prob)
        print "way: " + str(key)
        print "way data :"+str(data)
        print "\n"

        self.client.emit(Message(key, data))

        # register objectives skill as last active skill
        # so feedback is processed in this skill
        self.client.emit(Message("recognizer_loop:utterance", {"source":"objectives_skill", "utterances":["bump objectives to active skill list"]}))
        self.last_objective = name
        return intent

    def default_select(self, goal_list, objective_name):
        # choose a goal from list of goal objects

        # create weigthed list for this objective goals only
        goal_prob_dict = self.goal_prob_dict[objective_name]
        list = [k for k in goal_prob_dict for dummy in range(goal_prob_dict[k])]

        # get a random goal from weighted list
        selected_goal_name = random.choice(list)

        # get goal object for selected_goal_name
        selected_goal = None
        for goal in goal_list:
            if goal.name == selected_goal_name:
                selected_goal = goal
                self.last_goal = selected_goal
                break
        # TODO error handling if selected_goal is None
        # select way
        intent, data, key, way_id, way_prob = selected_goal.way_selector()
        self.last_way = way_id
        return intent, data, key, selected_goal.name, way_id, way_prob

    def set_default_probs(self, objective_name):
        num_goals = len(self.objectives[objective_name])
        prob = 100 / num_goals
        if prob == 0:
            prob = 1
        for goal in self.objectives[objective_name]:
            self.goal_prob_dict.setdefault(objective_name, {str(goal.name): prob})
        self.save_probs_to_disk(objective_name)

    def adjust_goal_prob(self, objective_name = None, ammount=0, increase=True, goal=None):

        if objective_name is None:
            objective_name = self.last_objective

        # goal object not name
        if goal is None:
            goal = self.last_goal

        size = len(self.goal_prob_dict[objective_name])
        if size == 1 or size == 0:
            size = 2
        # distribute ammount for all other goal probabilities
        ammount_to_distribute = ammount / (size - 1)
        # calculate new prob
        if increase:
            ammount = self.goal_prob_dict[objective_name][goal.name] + ammount
        else:
            ammount = self.goal_prob_dict[objective_name][goal.name] - ammount

        # set new probability for all
        for id in self.goal_prob_dict[objective_name]:
            if increase:
                self.goal_prob_dict[objective_name][id] -= ammount_to_distribute
            else:
                self.goal_prob_dict[objective_name][id] += ammount_to_distribute

        # set new probability for goal
        if ammount > 100:
            ammount = 100
        elif ammount <= 0:
            ammount = 1
        self.goal_prob_dict[objective_name][goal.name] = ammount
        self.save_probs_to_disk(objective_name)

    def adjust_way_prob(self, ammount, increase= True, goal = None , way = None):
        if way is None:
            if self.last_way is None:
                return
            else:
                way = self.last_way

        if goal is None:
            if self.last_goal is None:
                return
            else:
                goal = self.last_goal
        goal.adjust_way_prob(ammount, increase, way)

    def read_probs_from_disk(self, objective_name):
        path = dirname(__file__) + "/probs/"+objective_name+".objprob"
        save = shelve.open(path, writeback=True)
        self.goal_prob_dict = save["goal_prob_dict"]
        save.close()

    def save_probs_to_disk(self, objective_name):
        path = dirname(__file__) + "/probs/" + objective_name + ".objprob"
        save = shelve.open(path, writeback=True)
        save["goal_prob_dict"] = self.goal_prob_dict
        save.sync()
        save.close()

    def print_objectives(self):
        print "\nAvailable Objectives:\n"
        for objective in self.objectives:
            print objective

    def print_goals(self, objective):
        for goal in self.objectives[objective]:
            print goal.name
            goal.print_ways()


class ObjectivesSkill(MycroftSkill):
    def __init__(self):
        super(ObjectivesSkill, self).__init__(name='ObjectivesSkill')
        self.reload_skill = False
        # reward on feedback messages, from 0 to 100
        self.way_reward = 4
        self.goal_reward = 1

    def initialize(self):

        self.obj = Objectives(self.emitter)

        self.emitter.on("Register_Objective", self.register_objective)
        self.emitter.on("Execute_Objective", self.handle_execute_objective_intent)
        self.emitter.on("objectives_request", self.handle_list_objectives)


        prefixes = [
            'Objective', 'obj']
        self.__register_prefixed_regex(prefixes, "(?P<Objective>.*)")

        execute_objective_intent = IntentBuilder("ExecuteObjectiveIntent"). \
            require("Objective").build()

        self.register_intent(execute_objective_intent, self.handle_execute_objective_intent)

        available_objectives_intent = IntentBuilder("AvailableObjectivesIntent"). \
            require("ObjectiveKeyword").build()

        self.register_intent(available_objectives_intent, self.handle_available_objectives)

        activate_intent = IntentBuilder("ActiveSkillIntent"). \
            require("ActivateKeyword").build()

        self.register_intent(activate_intent, self.handle_set_on_top_active_list())

        self.load_objectives_from_config()

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    def handle_execute_objective_intent(self, message):
        objective = message.data.get("Objective")
        try:
            self.obj.execute_objective(objective)
        except:
            # TODO id error
            self.speak("No such objective")

    def handle_available_objectives(self, message):
        self.speak_dialog("available_objectives")
        for obj in self.obj.objectives:
            self.speak(obj)

    def handle_list_objectives(self, message):
        objs = []
        for obj in self.obj.objectives:
            objs.append(obj)
        self.emitter.emit(Message("objective_listing", {"objectives":objs}))

    def handle_set_on_top_active_list(self):
        # all objectives registered will be taken as coming from objective skill
        # this is because of feedback messages
        # dummy intent just to bump objectives to top of active skill list
        # called in execute objective function
        pass

    def load_objectives_from_config(self):
        objectives = ConfigurationManager.get([dirname(__file__)+"/objectives.conf"])[
            "Objectives"]
        for objective in objectives:
            objective_name = objective
            my_objective = ObjectiveBuilder(objective_name, self.emitter)
            for goal_name in objectives[objective]:
                ways_string = objectives[objective][goal_name]["ways"]
                for intent in ways_string:
                    for intent_name in intent:
                        ways = {}
                        ways.setdefault(intent_name, intent[intent_name])
                        my_objective.add_way(goal_name, intent_name, intent[intent_name])

            # create intent with objective name as vocab
            intent, self.handle_wiki_objective = my_objective.get_objective_intent()
            self.register_intent(intent, self.handle_wiki_objective)

    def register_objective(self, message):
        name = message.data["name"]
        goals = message.data["goals"]
        goalis = []
        for goal in goals:
            g = Goal(goal, goals[goal])
            goalis.append(g)
        self.obj.register_objective(name, goalis)

    def feedback(self, feedback, utterance):
        if feedback == "positive":
            self.obj.adjust_goal_prob(ammount= self.goal_reward, increase=True)
            self.obj.adjust_way_prob(ammount=self.way_reward, increase = True)
        elif feedback == "negative":
            self.obj.adjust_goal_prob(ammount=self.goal_reward, increase=False)
            self.obj.adjust_way_prob(ammount=self.way_reward, increase = False)


def create_skill():
    return ObjectivesSkill()
