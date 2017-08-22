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


from requests import HTTPError
from StringIO import StringIO
import re
import wolframalpha
import sys
from os.path import dirname

sys.path.append(dirname(dirname(__file__)))
from jarbas_utils.question_parser import LILACSQuestionParser

from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message
from mycroft.api import Api
from mycroft.util.log import getLogger
from mycroft.skills.core import MycroftSkill

__author__ = 'jarbas'

logger = getLogger(__name__)

PIDS = ['Value', 'NotableFacts:PeopleData', 'BasicInformation:PeopleData',
        'Definition', 'DecimalApproximation']


class WAApi(Api):
    def __init__(self):
        super(WAApi, self).__init__("wa")

    def get_data(self, response):
        return response

    def query(self, input):
        data = self.request({"query": {"input": input}})
        return wolframalpha.Result(StringIO(data.content))


class LILACSWolframalphaSkill(MycroftSkill):
    def __init__(self):
        super(LILACSWolframalphaSkill, self).__init__(
            name="LILACS_WolframalphaSkill")
        self.parser = LILACSQuestionParser()
        if False:
        #if self.config_core.get("WolframAlphaSkill").get("proxy"):
            self.client = WAApi()
        else:
            try:
                self.api = self.config_core.get("APIS").get("WolframAlpha")
            except:
                self.api = self.config_core.get("WolframAlphaSkill").get("api_key")
            self.client = wolframalpha.Client(self.api)

    def initialize(self):
        self.emitter.on("wolframalpha.request", self.handle_ask_wolframalpha)

        test_intent = IntentBuilder("TestWolframIntent") \
            .require("testr").require("TargetKeyword").build()
        self.register_intent(test_intent, self.handle_test_intent)

    def handle_test_intent(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        answer = self.adquire(node).get("wolfram alpha").get("answer")
        if answer != "no answer":
            self.speak(answer)
        else:
            self.speak("Could not get answer for " + node + " from wolfram alpha")

    def handle_ask_wolframalpha(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node)
        #self.speak(str(result))
        self.emitter.emit(Message("wolframalpha.result", result, self.message_context))

    def adquire(self, subject):
        logger.info('WolframalphaKnowledge_Adquire')
        dict = {}
        if subject is None:
            logger.error("No subject to adquire knowledge about")
        else:
            # get knowledge about
            # TODO exceptions for erros
            try:
                response, parents, synonims, midle = self.wolfram_to_nodes(
                    subject)
                node_data = {"answer": response, "parents": parents,
                             "synonims": synonims, "relevant": midle}
                # id info source
                dict["wolfram alpha"] = node_data
            except Exception as e:
                logger.error(
                    "Could not parse wolframalpha for " + str(subject))
        return dict

    def wolfram_to_nodes(self, query, lang="en-us"):
        responses = self.ask_wolfram(query)
        txt = query.lower().replace("the ", "").replace("an ", "").replace(
            "a ",
                                                                           "")
        try:
            center_node, target_node, parents, synonims, midle, question = \
            self.parser.process_entitys(
            txt)
            response = responses[0]

            txt = response.lower().replace("the ", "").replace("an ", "").replace(
                "a ", "")
            if txt != "no answer":
                midle2, parents2, synonims2 = self.parser.tag_from_dbpedia(txt)

                for parent in parents2:
                    if parent not in parents:
                        parents.setdefault(parent, parents2[parent])
                midle += midle2
                for synonim in synonims2:
                    synonims.setdefault(synonim, synonims2[synonim])
        except Exception as e:
            self.log.error(e)
            center_node = None
            midle = []
            parents = {}
            synonims = {}
            response = responses[0]

        return response, parents, synonims, midle

    def ask_wolfram(self, query, lang="en-us"):
        others = []
        result = None
        try:
            res = self.client.query(query)
            result = self.get_result(res)
            if result is None:
                others = self._find_did_you_mean(res)
        except HTTPError as e:
            if e.response.status_code == 401:
                self.emitter.emit(Message("mycroft.not.paired"))
            return
        except Exception as e:
            self.log.error(e)
            print "error asking wolfram alpha, did you insert an api key?"

        response = ["no answer"]
        if result:
            input_interpretation = self.__find_pod_id(res.pods, 'Input')
            verb = "is"

            if "|" in result:  # Assuming "|" indicates a list of items
                verb = ":"

            result = self.process_wolfram_string(result, lang)
            input_interpretation = \
                self.process_wolfram_string(input_interpretation, lang)
            response = "%s %s %s" % (input_interpretation, verb, result)
            i = response.find("?")
            if i != -1:
                response = response[i + 1:].replace("is ", "").replace("(", "\n").replace(")", " ")
            response = [response]

        else:
            if len(others) > 0:
                response.remove("no answer")
                for other in others:
                    response.append(self.ask_wolfram(other))

        return response

    def get_result(self, res):
        try:
            return next(res.results).text
        except:
            result = None
            try:
                for pid in PIDS:
                    result = self.__find_pod_id(res.pods, pid)
                    if result:
                        result = result[:5]
                        break
                if not result:
                    result = self.__find_num(res.pods, '200')
                return result
            except:
                return result

    def __find_pod_id(self, pods, pod_id):
        for pod in pods:
            if pod_id in pod.id:
                return pod.text
        return None

    def __find_num(self, pods, pod_num):
        for pod in pods:
            if pod.node.attrib['position'] == pod_num:
                return pod.text
        return None

    def _find_did_you_mean(self, res):
        value = []
        root = res.tree.find('didyoumeans')
        if root is not None:
            for result in root:
                value.append(result.text)
        return value

    def process_wolfram_string(self, text, lang):
        # Remove extra whitespace
        text = re.sub(r" \s+", r" ", text)

        # Convert | symbols to commas
        text = re.sub(r" \| ", r", ", text)

        # Convert newlines to commas
        text = re.sub(r"\n", r", ", text)

        # Convert !s to factorial
        text = re.sub(r"!", r",factorial", text)

        regex = "(1,|1\.) (?P<Definition>.*) (2,|2\.) (.*)"
        list_regex = re.compile(regex)

        match = list_regex.match(text)
        if match:
            text = match.group('Definition')

        return text


def create_skill():
    return LILACSWolframalphaSkill()