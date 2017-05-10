# mycroft intent layer and intent parser


These are tools meant to help give state to mycroft

IntentLayer ->  enable and disable more intents as appropriate

IntentParser -> determine intents from utterances from inside any skill, get skill id for intent name


# install

packaged as a skill for easy install

Intent Layer requires the following changes, either add these methods in core.py or inside the skill


            def bind(self, emitter):
                if emitter:
                    self.emitter = emitter
                    self.enclosure = EnclosureAPI(emitter)
                    self.__register_stop()
                    self.emitter.on('enable_intent', self.handle_enable_intent)
                    self.emitter.on('disable_intent', self.handle_disable_intent)

            def disable_intent(self, intent_name):
                """Disable a registered intent"""
                self.emitter.emit(Message("disable_intent", {"intent_name": intent_name}))

            def enable_intent(self, intent_name):
                """Reenable a registered self intent"""
                self.emitter.emit(Message("enable_intent", {"intent_name": intent_name}))

            def handle_enable_intent(self, message):
                intent_name = message.data["intent_name"]
                for (name, intent) in self.registered_intents:
                    if name == intent_name:
                        self.registered_intents.remove((name, intent))
                        intent.name = name
                        self.register_intent(intent, None)
                        logger.info("Enabling Intent " + intent_name)
                        return
                logger.error("Could not Re-enable Intent " + intent_name)

            def handle_disable_intent(self, message):
                intent_name = message.data["intent_name"]
                logger.debug('Disabling intent ' + intent_name)
                name = str(self.skill_id) + ':' + intent_name
                self.emitter.emit(Message("detach_intent", {"intent_name": name}))


Intent Parser requires following additions to intent class, assumes you have converse method PR for skill_id

                in __init__ method add
                      self.emitter.on('intent_request', self.handle_intent_request)
                      self.emitter.on('intent_to_skill_request', self.handle_intent_to_skill_request)

                def handle_intent_request(self, message):
                    utterance = message.data["utterance"]
                    # Get language of the utterance
                    lang = message.data.get('lang', None)
                    if not lang:
                        lang = "en-us"
                    best_intent = None
                    try:
                        # normalize() changes "it's a boy" to "it is boy", etc.
                        best_intent = next(self.engine.determine_intent(
                            normalize(utterance, lang), 100))

                        # TODO - Should Adapt handle this?
                        best_intent['utterance'] = utterance
                    except StopIteration, e:
                        logger.exception(e)

                    if best_intent and best_intent.get('confidence', 0.0) > 0.0:
                        skill_id = int(best_intent['intent_type'].split(":")[0])
                        intent_name = best_intent['intent_type'].split(":")[1]
                        self.emitter.emit(Message("intent_response", {
                            "skill_id": skill_id, "utterance": utterance, "lang": lang, "intent_name":intent_name}))
                        return
                    self.emitter.emit(Message("intent_response", {
                        "skill_id": 0, "utterance": utterance, "lang": lang, "intent_name": ""}))


                  def handle_intent_to_skill_request(self, message):
                        intent = message.data["intent_name"]
                        for id in self.skill_ids:
                            for name in self.skill_ids[id]:
                                if name == intent:
                                    self.emitter.emit(Message("intent_to_skill_response", {
                                        "skill_id": id, "intent_name": intent}))
                                    return id
                        self.emitter.emit(Message("intent_to_skill_response", {
                            "skill_id": 0, "intent_name": intent}))
                        return 0


# Usage

inside skill where you want to use it do

            # this is to add skills folder to import path, you need this skill in there
            import sys
            from os.path import dirname
            sys.path.append(dirname(dirname(__file__)))
            from service_intent_layer import IntentLayer, IntentParser

# Intent Parsing inside skills

with some changes to IntentService class we can now determine intents for utterances, and get source skill for intents

            in initialize -> self.intent_parser = IntentParser(self.emitter)

            on converse method -> get intent instead of manually parsing utterance
                def converse(self, transcript, lang="en-us"):
                     # check if some of the intents will be handled
                    intent, id = self.intent_parser.determine_intent(transcript[0])
                    if id != self.skill_id:
                        # no longer inside this conversation
                        skill_id = self.intent_parser.get_skill_id(intent)
                        # utterance will be handled by skill_id
                        if self.intercept_flag:
                            # dont let intent class handle this if you dont want to
                            return True
                    return False


# Coding States - Intent Layerss

Each state has different intents available to be executed

[Konami Code Example](https://github.com/JarbasAI/jarbas-core/blob/dev/mycroft/skills/konami_code/__init__.py) - layers with a single intent

            in initialize

            layers = [["KonamiUpIntent"], ["KonamiUpIntent"], ["KonamiDownIntent"], ["KonamiDownIntent"],
                    ["KonamiLeftIntent"], ["KonamiRightIntent"], ["KonamiLeftIntent"], ["KonamiRightIntent"],
                    ["KonamiBIntent"], ["KonamiAIntent"]]

            # 60 is the number of seconds for the layer timer
            self.layers = IntentLayer(self.emitter, layers, 60)

            to activate next layer/state -> self.layers.next()
            to activate previous layer/state -> self.layers.previous()
            to activate layer/state 0 -> self.layers.reset()
            to get current layer/state -> state = self.layers.current_layer

            each tree has a timer, after changing state this timer starts and at the end resets the tree
            to disable timer, after doing next/previous -> self.layers.stop_timer()

            to go directly to a layer do -> self.tree.activate_layer(layer_num)
            in this case no timer is started so you should also do - > self.layers.start_timer()

            on converse -> parse intent/utterance and manipulate layers if needed (bad sequence)


# Multiple Intent Layers

"Trees" can be made by making a IntentLayer for each intent, we can use layers as branches and do

            self.branch = IntentLayer(self.emitter, layers, 60)
            self.branch.disable()

and to activate later when needed

            self.branch.reset()

intent parsing in converse method can manipulate correct tree branch if needed

this allows for much more complex skills with each intent triggering their own sub-intents / sub - trees

on demand manipulation of tree layers may also open several unforeseen opportunities for intent data structures

            self.branch.add_layer([intent_list])
            self.branch.remove_layer(layer_num)
            self.branch.replace_layer(self, layer_num, intent_list)
            list_of_layers_with_this_intent_on_it = self.branch.find_layer(self, intent_list)

