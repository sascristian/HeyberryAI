from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from adapt.context import ContextManager

import time

client = None

class ContextService():
    def __init__(self):

        ##### messagebus
        global client
        client = WebsocketClient()

        client.emitter.on("vision_result", self.handle_vision_result)
        client.emitter.on('recognizer_loop:utterance', self.handle_recognizer_loop_utterance)
        client.emitter.on("freewill_result", self.handle_freewill_result)
        client.emitter.on("speak", self.handle_speak)
        client.emitter.on("results", self.handle_skill_results)
        client.emitter.on("context_request", self.handle_context_request)
        client.emitter.on("intent_failure", self.handle_intent_failure) #counts fails
        client.emitter.on("register_vocab", self.handle_register_vocab) #handle regexes
        client.emitter.on("skill_loaded", self.handle_register_skill)
        client.emitter.on("context_key_request", self.handle_key_context_request)
        client.emitter.on("context_key_override", self.handle_key_context_override)
        client.emitter.on("register_intent", self.handle_register_intent)

        #### database
        self.vocab = [] #keys
        self.regex = [] #ArticleTitle
        self.context_dict = {} # Location : Here
        self.bluetooth_ids = {} # 666 : True
        self.intents = {}

        #### synonims
        #self.synonims = {"last speech":"utterance", "last heard":"utterances"}

        self.register_signals()
        self.register_abstract()

        #### adapt
        self.manager = ContextManager()

    ####### init / helper functions

    def register_context(self, params, type="default"):
        for name in params:
            if name not in self.vocab:
                self.vocab.append(name)
                self.context_dict.setdefault(name)
                print "registering context " + name + "   type: " + type

    def register_abstract(self):
        # params that are not listened from bus but are otherwise wanted
        params = ["start time up", "language", "name", "location", "last_heard","last_spoken"] #name #location
        self.register_context(params)
        self.context_dict["start up time"] = time.time()
        self.context_dict["language"] = "english"
        self.context_dict["name"] = "jarbas"
        self.context_dict["location"] = "internet" # TODO get this from config

    def register_signals(self):
        params = ["utterance", "utterances", "dopamine", "serotonine", "tiredness", "last_tought", "last_action", "mood", "movement", "number of persons", "master", "smile detected"]
        for name in params:
            if name not in self.vocab:
                self.register_context(params, type="signal")
        #register fail
        params = ["fails", "last_fail"]
        for param in params:
            if param not in self.vocab:
                self.register_context(params=[param],type="signal")
        self.context_dict["fails"]= 0
        self.context_dict["last_fail"] = "achieve sentience"

    def handle_register_skill(self, message):
        params = [message.data.get("skill_name")]
        self.register_context(params, type="skill")

    def request_update(self, target="all"):
        # target = freewill / vision / all
        client.emit(Message("context_update", {'target': target}))

    def get_regex_context(self, result, regex):
        print "\nkey detected " + regex + "\n updating with "+ result
        self.context_dict[regex] = result
        self.register_with_adapt(regex)

                ##### abstract signals  general api yet to be implemented

    ### adapt functions - dont know how to work with this

    def register_with_adapt(self, key):
        if key is not None:
            print "injecting context " + key + " with value " + self.regex[key]
            self.manager.inject_context(entity=key, metadata=self.regex[key])

    def register_with_adapt_all(self, message):
        for key in self.regex:
            if self.regex[key] is not None:
                print "injecting context " + key + " with value " + self.regex[key]
                self.manager.inject_context(entity=key, metadata=self.regex[key])

    #### implement more signals

    def handle_register_intent(self, message):
        # just for expansion, may be usefull to have intents in the future
        intent = message.data.get["name"]
        data = message.data
        self.intents.setdefault(intent)
        self.intents[intent] = data
        #print "registered intent " + intent

    def handle_context_request(self, message):
        self.request_update()

        time.sleep(0.5)#TODO implement wait for signal response?

        # emit unified response from all contexts   ### need a better title for message
        client.emit(
            Message("context_result", {'dictionary': self.context_dict}))

    def handle_register_vocab(self, message):
        regex = message.data.get("regex")
        if regex is not None and regex not in self.regex:
           # print regex
            # parse words for regex (<?P<KEY>.*)
            s = regex.find("(?P<")
            e = regex.find(">")
            params = [str(regex[s + 4:e])]
            self.register_context(params, type="regex")
            self.regex.append(params)

    def handle_vision_result(self, message):
        params = ["movement", "number of persons", "master", "smile detected"]
        for name in params:
            self.context_dict[name] = message.data.get(name)

    def handle_freewill_result(self, message):
        params = ["dopamine", "serotonine", "tiredness", "last_tought", "last_action", "mood"]
        for name in params:
            self.context_dict[name] = message.data.get(name)

    def handle_speak(self, message):
        params = ["utterance"]
        #note: already saved as speak in skills_result, keeping for redundancy
        for name in params:
            self.context_dict[name] = message.data.get(name)

        self.context_dict["last_spoken"] = self.context_dict["utterance"] #probably shared key, may be over-riden by other signal , registering synonim key

    def handle_recognizer_loop_utterance(self, message):
        params = ["utterances"]
        for name in params:
            self.context_dict[name] = message.data.get(name)

        self.context_dict["last_heard"] =self.context_dict["utterances"]

    def handle_intent_failure(self, message):
        self.context_dict["fails"] = self.context_dict["fails"]+1
        self.context_dict["last_fail"] = message.data.get("utteramce")

    def handle_skill_results(self, message):
        key = message.data.get('skill_name') #must send results in skill, NOT default
        results = message.data
        self.context_dict[key]=results
        #logger.info("Updated context for results from "+key)
        for result in results:
           # print result
            params = [result]  # if you send a string instead it is taken like a list of chars
            if result not in self.vocab and result != "skill_name":
                self.register_context(params, type="skill_result")
            try:
                self.context_dict[result] = message.data.get[result]
                print result + " updated with " + self.context_dict[result]
            except:
                pass
        for regex in self.regex:
            result = message.data.get(regex[0])
            if result is not None:
                self.get_regex_context(result, regex[0])

    def handle_key_context_request(self,message):
        key = message.data.get["key"]
        if key is not None:
            result = self.context_dict[key]
            #emit result
            client.emit(
                Message("context_key_result", {'key': key, "result":result }))

    def handle_key_context_override(self, message):
        key = message.data.get["key"]
        value = message.data.get["value"]
        if key is not None and value is not None:
            self.context_dict[key] = value

    ### future signals

    def handle_bluetooth_new(self, message):
        #registered context with bluetooth id
        id = message.data.get("id")
        if id not in self.bluetooth_ids:
            params = [id]
            self.register_context(params, type="bluetooth")
        self.context_dict[id]= True

    def handle_bluetooth_leave(self, message):
        #registered context with bluetooth id
        id = message.data.get("id")
        self.context_dict[id]= False

    ### main loop

    def listen(self):
        global client
        client.run_forever()


manager = ContextService()
manager.listen()
