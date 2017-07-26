
import re

import spotlight
from requests import ConnectionError, HTTPError

class EnglishQuestionParser():
    """
    Poor-man's english question parser. Not even close to conclusive, but
    appears to construct some decent w|a queries and responses.
    
    __author__ = 'seanfitz'
    
    """


    def __init__(self):
        self.regexes = [

            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|whose) "
                "(?P<Query1>.*) (?P<QuestionVerb>is|are|was|were) "
                "(?P<Query2>.*)"),
            re.compile(
                ".*(?P<QuestionWord>are|is) "
                "(?P<Query1>.*) (?P<QuestionVerb>an|a|an example off|an instance off) "
                "(?P<Query2>.*)"),
            re.compile(
                "(?P<Query1>.*) (?P<QuestionVerb>and) "
                "(?P<Query2>.*) (?P<QuestionWord>in common)"),

            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|how "
                "to|how|talk"
                "|rant|think) "
                ""
                "(?P<QuestionVerb>\w+)"
                "(?P<Query1>.*) (?P<QuestionTarget>of|from|at) "
                "(?P<Query2>.*)"),
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|how to|ho"
                "w|example|examples) "
                ""
                "(?P<QuestionVerb>\w+) (?P<Query>.*)")

        ]

    def _normalize(self, groupdict):
        if 'Query' in groupdict:
            return groupdict
        elif 'Query1' and 'Query2' in groupdict:
            return {
                'QuestionWord': groupdict.get('QuestionWord'),
                'QuestionVerb': groupdict.get('QuestionVerb'),
                'QuestionTarget': groupdict.get('QuestionTarget'),
                'Query1': groupdict.get('Query1'),
                'Query2': groupdict.get('Query2'),
                'Query': ' '.join([groupdict.get('Query1'), groupdict.get(
                    'Query2')])
            }

    def parse(self, utterance):
        for regex in self.regexes:
            match = regex.match(utterance)
            if match:
                return self._normalize(match.groupdict())
        return {'Query': utterance}


class LILACSQuestionParser():
    def __init__(self, host="http://model.dbpedia-spotlight.org/en/annotate"):
        # 222 2en 8pt 5fr
        #host = "http://spotlight.sztaki.hu:2222/rest/annotate"
        self.parser = EnglishQuestionParser()
        self.host = host

    def process_entitys(self, text):
        parse = self.poor_parse(text)
        query = parse.get("Query", "")
        subjects, parents, synonims = self.tag_from_dbpedia(text)
        center_node, target_node = self.select_from_dbpedia(subjects)
        center_node, target_node = self.process_nodes(center_node,
                                                      target_node, query)
        if center_node == "":
            center_node, target_node = self.select_from_regex(parse)
        center_node, target_node = self.check_nodes(center_node, target_node)
        middle = [node for node in subjects if
                  node != center_node and node != target_node]
        return center_node, target_node, parents, synonims, middle, parse

    def select_from_dbpedia(self, subjects):
        # process dbpedia rating
        center = 666
        center_node = ""
        for node in subjects:
            if subjects[node] < center:
                center = subjects[node]
                center_node = node

        target = 666
        # TODO better select target mechanism
        target_node = ""
        for node in subjects:
            if subjects[node] < target and node != center_node:
                target = subjects[node]
                target_node = node

        return center_node, target_node

    def select_from_regex(self, parse):
        center_node = ""
        target_node = ""
        # aproximate guess from regex
        if target_node == "":
            verb = parse.get("QuestionVerb", "")
            verbs = ["is", "are", "was", "were", "of", "will", "the", "am"]
            if verb in verbs:
                verb = ""
            target_node = parse.get("Query2", verb)
        if center_node == "":
            center_node = parse.get("Query1", parse.get("Query", ""))
            center_node = center_node.replace(" is the ", "")
            center_node = center_node.replace("is the ", "")
            center_node = center_node.replace("is ", "")
            center_node = center_node.replace("the ", "")
            center_node = center_node.replace(" is ", "")
            center_node = center_node.replace(" the ", "")
            center_node = center_node.replace(" a ", "")
            center_node = center_node.replace(" an ", "")
            center_node = center_node.replace("a ", "")
            center_node = center_node.replace("an ", "")
            words = center_node.split(" ")
            if len(words) > 1:
                i = 0
                center_node = words[0]
                if target_node == "":
                    target_node = words[1]
        return center_node, target_node

    def check_nodes(self, center_node, target_node):
        if center_node == "i":
            center_node = "current_user"
        if target_node == "i":
            target_node = "current_user"
        return center_node, target_node

    def process_nodes(self, center_node, target_node, query):
        stuff = ["favorite", "favourite"]
        # check if my | i | mine |you |your
        user = ["my", "mine"]
        jarbas = ["you", "your"]
        flag = False
        # try to guess if talking about current user
        for word in user:
            if word in query:
                # check if it is allowed ( i vs is)
                target_node = center_node
                center_node = "current_user"
                flag = True
                break
        # if not, guess if talking about self
        if not flag:
            for word in jarbas:
                if word in query:
                    target_node = center_node
                    center_node = "self"
                    break

        # check if "favorite" (or other meaningful adjective) is not the
        # first single node
        if center_node in stuff:
            candidate = query[query.find(center_node):]
            # if the word after favorite is target node
            if target_node in candidate:
                # make center node "favorite" target_node
                candidate = candidate[:candidate.find(target_node)]
                # make target empty
                target_node = ""
            # update center node
            center_node = candidate

        elif target_node in stuff:
            # make target node everything after "favorite"
            candidate = query[query.find(target_node):]
            target_node = candidate

        return center_node, target_node

    def poor_parse(self, text):
        return self.parser.parse(text)

    def tag_from_dbpedia(self, text, spotter='Default'):
        text = str(text).lower()
        subjects = {}
        parents = {}
        synonims = {}
        try:
            annotations = spotlight.annotate(self.host, text,
                                             spotter=spotter)
            for annotation in annotations:

                # how sure we are this is about this dbpedia entry
                score = annotation["similarityScore"]
                # entry we are talking about
                subject = annotation["surfaceForm"].lower()
                # smaller is closer to be main topic of sentence
                offset = annotation["offset"]
                # TODO tweak this value and make configuable
                if float(score) < 0.2:
                    continue
                subjects.setdefault(subject, offset)
                # categorie of this <- linked nodes <- parsing for dbpedia search
                if annotation["types"]:
                    p = []
                    types = annotation["types"].split(",")
                    for type in types:
                        type = type.replace("DBpedia:", "").replace("Schema:", "").replace("Http://xmlns.com/foaf/0.1/", "").lower()
                        if type not in p:
                            p.append(type)
                    parents.setdefault(subject, p)
                # dbpedia link
                url = annotation["URI"]
                #print "link: " + url
                dbpedia_name = url.replace("http://dbpedia.org/resource/", "").replace("_", " ")
                if dbpedia_name.lower() not in subject:
                    synonims.setdefault(subject, dbpedia_name.lower())
        except ConnectionError as e:
            # TODO use logger
            print e
        except HTTPError as e:
            print e
        except Exception as e:
            print e
        return subjects, parents, synonims


def test_qp(questions = None):
    parser = LILACSQuestionParser()
    if questions is None:
        questions = ["what is the speed of light","who are you", "who am i",
                     "what is my favorite song",
                     "what is your favorite book", "who is my cousin",
                     "what is war", "how to kill animals ( a cow ) and make meat",
                     "what is a living being", "why are humans living beings",
                     "give examples of animals"]
    for text in questions:
        center_node, target_node, parents, synonims, midle, \
        parse = parser.process_entitys(text)
        question = parse.get("QuestionWord", "unknown")
        print "\nQuestion: " + text
        print "question_type: " + question
        print "center_node: " + center_node
        print "target_node: " + target_node
        print "parents: " + str(parents)
        print "relevant_nodes: " + str(midle)
        print "synonims: " + str(synonims)
        print "parse: " + str(parse)
