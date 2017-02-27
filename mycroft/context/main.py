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
        client.emitter.on("chat_request", self.handle_fbchat_intent)

        ############## database
        self.vocab = [] #all keys
        # all contexts -> this should be enough for everything, same name keys may get replaced
        self.context_dict = {}  # Location : Here
        ## for redundancy -> seperation -> future unforseen expansion
        # skill data
        self.skills_dict = {} # data from loaded skills
        self.results_dict = {} # data from received skill results
        # regex data
        self.regex_dict = {} # regex expressions data
        # intent data
        self.intents_dict = {} #registered intents data
        # signals data
        self.signals_dict = {}# messagebus signals data
        # abstract data
        self.abstract_dict = {}# other data
        # facebook hcat data
        self.fbchat_dict = {}# userid: last sentence   and   username: userid

        #future / POC
        self.bluetooth_dict = {"me":True} # bluetooth ids for user presence    666 : False

        ## init contexts
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
                if type == "skill":
                    self.skills_dict.setdefault(name)
                elif type == "skil_result":
                    self.results_dict.setdefault(name)
                elif type == "regex":
                    self.regex_dict.setdefault(name)
                elif type == "intent":
                    self.intents_dict.setdefault(name)
                elif type == "signal":
                    self.signals_dict.setdefault(name)
                elif type == "abstract":
                    self.abstract_dict.setdefault(name)
                elif type == "bluetooth":
                    self.bluetooth_dict.setdefault(name)
                elif type == "facebook":
                    self.fbchat_dict.setdefault(name)


                print "registering context " + name + "   type: " + type

    def register_abstract(self):
        # params that are not listened from bus but are otherwise wanted
        params = ["start time up", "language", "name", "location", "last_heard","last_spoken","last_seen_timestamp","last_heard_timestamp","last_spoken_timestamp"] #name #location
        self.register_context(params)
        self.context_dict["start up time"] = time.time()
        self.context_dict["language"] = "english"
        self.context_dict["name"] = "jarbas"
        self.context_dict["location"] = "internet" # TODO get this from config
        ### redundancy
        self.abstract_dict["start up time"] = time.time()
        self.abstract_dict["language"] = "english"
        self.abstract_dict["name"] = "jarbas"
        self.abstract_dict["location"] = "internet"  # TODO get this from config

    def register_signals(self):
        params = ["utterance", "utterances", "dopamine", "serotonine", "tiredness", "last_tought", "last_action", "mood", "movement", "number of persons", "master", "smile detected"]
        for name in params:
            if name not in self.vocab:
                self.register_context(params, type="signal")
        #register and init fail
        params = ["fails", "last_fail"]
        for param in params:
            if param not in self.vocab:
                self.register_context(params=[param],type="signal")
        self.context_dict["fails"]= 0
        self.context_dict["last_fail"] = "achieve sentience"
        # redudnacy
        self.signals_dict["fails"] = 0
        self.signals_dict["last_fail"] = "achieve sentience"

    def handle_register_skill(self, message):
        params = [message.data.get("skill_name")]
        self.register_context(params, type="skill")

    def request_update(self, target="all"):
        # target = freewill / vision / all
        client.emit(Message("context_update", {'target': target}))

    def get_regex_context(self, result, regex):
        print "\nkey detected " + regex + "\n updating with "+ result
        self.regex_dict[regex] = result #this was already added in results dict also
        self.register_with_adapt(regex)

                ##### abstract signals  general api yet to be implemented

    ### adapt functions - dont know how to work with this

    def register_with_adapt(self, key):
        if key is not None:
            print "injecting adapt context manager key: " + key + "\nwith value: " + self.regex_dict[key]
            #self.manager.inject_context(entity=key, metadata=self.regex_dict[key])

            entity = {'key': key, 'data': self.regex_dict[key], 'confidence': 1.0}
            self.manager.inject_context(entity)
            context = self.manager.get_context()
            print context

    def register_with_adapt_all(self, message):
        for key in self.regex_dict:
            if self.regex_dict[key] is not None:
                print "injecting context " + key + " with value " + self.regex_dict[key]
                self.manager.inject_context(entity=key, metadata=self.regex_dict[key])

    #### implement more signals

    def handle_fbchat_intent(self, message):
        # just for expansion, may be usefull to have intents in the future
        # print message.data["name"]
        user = message.data["id"]
        username = message.data["name"]
        data = message.data["utterances"]
        # print data
        self.register_context([user], type="facebook")
        self.context_dict[user] = data  # populate
        self.context_dict[username] = user  # populate
        self.fbchat_dict[user] = data  # populate
        self.fbchat_dict[username] = user  # populate
        print "populating fbchat user id: " + user + " user name: " + username + " with data: " + data

    def handle_register_intent(self, message):
        # just for expansion, may be usefull to have intents in the future
        #print message.data["name"]
        intent = message.data["name"]
        data = message.data
        #print data
        self.register_context([intent], type="intent")
        self.context_dict[intent] = data  # populate
        self.intents_dict[intent] = data #populate
        print "populating intent " + intent + " with data: " + data

    def handle_context_request(self, message):
        self.request_update()

        time.sleep(0.5)#TODO implement wait for signal response?

        # emit unified response from all contexts   ### need a better title for message
        client.emit(
            Message("context_result", {'full_dictionary': self.context_dict,'bluetooth': self.bluetooth_dict, 'abstract': self.abstract_dict, 'signals': self.signals_dict, 'results': self.results_dict, 'intents': self.intents_dict,'regex': self.regex_dict,'skills': self.skills_dict}))

    def handle_register_vocab(self, message):
        regex = message.data.get("regex")
        if regex is not None and regex not in self.regex_dict:
           # print regex
            # parse words for regex (<?P<KEY>.*)
            s = regex.find("(?P<")
            e = regex.find(">")
            params = [str(regex[s + 4:e])]
            self.register_context(params, type="regex")
            #self.regex.append(params)

    def handle_vision_result(self, message):
        params = ["movement", "number of persons", "master", "smile detected"]
        for name in params:
            self.context_dict[name] = message.data.get(name)
            self.signals_dict[name] = message.data.get(name)

        if message.data.get("number of persons") > int(0):
            self.context_dict["last_seen_timestamp"] = time.asctime()
            self.abstract_dict["last_seen_timestamp"] = time.asctime()

    def handle_freewill_result(self, message):
        params = ["dopamine", "serotonine", "tiredness", "last_tought", "last_action", "mood"]
        for name in params:
            self.context_dict[name] = message.data.get(name)
            self.signals_dict[name] = message.data.get(name)

    def handle_speak(self, message):
        params = ["utterance"]
        #note: already saved as speak in skills_result, keeping for redundancy
        for name in params:
            self.context_dict[name] = message.data.get(name)
            self.signals_dict[name] = message.data.get(name)

        self.context_dict["last_spoken"] = self.context_dict["utterance"]
        self.abstract_dict["last_spoken"] = self.context_dict["utterance"]
        self.context_dict["last_spoken_timestamp"] = time.asctime()
        self.abstract_dict["last_spoken_timestamp"] = time.asctime()

    def handle_recognizer_loop_utterance(self, message):
        params = ["utterances","source"]
        for name in params:
            self.context_dict[name] = message.data.get(name)
            self.signals_dict[name] = message.data.get(name)

        self.context_dict["last_heard"] =self.context_dict["utterances"]
        self.abstract_dict["last_heard"] = self.context_dict["utterances"]
        self.context_dict["last_heard_timestamp"] = time.asctime()
        self.abstract_dict["last_heard_timestamp"] = time.asctime()

    def handle_intent_failure(self, message):
        self.context_dict["fails"] = self.context_dict["fails"]+1
        self.context_dict["last_fail"] = message.data.get("utteramce")
        self.signals_dict["fails"] = self.context_dict["fails"] + 1
        self.signals_dict["last_fail"] = message.data.get("utteramce")

    def handle_skill_results(self, message):
        key = message.data.get('skill_name') #must send results in skill, NOT default
        results = message.data
        self.context_dict[key] = results
        self.results_dict[key] = results
        #logger.info("Updated context for results from "+key)
        for result in results:
            params = [result]  # if you send a string instead it is taken like a list of chars
            if result not in self.vocab and result != "skill_name":
                self.register_context(params, type="skill_result")
            try:
                self.context_dict[result] = message.data[result]
                self.results_dict[result] = message.data[result]
                print result + " updated with " + self.context_dict[result]
            except:
                pass

        for regex in self.regex_dict:
            result = message.data.get(regex)
            if result is not None:
                self.get_regex_context(result, regex)

    def handle_key_context_request(self,message):
        key = message.data.get["key"]
        if key is not None:
            result = self.context_dict[key]
            #emit result
            client.emit(
                Message("context_key_result", {'key': key, "result":result }))

    def handle_key_context_type_request(self,message):
        key = message.data.get["key"]
        type = message.data.get["type"]
        if key is not None and type is not None:
            result = self.context_dict[key]
            if "type" == "abstract":
                result = self.abstract_dict[key]
            elif "type" == "signal":
                result = self.signals_dict[key]
            elif "type" == "intent":
                result = self.intents_dict[key]
            elif "type" == "regex":
                result = self.regex_dict[key]
            elif "type" == "skill":
                result = self.skills_dict[key]
            elif "type" == "skills_result":
                result = self.result_dict[key]
            elif "type" == "bluetooth":
                result = self.bluetooth_dict[key]
            #emit result
            client.emit(
                Message("context_key_result", {'key': key, "result":result , "type":type}))

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
