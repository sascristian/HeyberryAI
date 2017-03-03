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

sys.path.append(abspath(dirname(__file__)))

logger = getLogger(abspath(__file__).split('/')[-2])

__author__ = 'jarbas'

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
            old_goals = self.objectives[name]
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

    def default_select(self, goal_list):
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

    def initialize(self):

        self.obj = Objectives(self.emitter)

        self.load_objectives_from_config()

        self.emitter.on("Register_Objective", self.register_objective)

        self.wiki_objective()

        self.obj.print_objectives()

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
        try:
            self.obj.execute_objective(objective)
            ### TODO abstract this with probabilities for each goal and way
        except:
            self.speak("No such objective")

    def handle_available_objectives(self, message):
        self.speak("The following objectives are registered")
        for obj in self.obj.objectives:
            self.speak(obj)

    ### example coded objectives
    # more available in freewill service
    def wiki_objective(self):

        word_bank = self.load_word_bank()

        name = "WikipediaIntent"
        waylist = []
        goals = {}
        g = []
        for word in word_bank:
            ways = {}  # list dumb
            ways.setdefault(name, {"ArticleTitle": word})
            waylist.append(ways)

        name = "Search_Wikipedia" #goal name
        goals.setdefault(name, waylist)
        g.append(Goal(name,waylist))

        name = "wiki" #objective name to invoke for executing

        # you can do this from inside this skill as long as goals is a list
        self.obj.register_objective(name, g)
        # or from any other skill you can do this, goals is a dict
        #self.emitter.emit(Message("Register_Objective", {"name":name,"goals":goals}))

        name = "KnowledgeIntent"
        waylist = []
        g = []
        for word in word_bank:
            ways = {}
            ways.setdefault(name, {"ArticleTitle": word})
            waylist.append(ways)

        name = "Search_Wikipedia"
        g.append(Goal(name, waylist))

        name = "AdquireKnowledge"
        self.obj.register_objective(name, g)

    def load_word_bank(self):
        word_bank = []
        path = os.path.dirname(__file__) + '/wordbank.txt'
        with open(path) as f:
            words = f.readlines()
            for word in words:
                word_bank.append(word.replace("\n", ""))

        return word_bank

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
