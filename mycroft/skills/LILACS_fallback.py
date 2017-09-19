from mycroft.skills.core import FallbackSkill
from jarbas_utils.skill_dev_tools import ResponderBackend
from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message
from os.path import dirname


class LILACSFallback(FallbackSkill):
    lilacs_folders = {}
    order = ["dbpedia", "wikipedia", "wikidata", "duckduckgo", "conceptnet",
             "wordnik", "wikihow", "wolframalpha"]

    def __init__(self, name=""):
        super(LILACSFallback, self).__init__(name=name)
        self.request_type = self.name + ".request"
        self.responder = None
        self.active = False
        self.LILACS_data = {}
        self.relevant_data = ["CenterNode", "TargetNode", "LastConcept",
                              "TargetKeyword", "QuestionType"]

    @classmethod
    def make_LILACS_handler(cls, ws):
        """Goes through all fallback handlers until one returns True"""

        def handler(message):
            # try fallbacks in ordered list
            for folder in cls.order:
                for f in cls.lilacs_folders.keys():
                    if folder == f:
                        handler = cls.lilacs_folders[f]
                        try:
                            handler.__self__.handle_update_message_context(
                                message)
                            if handler(message):
                                return True
                        except Exception as e:
                            pass
            return False

        return handler

    @classmethod
    def _register_lilacs(cls, handler, skill_folder=None):
        """
        Register a function to be called as a lilacs fallback
        Fallback should receive message and return
        a boolean (True if succeeded or False if failed)

        """
        skill_folder = skill_folder.split("/")[-1]
        cls.lilacs_folders[skill_folder] = handler

    def register_lilacs(self, handler):
        """
            register a fallback with the list of fallback handlers
            and with the list of handlers registered by this instance
        """
        self.instance_fallback_handlers.append(handler)
        # folder path
        try:
            skill_folder = self._dir
        except:
            skill_folder = dirname(__file__)  # skill
        self._register_lilacs(handler, skill_folder)

    def initialize(self):
        self.responder = ResponderBackend(self.name, self.emitter, self.log)
        self.responder.set_response_handler(self.request_type,
                                            self._handle_ask)
        test_intent = IntentBuilder("Test" + self.name + "Intent") \
            .require(self.name + "Keyword").optionally("TargetKeyword") \
            .require("TestKeyword").build()
        self.register_intent(test_intent, self.handle_test_intent)

        test_intent = IntentBuilder("Test" + self.name + "sIntent") \
            .require("SourceKeyword").optionally("TargetKeyword")
        self.register_intent(test_intent,
                             self._handle_check_source)

        self.start_up()

        self.emitter.on("LILACS.fallback.enable", self._LILACS_activate)
        self.emitter.on("LILACS.fallback.disable", self._LILACS_deactivate)
        self.emitter.on("add_context", self.handle_add_context)
        self.emitter.on("remove_context", self.handle_remove_context)
        self.register_lilacs(self._handle_fallback)

    def _handle_check_source(self, message):
        source = message.data.get("SourceKeyword", "")
        if source == self.name:
            self.handle_test_intent(message)

    def _LILACS_activate(self, message):
        fallback = message.data.get("name", "")
        if fallback == self.name:
            self.active = True

    def _LILACS_deactivate(self, message):
        fallback = message.data.get("name", "")
        if fallback == self.name:
            self.active = False

    def start_up(self):
        ''' additional things to do in initialize '''
        pass

    def _handle_fallback(self, message):
        ''' activate depending on LILACS_core and inject data '''
        if self.active:
            for context in self.LILACS_data.keys():
                message.data[context] = self.LILACS_data[context]
            return self.handle_fallback(message)
        return False

    def handle_fallback(self, message):
        ''' answer lilacs fallback query, return True if answered
        when lilacs fails to answer from nodes in memory this will be
        triggered in all fallbacks '''
        return False

    def handle_test_intent(self, message):
        ''' test this fallback intent  '''
        ### get subject for test and update context###
        node = message.data.get("TargetKeyword",
                                message.data.get("LastConcept", "god"))
        self.set_context("LastConcept", node)

        ### adquire result with internal method for testing ###
        result = self._adquire(node).get(self.name)
        if not result:
            self.speak("Could not get info about " + node + " from " +
                       self.name)
            return

        ### speak back data
        self.speak(self.name + " seems to work ")
        self.speak(str(result))

    def get_data(self, subject):
        ''' implement getting a dict of parsed data from this backend,
        this will be returned to LILACS queries '''
        node_data = {}
        return node_data

    def get_connections(self, subject):
        ''' implement getting a dict of parsed connections from this backend,
        this will be returned to LILACS queries '''
        node_cons = {}
        return node_cons

    def _handle_ask(self, message):
        ''' Responder for LILACS queries '''
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword", message.data.get(
            "LastConcept", "god"))
        self.set_context("LastConcept", node)
        result = self._adquire(node).get(self.name, {})
        self.responder.update_response_data(result, self.message_context)

    def _adquire(self, subject):
        ''' call get data '''
        self.log.info(self.name + '_Adquire')
        result = {self.name: {"node_dict": {}}}
        if subject is None:
            self.log.error("No subject to _adquire knowledge about")
        else:
            try:
                node_data = self.get_data(subject)
                node_connections = self.get_connections(subject)
                node_dict = {"name": subject, "data": node_data,
                             "connections": node_connections}
                result[self.name]["node_dict"] = node_dict
                self.emitter.emit(Message("LILACS.node.update",
                                          {"node_dict": node_dict}))
            except Exception as e:
                self.log.warning(
                    "Could not parse " + self.name + " for " + str(subject))
                self.log.error(str(e))
        return result

    def handle_add_context(self, message):
        ''' parse relevant contexts '''
        context = message.data.get("context", "")
        word = message.data.get("word", "")
        if context in self.relevant_data:
            self.LILACS_data[context] = word

    def handle_remove_context(self, message):
        ''' remove relevant contexts '''
        context = message.data.get("context", "")
        if context in self.LILACS_data.keys():
            self.LILACS_data.pop(context)

    def update_node(self, node_name, node_data=None, node_connections=None,
                    node_type="info"):
        ''' updates node in LILACS_core memory '''
        if node_data is None:
            node_data = {}
        if node_connections is None:
            node_connections = {}
        node_dict = {"name": node_name, "data": node_data, "connections":
            node_connections, "type": node_type}
        self.emitter.emit(Message("LILACS.node.update", {"node_dict":
                                                             node_dict}))
