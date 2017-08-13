
import re
from mycroft.util.parse import normalize
import spotlight
from requests import ConnectionError, HTTPError
from nltk.stem.wordnet import WordNetLemmatizer


class EnglishQuestionParser():
    """
    Poor-man's english question parser. Not even close to conclusive, but
    appears to construct some decent w|a queries and responses.
    
    __author__ = 'seanfitz'
    
    """


    def __init__(self):
        self.regexes = [
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|how)"
                "(?P<Query1>.*) (?P<QuestionTargetWord>of|from|at|on|in|off) "
                "(?P<Query2>.*)"),
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|whose) "
                "(?P<Query1>.*) "
                "(?P<QuestionVerb>is|are|was|were)"
                "(?P<Query2>.*)"),
            re.compile(
                ".*(?P<QuestionWord>think|wonder|talk|rant) "
                "(?P<QuestionTargetWord>about|off|of)"
                "(?!of|from|at|on|in|off)(<Query>.*)"),
            re.compile(
                ".*(?P<QuestionWord>think|wonder|talk|rant) "
                "(?P<QuestionTargetWord>about |off |of )"
                "(?P<Query1>.*) (?P<QuestionTargetWord2>of |from |at |on |in |off )"
                "(?P<Query2>.*)"),
            re.compile(
                "^(?P<QuestionWord>are|is|am) "
                "(?P<Query1>.*) (?P<QuestionVerb>an|a|an example off|an "
                "instance off|a example off|a instance off|an example of|an instance of|a example of|a instance of) "
                "(?P<Query2>.*)"),
            re.compile(
                "^(?P<QuestionWord>are|is|am) "
                "(?P<Query1>.*) (?P<QuestionTargetWord>with)"
                "(?P<Query2>.*)"),
            re.compile(
                "^(?P<QuestionWord>is|am|are|can) "
                "(?P<QuestionPerson>i|him|it|she|we|he|they|you|your|my|me|we|you'r) "
                "(?P<Query>.*)"),
            re.compile(
                "(?P<Query1>.*) (?P<QuestionVerb>and) "
                "(?P<Query2>.*) (?P<QuestionWord>in common)"),
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|how|example|examples|think|wonder|talk|rant) "
                "(?P<QuestionVerb>\w+)(?P<Query>.*)"),
        ]

    def _normalize(self, groupdict):
        if 'Query' in groupdict:
            groupdict["Query"] = normalize(groupdict["Query"],
                                           remove_articles=True)
            return groupdict
        elif 'Query1' and 'Query2' in groupdict:
            return {
                'QuestionWord': groupdict.get('QuestionWord'),
                'QuestionVerb': groupdict.get('QuestionVerb'),
                'QuestionTargetWord': groupdict.get('QuestionTargetWord'),
                'QuestionTargetWord2': groupdict.get('QuestionTargetWord2'),
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
        return {'Query': normalize(utterance, remove_articles=True)}


class LILACSQuestionParser():
    def __init__(self, host="http://model.dbpedia-spotlight.org/en/annotate"):
        # 222 2en 8pt 5fr
        #host = "http://spotlight.sztaki.hu:2222/rest/annotate"
        self.parser = EnglishQuestionParser()
        self.host = host
        self.lmtzr = WordNetLemmatizer()

    def process_entitys(self, text):
        parse = self.poor_parse(text)
        query = parse.get("Query", "")
        subjects, parents, synonims = self.tag_from_dbpedia(text)
        center_node, target_node = self.select_from_dbpedia(subjects)
        center_node, target_node = self.process_nodes(center_node,
                                                      target_node, query)
        if center_node == "" or target_node == "":
            center_node, target_node = self.select_from_regex(parse)
        center_node = self.fix_node(center_node)
        target_node = self.fix_node(target_node)
        middle = [self.fix_node(node) for node in subjects if
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
        # aproximate guess from regex

        verb = parse.get("QuestionVerb", "")
        verbs = ["is", "are", "was", "were", "of", "will", "the", "am",
                 "favorite", "favourite"]
        if verb in verbs:
            verb = ""
        center_node = parse.get("QuestionPerson")
        if not center_node:
            target_node = parse.get("Query2", verb)
            center_node = parse.get("Query1", parse.get("Query", ""))
        else:
            target_node = parse.get("Query1", parse.get("Query", verb))
            words = center_node.split(" ")
            bads = ["the", "is", "a", "an", "of", "off",parse.get(
                "QuestionWord", "gsaetjhtsvreh")]
            for w in bads:
                if w in words:
                    words = words.remove(w)
            if len(words) > 1:
                center_node = words[0]
                if target_node == "":
                    for w in words[1:]:
                        target_node += w + " "
        return center_node, target_node

    def fix_node(self, node):
        if node is None:
            return ""
        # removing symbols
        symbols = [",", ";", ".", ":", "-", "_", "?", "!", "+", "*","/", "(",
                   ")", "[", "]", "{", "}", '"', "'"]
        for s in symbols:
            if s in node:
                node = node.replace(s, " ")
        # distinguishing self and user
        mes = ["i", "me", "my", "mine"]
        jarbas = ["you", "your", "you'r", "yourself"]
        if node in mes:
            node = "current_user"
        if node in jarbas:
            node = "self"
        # remove bad words
        bads = ["the", "in", "a", "an", "on", "at", "of", "off", "and"]
        for word in bads:
            if word in node.split(" "):
                node = node.replace(word+" ", "")
        # lenmatize
        if node:
            try:
                n = ""
                for word in node.split(" "):
                    word = self.lmtzr.lemmatize(word)
                    #word = self.lmtzr.lemmatize(word, "v")
                    n += word + " "
                node = n
            except:
                node = self.lmtzr.lemmatize(node)
        # check empty strings at start or end
        if node:
            while node[0] == " ":
                node = node[1:]
            while node[-1] == " ":
                node = node[:-1]
        return node

    def process_nodes(self, center_node, target_node, query):
        stuff = ["favorite", "favourite"]
        # check if my | i | mine |you |your
        user = ["my", "mine", "me", "i"]
        jarbas = ["you", "your", "you'r", "yourself"]
        flag = False
        # try to guess if talking about current user
        for word in user:
            if word in query.split(" "):
                if target_node != "":
                    target_node = center_node
                    center_node = "current_user"
                else:
                    target_node = "current_user"
                flag = True
                break
        # if not, guess if talking about self
        if not flag:
            for word in jarbas:
                if word in query.split(" "):
                    target_node = center_node
                    center_node = "self"
                    break

        # check if "favorite" (or other meaningful adjective) is not the
        # first single node
        if center_node in stuff:
            candidate = query.split(" ")
            # if the word after favorite is target node
            if target_node in candidate:
                # make center node "favorite" target_node
                candidate = candidate.remove(target_node)
                # make target empty
                target_node = ""
                # update center node
                for word in candidate[:2]:
                    center_node += word + " "
                for word in candidate[2:]:
                    target_node += word + " "
        if target_node in stuff:
            target_node = query[query.find(target_node):]
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
                subject = self.lmtzr.lemmatize(annotation["surfaceForm"].lower())
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
                            type = self.lmtzr.lemmatize(type)
                            p.append(type)

                    parents.setdefault(subject, p)
                # dbpedia link
                url = annotation["URI"]
                #print "link: " + url
                dbpedia_name = url.replace("http://dbpedia.org/resource/", "").replace("_", " ")
                if dbpedia_name.lower() not in subject:
                    synonims.setdefault(subject,
                                        self.lmtzr.lemmatize(dbpedia_name.lower()))
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
        questions = ["think about the meaning of life", "what is the speed of "
                     "light","who are you", "who am i",
                     "what is my favorite song",
                     "what is your favorite book", "who is my cousin",
                     "what is war", "how to kill animals ( a cow ) and make meat",
                     "what is a living being", "why are humans living beings",
                     "give examples of animals","how do i make money with "
                                                "bitcoin", "how can i win "
                                                           "bitcoin","are the prophets with me", "is your god evil"]
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

if __name__ == "__main__":
    test_qp()