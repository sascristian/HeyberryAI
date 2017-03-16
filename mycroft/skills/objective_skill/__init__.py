import sys
from os.path import abspath

from mycroft.skills.core import MycroftSkill
from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message
from mycroft.configuration import ConfigurationManager

import random
import os

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
            sleep(1)  # wait for connect
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
    def __init__(self, name, ways):
        self.name = name#"knowledge"
        self.ways = ways#["wikipedia", "wolphram", "articles", "ask user"]

    def way_selector(self, function=None):
        if function is not None:
            return function(self.ways)
        else:
            return self.default_way_selector(self.ways)

    def default_way_selector(self, ways):
        selected_way = random.choice(ways)
        for key in selected_way:
            #selected_way = way
            data = selected_way[key]
            return selected_way , data, key

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

    def register_objective(self, name, goals=None):
        try:  # if key exists in dict
            old_goals = self.objectives[name.lower()]
            for goal in old_goals:
                goals.append(goal)  # load previously defined goals
            self.objectives[name.lower()] = goals
        except:#doesnt exit, register
            self.objectives.setdefault(name.lower(), goals)

        data = []
        for goal in goals:
            data.append(goal.name)

        data = {"Name":name,"Goals":data}
        self.client.emit(Message("Objective_Registered", data))

    def execute_objective(self, name, selectfunction=None):
        if selectfunction is None:
            selectfunction = self.default_select
        intent , data, key, goal = selectfunction(self.objectives[name])

        print "\nExecuting\n"
        print "objective: "+name
        print "Goal: " + goal
        print "way: " + str(key)
        print "way data :"+str(data)

        self.client.emit(Message(key, data))

        return intent

    def default_select(self, goal_list):#
        selected_goal = random.choice(goal_list)
        intent , data, key  = selected_goal.way_selector()
        return intent, data, key, selected_goal.name

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

    def initialize(self):

        self.obj = Objectives(self.emitter)

        self.load_objectives_from_config()

        self.emitter.on("Register_Objective", self.register_objective)
        self.emitter.on("Execute_Objective", self.handle_execute_objective_intent)

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

    def handle_execute_objective_intent(self, message):
        objective = message.data.get("Objective")
        #objective.replace(" ","_")
        try:
            self.obj.execute_objective(objective)
            ### TODO abstract this with probabilities for each goal and way
        except:
            self.speak("No such objective")

    def handle_available_objectives(self, message):
        self.speak("The following objectives are registered")
        for obj in self.obj.objectives:
            self.speak(obj)


    ####### objectives #####

    def load_objectives_from_config(self):
        objectives = ConfigurationManager.get([dirname(__file__)+"/objectives.conf"])[
            "Objectives"]
        for objective in objectives:
            # print objective
            goals = []
            for goal in objectives[objective]:
                name = goal
                ways_string = objectives[objective][goal]["ways"]
                # print ways_string

                waylist = []
                for intent in ways_string:
                    # print intent
                    for key in intent:
                        # print key
                        # print intent[key]
                        ways = {}
                        ways.setdefault(key, intent[key])
                        waylist.append(ways)

                goal = Goal(name, waylist)
                goals.append(goal)

            self.obj.register_objective(objective, goals)

    def register_objective(self, message):
        name = message.data["name"]
        goals = message.data["goals"]
        goalis = []
        for goal in goals:
            g = Goal(goal, goals[goal])
            goalis.append(g)
        self.obj.register_objective(name, goalis)

def create_skill():
    return ObjectivesSkill()
