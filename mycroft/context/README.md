# context manager service

listens on message bus for signals and keeps track of context

requests context update from services

on request emits current context to bus

# relevant signals

        Listens to:
        
        speak - last spoken sentence
        recognizer_loop:utterance - last heard/received sentence
        results - context for results property from skills
        intent_failure - context for number of un-recognized intents
        freewill_result - context from freewill service
        vision_result - context from vision service
        register_vocab - context for all regex expressions in skills
        skill_loaded - context for available skills
        register_intent - context for registered intents
        
        Responds to:
        
        context_request - emits full context 
        context_key_request - emits result of requested context
        context_key_override - changes context to desired value
        
        Emits:
        
        context_key_result - Message("context_key_result", {'key': key, "result":result }))
        context_result - Message("context_result", {'dictionary': self.context_dict}))


# usage

run main.py

# install

clone repo into mycroft-core folder

Warning: updates core.py to add results property 
Warning: updates wikipedia skill to add example usage of results

# dev usage

**ContextService consumes the results from all skills**

for regex context registering when handling intent add the following (wikipedia case)
        
        title = message.data.get("ArticleTitle")
        self.add_result("ArticleTitle",title)

only when you want the results are emitted, so you need the following call when your results are ready, usually at the end of intent handling

        self.emit_results()

the ArticleTitle context in ContextService is now updated with the user inputed value

**Requesting Context from ContextService**

check [example skill](https://github.com/JarbasAI/jarbas-core/tree/dev/mycroft/skills/ContextManagerTest) that registers all regex contexts from ContextService,

in this case asking mycroft for context test will output the following, after having searched wikipedia for dinosaurs

        2017-02-26 21:36:44,226 - CLIClient - INFO - Speak: the following contexts are available in adapt context manager
        2017-02-26 21:36:51,553 - CLIClient - INFO - Speak: ArticleTitle
        2017-02-26 21:36:54,892 - CLIClient - INFO - Speak: dinosaurs

still struggling a bit with adapt context manager integation, example skill needs to be polished , consider it a proof of concept only, yet to be integrated in adapt

#author

jarbas

#aknowledgments

Thx mycroft team