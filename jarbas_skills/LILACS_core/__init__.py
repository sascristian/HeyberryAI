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

import random
from time import sleep

import os, sys
from adapt.intent import IntentBuilder
from os.path import dirname
sys.path.append(dirname(__file__))
from concept import ConceptConnector
from crawler import ConceptCrawler
from jarbas_utils.question_parser import LILACSQuestionParser
# import helper questions functions
from questions import *

from jarbas_utils.skill_tools import KnowledgeQuery
from mycroft.util.log import getLogger
from mycroft.skills.core import FallbackSkill
from mycroft.skills.displayservice import DisplayService

logger = getLogger("Skills")

__author__ = "jarbas"


class LilacsCoreSkill(FallbackSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/28
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/blob/dev/lilacs-core.png
    def __init__(self):
        super(LilacsCoreSkill, self).__init__(name="LilacsCoreSkill")
        self.reload_skill = False
        self.connector = None
        self.crawler = None
        self.parser = None
        self.service = None
        self.debug = False

        # number of examples to list
        self.example_num = 5

        self.focus = 20
        # focus = 0 -> think about all nodes
        # focus >15 -> think only of original subject
        # focus <15 -> think only of current subject
        # focus < 10 -> also think about parents and childs of current node

        self.creativity = 0
        # c > 10 -> also think about synonims and antonims of current node
        # focus > 15 -> also get related nodes from wordnik (less objective)
        # focus > 20 -> gets even more nodes from wordnik
        # focus > 25 -> even more nodes from wordnik

        self.answered = False
        self.last_question = ""
        self.last_question_type = ""
        self.last_center = ""
        self.last_target = ""
        self.last_data = {}

    def initialize(self):
        self.display_service = DisplayService(self.emitter, "LILACS")
        self.register_fallback(self.handle_fallback, 0)
        #self.emitter.on("intent_failure", self.handle_fallback)
        self.emitter.on("LILACS_feedback", self.feedback)

        self.parser = LILACSQuestionParser()
        self.service = KnowledgeQuery(self.name, self.emitter)
        self.build_intents()

        self.connector = ConceptConnector(emitter=self.emitter)
        self.create_concepts()
        self.crawler = ConceptCrawler(self.connector)

    def build_intents(self):
        # build intents
        intro_intent = IntentBuilder("IntroduceLILACSIntent") \
            .require("IntroduceKeyword").build()
        nodes_intent = IntentBuilder("ListNodesIntent"). \
            require("nodesKeyword").build()
        focus_intent = IntentBuilder("ListFocusIntent"). \
            require("focusKeyword").build()
        increase_focus_intent = IntentBuilder("IncreaseFocusIntent"). \
            require("focusincreaseKeyword").build()
        decrease_focus_intent = IntentBuilder("DecreaseFocusIntent"). \
            require("focusdecreaseKeyword").build()
        debug_intent = IntentBuilder("ListDebugIntent"). \
            require("debugKeyword").build()
        debug_on_intent = IntentBuilder("DebugOnIntent"). \
            require("debugonKeyword").build()
        debug_off_intent = IntentBuilder("DebugOffIntent"). \
            require("debugoffKeyword").build()

        # register intents
        self.register_intent(intro_intent, self.handle_introduce_intent)
        self.register_intent(nodes_intent, self.handle_list_nodes_intent)
        self.register_intent(focus_intent, self.handle_focus_intent)
        self.register_intent(increase_focus_intent, self.handle_increase_focus_intent)
        self.register_intent(decrease_focus_intent, self.handle_decrease_focus_intent)
        self.register_intent(debug_intent, self.handle_debug_intent)
        self.register_intent(debug_on_intent, self.handle_debug_on_intent)
        self.register_intent(debug_off_intent, self.handle_debug_off_intent)

    # debug methods
    def create_concepts(self):
        # this is just for debug purposes
        if self.debug:
            self.speak("creating standard nodes for debugging")
            name = "human"
            child_concepts = {}
            parent_concepts = {"animal": 2, "mammal": 1}
            self.connector.create_concept(name, parent_concepts=parent_concepts,
                                          child_concepts=child_concepts)

            name = "animal"
            child_concepts = {"frog": 1}
            parent_concepts = {}
            self.connector.create_concept(name, parent_concepts=parent_concepts,
                                          child_concepts=child_concepts)

    def handle_list_nodes_intent(self, message):
        nodes = self.connector.get_concept_names()
        self.speak("the following nodes are in memory")
        if nodes == []:
            self.speak("none")
        else:
            for node in nodes:
                self.speak(node)
                sleep(0.5)

        nodes = os.listdir(dirname(dirname(
            __file__))+"/LILACS_storage/json")
        self.speak("the following nodes are in storage")
        if nodes == []:
            self.speak("none")
            sleep(0.5)
        else:
            for node in nodes:
                self.speak(node.replace(".json",""))

    def handle_focus_intent(self, message):
        # TODO use dialog
        self.speak("Focus is " + str(self.focus))

    def handle_debug_intent(self, message):
        # TODO use dialog
        self.speak("debug is " + str(self.debug))

    def handle_debug_on_intent(self, message):
        # TODO use dialog
        self.speak("debug on")
        self.debug = True

    def handle_debug_off_intent(self, message):
        # TODO use dialog
        self.speak("debug off")
        self.debug = False

    def handle_increase_focus_intent(self, message):
        self.focus += 5
        self.speak("Focus is " + str(self.focus))

    def handle_decrease_focus_intent(self, message):
        self.focus -= 5
        self.speak("Focus is " + str(self.focus))

    # standard intents
    def handle_introduce_intent(self, message):
        self.speak_dialog("whatisLILACS")

    # core methods
    def save_nodes(self, nodes=None):
        if nodes is None:
            nodes = self.connector.get_concept_names()
        saved = []
        for node in nodes:
            if node is None or node in saved or node == "" or node == " ":
                continue
            self.log.info("saving node: " + node)
            if node == "self" or node == "current_user":
                self.connector.save_concept(node, "user")
            else:
                self.connector.save_concept(node)
            saved.append(node)
        if self.debug:
            self.speak("saved nodes: " + str(saved))

    def parse_utterance(self, utterance):
        # get question type from utterance
        center_node, target_node, parents, synonims, midle, \
        parse = self.parser.process_entitys(utterance)
        question = parse.get("QuestionWord", "")
        # differenciate what is {x} from what is {x} of {y}
        target = parse.get("QuestionTargetWord")
        if target:
            # question += "_"+target
            question += "_of"
        tos = ["do", "to", "can"]
        if question == "how" and parse.get("QuestionVerb","") in tos:
            question += "_to"
        if self.debug:
            self.speak(str(parse))
        self.log.info(parse)
        # TODO try to load concepts from storage
        # TODO input relevant nodes in connector
        # TODO update crawler with new nodes
        # TODO save nodes in storage
        return center_node, target_node, parents, synonims, midle, question

    def deduce_answer(self, utterance):
        # try to undestand what user asks
        self.log.info("Deducing answer to: " + utterance)
        try:
            center_node, target_node, parents, synonims, midle, question = \
            self.parse_utterance(utterance)
            # set adapt context for current subject
            self.set_context("CenterNode", center_node)
            self.set_context("TargetNode", target_node)
            self.set_context("RelevantNodes", center_node)
        except Exception as e:
            logger.error(e)
            center_node = ""
            target_node = ""
            question = "unknown"
            parents = {}
            synonims = {}
            midle = []

        # update data for feedback
        self.last_center = center_node
        self.last_target = target_node
        self.last_question = utterance
        self.last_question_type = question
        # TODO maybe add question verb to parser, may be needed for disambiguation between types
        # TODO add more question types
        if self.debug:
            self.speak("Pre-processing of utterance : " + utterance)
            self.speak("question type: " + str(question))
            self.speak("center_node: " + str(center_node))
            self.speak("target_node: " + str(target_node))
            self.speak("parents: " + str(parents))
            self.speak("synonims: " + str(synonims))
            self.speak("related: " + str(midle))
        self.log.info("utterance : " + utterance)
        self.log.info("question type: " + question)
        self.log.info("center_node: " + center_node)
        self.log.info("target_node: " + target_node)
        self.log.info("parents: " + str(parents))
        self.log.info("synonims: " + str(synonims))
        self.log.info("related: " + str(midle))

        if center_node is None or center_node == "":
            self.log.warning("No center node detected, possible parser malfunction")
            if self.debug:
                self.speak("i am not sure what the question is about")

            self.answered = self.handle_learning(utterance)
            return self.answered


        # update nodes in connector
        nodes = [center_node, target_node]
        for node in midle:
            nodes.append(node)
        # load all nodes from memory
        total_nodes = nodes
        for node in parents:
            total_nodes.extend(parents[node])
        for node in synonims:
            total_nodes.append(synonims[node])

        loaded = []
        for node in total_nodes:
            if node is None or node in loaded or node == "" or node == " ":
                continue
            loaded.append(node)
            #if node not in self.connector.get_concept_names():
            self.connector.load_concept(node)

        #nodes += midle
        childs = {}
        antonims = {}
        self.handle_update_connector(nodes, parents, childs, synonims, antonims)

        # try to answer what user asks depending on question type
        self.answered = False
        if question == "what":
            self.answered = self.handle_what_intent(center_node)
        elif question == "how to" or question == "how do i":
            self.answered = self.handle_how_intent(utterance)
        elif question == "who":
            # TODO find a good backend for persons only!
            self.answered = self.handle_who_intent(center_node)
        elif question == "when":
            pass
        elif question == "where":
            pass
        elif question == "why":
            self.answered = self.handle_why(center_node, target_node)
        elif question == "which":
            pass
        elif question == "whose":
            pass
        elif question == "talk" or question == "rant":
            self.answered = self.handle_talk_about(center_node, target_node, utterance)
        elif question == "think" or question == "wonder":
            self.answered = self.handle_think_about(center_node)
        elif question == "in common":
            self.answered = self.handle_relation(center_node, target_node)
        elif question == "is" or question == "are" :
            self.answered = self.handle_compare_intent(center_node, target_node)
        elif question == "examples":
            self.answered = self.handle_examples_intent(center_node)
        elif question == "what_of":
            # TODO finish this, use new crawl strategy
            center_node = center_node + " of " + target_node
            target_node = ""
            #self.answered = self.handle_what_of_intent(center_node)
        # target_node)
        else:# question == "unknown":
            self.answered, answer = self.handle_unknown_intent(utterance)

        self.log.info("answered: " + str(self.answered))
        if self.debug:
            self.speak("answered: " + str(self.answered))

        # if no answer ask user
        if not self.answered:
            self.answered = self.handle_learning(utterance, center_node, True)
            self.log.info("learned: " + str(self.answered))
            if self.debug:
                self.speak("learned: " + str(self.answered))

        try:
            self.save_nodes(total_nodes)
        except Exception as e:
            self.log.error(e)
            if self.debug:
                self.speak(str(e))
        return self.answered

    def handle_update_connector(self, nodes=None, parents=None, childs=None, synonims=None, antonims=None, data=None):
        # nodes = [ node_names ]
        # parents = { node_name: [node_parents] }
        # childs = { node_name: [node_childs] }
        # synonims = { node_name: [node_synonims] }
        # antonims = { node_name: [node_antonims] }
        if nodes is None:
            nodes = []
        if parents is None:
            parents = {}
        if childs is None:
            childs = {}
        if synonims is None:
            synonims = {}
        if antonims is None:
            antonims = {}
        if data is None:
            data = {}
        # create_concept(self, new_concept_name, data={},
        #                   child_concepts={}, parent_concepts={}, synonims=[], antonims=[])


        total_nodes = nodes
        total_nodes.extend(parents.keys())
        total_nodes.extend(childs.keys())
        total_nodes.extend(synonims.keys())
        total_nodes.extend(antonims.keys())

        # make empty nodes
        for node in nodes:
            if node is not None and node != "" and node != " ":
                self.log.info("processing node: " + node)
                self.connector.create_concept(node)
        # make all nodes with parents
        for node in parents:
            self.log.info("processing parents of node: " + node)
            if node is not None and node != "" and node != " ":
                pdict = {}
                for p in parents[node]:
                    self.log.info("parent: " + p)
                    pdict.setdefault(p, 5)  # gen 5 for auto-adquire
                self.connector.create_concept(node, parent_concepts=pdict)
        # make all nodes with childs
        for node in childs:
            self.log.info("processing childs of node: " + node)
            if node is not None and node != "" and node != " ":
                cdict = {}
                for c in childs[node]:
                    self.log.info("child: " + c)
                    cdict.setdefault(c, 5)  # gen 5 for auto-adquire
                self.connector.create_concept(node, child_concepts=cdict)
        # make all nodes with synonims
        for node in synonims:
            self.log.info("processing synonims of node: " + node)
            if node is not None and node != "" and node != " ":
                self.connector.create_concept(node, synonims={synonims[node]:5})
        # make all nodes with antonims
        for node in antonims:
            self.log.info("processing antonims of node: " + node)
            if node is not None and node != "" and node != " ":
                self.connector.create_concept(node, antonims={antonims[node]:5})
        # make all nodes with data
        for node in data:
            self.log.info("processing data of node: " + node)
            if node is not None and node != "" and node != " ":
                self.connector.create_concept(node, data=data[node])

        # update crawler
        #self.save_nodes(total_nodes)
        self.crawler.update_connector(self.connector)
        self.connector.saved = []

    def handle_learning(self, utterance, center_node=None, save=False):
        self.log.info("learning correct answer")
        #self.speak("learning correct answer")
        if self.debug:
            self.speak("Searching wolfram alpha")
        # this is placeholder, always call wolfram, when question type is fully implemented wolfram maybe wont be called
        learned, answer = self.handle_unknown_intent(utterance)

        if not learned:
            pass
            #self.speak("i dont know the answer")
        elif save and center_node is not None:
            self.connector.add_data(center_node, "wolfram_description", answer)
        return learned
        # TODO ask user questions about unknown nodes, teach skill handles response

    def handle_fallback(self, message):
        # try to deduce and learn an answer
        utterance = message.data["utterance"]
        return self.deduce_answer(utterance)

    # questions methods

    def get_wordnik(self, node):

        # check wordnik backend for more related nodes
        try:
            wordnik = self.connector.get_data(node, "wordnik")
        except:
            wordnik = self.service.adquire(node, "wordnik")["wordnik"]
            #self.connector.add_data(node, "wordnik", wordnik)
            #definition = wordnik["definitions"][0]
            #self.connector.add_data(node, "definition", definition)

        w_dict = wordnik
        wordnik = wordnik["relations"]
        if "antonym" in wordnik.keys():
            # antonyms are legit
            for antonim in wordnik["antonym"]:
                self.connector.add_antonim(node, antonim)
        else:
            self.log.info("no antonyms in wordnik")

        # other fields not very reliable, make cousins
        related = ["unknown"]
        extra = ["equivalent", "cross-reference", "hypernym"]
        extra2 = ["synonym", "same-context"]
        if self.focus < 10:
            related += extra
        if self.focus < 5:
            related += extra2

        concepts = self.connector.get_concept_names()
        for r in related:
            if r in wordnik.keys():
                for c in wordnik[r]:
                    c = c.lower().replace("the ", "")
                    if c not in concepts:
                        if self.debug:
                            self.speak("creating concept: " + c)
                        self.connector.create_concept(new_concept_name=c)
                    if c not in self.connector.get_cousins(node):
                        if self.debug:
                            self.speak("adding cousin: " + c + " to concept: " + node)
                        self.log.info("adding cousin: " + c + " to concept: " + node)
                        self.connector.add_cousin(node, c)
            else:
                self.log.info("no " + r + " in wordnik")
        return w_dict

    def handle_think_about(self, node, related=None):
        if related is None:
            related = {}
        # talk until no more related subjects
        # say what
        talked = self.handle_what_intent(node)
        if not talked:
            # no what ask wolfram
            talked , ans = self.handle_unknown_intent(node)
        else:
            # save updated data, only start node will be saved otherwise
            self.connector.save_concept(node)


        # check wordnik backend for more related nodes
        if self.focus < 15:
            w = self.get_wordnik(node)

        # get related nodes
        rel = self.connector.get_cousins(node)
        if self.debug:
            self.speak("focus level: " + str(self.focus))
            self.speak("related nodes: " + str(rel))
        self.log.info("focus level: " + str(self.focus))
        self.log.info("related nodes: " + str(rel))
        if self.focus > 15:
            # previous
            if self.debug:
                self.speak("focusing only in nodes related to previous node")
                self.speak("thinking about: " + str(related))
            self.log.info("focusing only in nodes related to previous node")
            self.log.info("thinking about: " + str(related))

        if self.focus < 10:
            # previous
            if self.debug:
                self.speak("forgetting previous nodes, focusing on node: " + node)
                self.speak("thinking about:" + str(related))
            self.log.info("forgetting previous nodes, focusing on node: " + node)
            # only related to this node
            related = rel
            self.log.info("thinking about:" + str(related))

        if self.focus == 0 or related == {}:
            if related == {}:
                self.log.info("no related nodes available")
            if self.debug:
                self.speak("adquiring new nodes")
            self.log.info("adquiring new nodes")
            # keep both
            related.update(rel)
            if self.debug:
                self.speak("thinking about:" + str(related))
            self.log.info("thinking about:" + str(related))

        try:
            # add parents and childs ot possible choice
            if self.focus < 15 or related == {}:
                if related == {}:
                    self.log.info("no related nodes available")
                if self.debug:
                    self.speak("Getting parents and childs of this node")
                self.log.info("Getting parents and childs of this node")
                for c in self.connector.get_parents(node):
                    if c not in related:
                        related[c] = 5
                for c in self.connector.get_childs(node):
                    if c not in related:
                        related[c] = 5
            if self.focus < 10 or related == {}:
                if related == {}:
                    self.log.info("no related nodes available")
                if self.debug:
                    self.speak("Getting synonims and antonims of this node")
                self.log.info("Getting synonims and antonims of this node")
                for c in self.connector.get_synonims(node):
                    if c not in related:
                        related[c] = 5
                for c in self.connector.get_antonims(node):
                    if c not in related:
                        related[c] = 5

            # remove self from dict
            if node in related.keys():
                related.pop(node)

            if self.debug:
                self.speak("related subjects: " + str(related))
            # pick one at random
            choice = random.choice(related.keys()).lower()
            self.log.info("current tought: " + choice)
            self.speak(choice)
            # talk about it
            more = self.handle_think_about(choice, related)
            if not more:
                f, ans = self.handle_unknown_intent(choice)
        except Exception as e:
            if self.debug:
                self.speak("could not find related info")
                self.speak(str(e))
            self.log.info("could not find related info")
            self.log.error(str(e))
        return talked

    def handle_talk_about(self, node, node2, utterance=""):

        # dont talk about "action" node
        if node == "talk" or node == "rant":
            node = node2

        # say what
        talked = self.handle_what_intent(node)
        if not talked:
            # no what ask wolfram
            talked, ans = self.handle_unknown_intent(utterance)

        # get related nodes
        related = self.connector.get_cousins(node)

        if self.debug:
            self.speak("related subjects: " + str(related))
        try:
            # add parents and childs ot possible choice
            for c in self.connector.get_parents(node):
                if c not in related:
                    related.append(c)
            for c in self.connector.get_childs(node):
                if c not in related:
                    related.append(c)
            for c in self.connector.get_synonims(node):
                if c not in related:
                    related.append(c)
            for c in self.connector.get_antonims(node):
                if c not in related:
                    related.append(c)
            # pick one at random
            choice = random.choice(related).lower()
            if self.debug:
                self.speak("chosing related topic: " + choice)
            # talk about it
            more = self.handle_what_intent(choice)
            if not more:
                f, ans = self.handle_unknown_intent(choice)
        except:
            if self.debug:
                self.speak("could not find related info")
            self.log.info("could not find related info")
        return talked

    def handle_relation(self, center_node, target_node):
        self.crawler.update_connector(self.connector)
        commons = common_this_and_that(center_node, target_node, self.crawler)

        c = 0
        for common in commons:
            if c > self.example_num:
                break
            self.speak(center_node + " are " + common + " like " + target_node)
            c += 1

        if commons == []:
            self.speak(center_node + " and " + target_node + " have nothing in common")
        return True

    def handle_why(self, center_node, target_node):
        # is this that
        # is this that
        self.crawler.update_connector(self.connector)
        flag = is_this_that(center_node, target_node, self.crawler)
        self.speak("answer to is " + center_node + " a " + target_node + " is " + str(flag))
        if flag:
            # why
            nodes = why_is_this_that(center_node, target_node, self.crawler)
            i = 0
            for node in nodes:
                if node != target_node:
                    self.speak(node + " is " + nodes[i + 1])
                i += 1
        return True

    def handle_how_intent(self, utterance):
        how_to = self.service.adquire(utterance, "wikihow")
        # TODO emit bus message for connector to update node with info
        how_to = how_to["wikihow"]
        # TODO check for empty how to and return false
        # the following how_tos are available
        self.speak("the following how tos are available")
        for step in how_to[0]["steps"]:
            self.speak(step)
        # TODO create intent tree
        # TODO start selection query
        # TODO speak how to
        return True

    def handle_compare_intent(self, center_node, target_node):
        self.crawler.update_connector(self.connector)
        flag = is_this_that(center_node, target_node, self.crawler)
        self.speak("answer to is " + center_node + " a " + target_node + " is " + str(flag))
        return True

    def handle_unknown_intent(self, utterance):
        # get answer from wolfram alpha
        result = self.service.adquire(utterance, "wolfram alpha")

        result = result["wolfram alpha"]
        answer = result["answer"]
        parents = result["parents"]
        synonims = result["synonims"]
        relevant = result["relevant"]
        childs = {}
        antonims = {}
        if self.debug:
            self.speak("new nodes from wolfram alpha answer: " + str(answer))
            self.speak("parents: " + str(parents))
            self.speak("synonims: " + str(synonims))
            self.speak("relevant: " + str(relevant))
        # TODO load/update nodes
        self.handle_update_connector(relevant, parents, childs, synonims, antonims)
        # say answer to user
        if answer != "no answer":
            self.speak(answer)
            return True, answer
        return False, answer

    def handle_examples_intent(self, node):
        self.log.info("searching examples of: " + node)
        if self.debug:
            self.speak("searching examples of: " + node)
        self.crawler.update_connector(self.connector)
        examples = examples_of_this(node, self.crawler)
        if self.debug:
            self.speak("examples: " + str(examples))
        if not examples:
            #self.speak("i dont know any examples of " + node)
            return False

        c = 0
        while c < self.example_num and examples:

            example = random.choice(examples)
            if example == node:
                i = 0
                for e in examples:
                    if example == e:
                        examples.pop(i)
                    i += 1

            if example != node:
                self.speak(str(example) + " is an example of " + str(node))
            i = 0
            for e in examples:
                if example == e:
                    examples.pop(i)
                i += 1

            c += 1

        return True

    def handle_what_intent(self, node):
        data = self.connector.get_data(node)
        dbpedia = {}
        wikidata = {}
        wikipedia = {}
        wordnik = {}

        if self.debug:
            self.speak("answering what")
            self.speak("node name:" + node)
            self.speak("node data: " + str(data))

        if node == "self":
            list = data.get("description", [])
            if len(list) == 0:
                return False
            else:
                self.speak(random.choice(list))
                return True

        # get data from web
        elif data == {}:
            self.log.info("no node data available")
            if self.debug:
                self.speak("seaching dbpedia")
            self.log.info("adquiring dbpedia")
            try:
                dbpedia = self.service.adquire(node, "dbpedia")["dbpedia"][node]
            except:
                if self.debug:
                    self.speak("no results from dbpedia")
                self.log.info("no results from dbpedia")

                if self.debug:
                    self.speak("seaching wikidata")
                self.log.info("adquiring wikidata")
                try:
                    wikidata = self.service.adquire(node, "wikidata")["wikidata"]
                except:
                    if self.debug:
                        self.speak("no results from wikidata")
                    self.log.info("no results from wikidata")

                    if self.debug:
                        self.speak("seaching wikipedia")
                    self.log.info("adquiring wikipedia")
                    try:
                        wikipedia = self.service.adquire(node, "wikipedia")["wikipedia"]
                    except:
                        if self.debug:
                            self.speak("no results from wikipedia")
                        self.log.info("no results from wikipedia")
                        if self.debug:
                            self.speak("seaching wordnik")
                        self.log.info("adquiring wordnik")
                        try:
                            wordnik = self.get_wordnik(node)
                        except:
                            if self.debug:
                                self.speak("no results from wordnik")
                            self.log.info("no results from wordnik")

           # debug available data

            if self.debug:
                self.speak("dbpedia data: " + str(dbpedia))
                self.speak("wikidata data: " + str(wikidata))
                self.speak("wikipedia data: " + str(wikipedia))
                self.speak("wordnik data: " + str(wordnik))

        # update data from web
        try:
            # dbpedia parents are handled in pre-processing / curiosity
            abstract = dbpedia["page_info"]["abstract"]
            data["abstract"] = abstract
            self.connector.add_data(node, "abstract", abstract)
            pic = dbpedia["page_info"]["picture"]
            data["pic"] = pic
            self.connector.add_data(node, "pic", pic)
            links = dbpedia["page_info"]["external_links"]
            self.connector.add_data(node, "links", links)
            cousins = dbpedia["page_info"]["related_subjects"]
            concepts = self.connector.get_concept_names()
            for cousin in cousins:
                if cousin not in concepts:
                    if self.debug:
                        self.speak("creating concept: " + cousin)
                    self.connector.create_concept(new_concept_name=cousin.lower())

                if cousin not in self.connector.get_cousins(node):
                    if self.debug:
                        self.speak("adding cousin: " + cousin + " to concept: " + node)
                    self.log.info("adding cousin: " + cousin + " to concept: " + node)
                    self.connector.add_cousin(node, cousin.lower())
        except:
            self.log.error("no dbpedia for " + node)
            try:
                # TODO all fields
                description = wikidata["description"]
                data["description"] = description
                self.connector.add_data(node, "description", description)
            except:
                self.log.error("no wikidata for " + node)
                try:
                    # TODO all fields
                    summary = wikipedia["summary"]
                    data["summary"] = summary
                    self.connector.add_data(node, "summary", summary)
                    description = wikipedia["description"]
                    data["description"] = description
                    self.connector.add_data(node, "description", description)
                except:
                    self.log.error("no wikipedia for " + node)
                    try:
                        definition = wordnik["definitions"][0]
                        data["definition"] = definition
                        self.connector.add_data(node, "definition", definition)
                    except:
                        self.log.error("no wordnik for " + node)

        self.crawler.update_connector(self.connector)
        #self.save_nodes([node])

        # read node data
        pics = data.get("pic")
        if pics:
            self.display_service.display(pics)

        metadata = {}
        links = data.get("links")
        if links:
            self.set_context("RelatedUrls", links)
            metadata = {"links": links}

        answer = data.get("abstract", "")
        if answer == "":
            answer = data.get("description", "")
            if answer == "":
                answer = data.get("summary", "")
                if answer == "":
                    answer = data.get("definition", "")
                    if answer == "":
                        answer = data.get("wolfram_description", "")

        # TODO use intent tree to give interactive dialog suggesting more info
        # self.speak("Do you want examples of " + node)
        # activate yes intent
        # use converse method to disable or do something
        if answer != "":
            self.speak(answer, metadata=metadata)
            return True
        return False

    def handle_who_intent(self, node):
        self.crawler.update_connector(self.connector)
        if node == "self":
            data = self.connector.get_data("self")
            list = data.get("name", {}).get("info", {}).keys()
            if len(list) == 0:
                return False
            else:
                self.speak("I am " + random.choice(list))
                return True
        else:
            return self.handle_what_intent(node)

    def handle_when_intent(self, node):
        self.crawler.update_connector(self.connector)
        if node == "self":
            data = self.connector.get_data("self")
        return False

    def handle_where_intent(self, node):
        self.crawler.update_connector(self.connector)
        if node == "self":
            data = self.connector.get_data("self")
        return False

    def handle_which_intent(self, node):
        self.crawler.update_connector(self.connector)
        if node == "self":
            data = self.connector.get_data("self")
        return False

    def handle_whose_intent(self, node):
        self.crawler.update_connector(self.connector)
        if node == "self":
            data = self.connector.get_data("self")
        return False

    # feedback
    def handle_incorrect_answer(self):
        # create nodes / connections for right answer
        #self.last_question = ""
        #self.last_question_type = ""
        #self.last_center = ""
        #self.last_target = ""
        self.speak_dialog("wrong_answer")

    def feedback(self, message):
        feedback = message.data.get("feedback", "")
        # check if previously answered a question
        if feedback == "negative" and self.answered:
            # wrong answer was given, react to negative feedback
            self.handle_incorrect_answer()
        if feedback == "negative" and not self.answered:
            # no apparent reason for negative feedback
            self.speak_dialog("wrong_answer_confused")

    def stop(self):
        self.save_nodes()


def create_skill():
    return LilacsCoreSkill()

