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
        Objective_Registered - context for registered objectives
        ExecuteObjectiveIntent - context for last executed objective
        
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

Warning: updates core.py to add results property and adapt context manager to all skills

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

check [example skill](https://github.com/JarbasAI/jarbas-core/tree/dev/mycroft/skills/ContextManagerTest)

in this case asking mycroft for context test will output the following, after having searched wikipedia for god and pictures of dinosaur

        2017-02-26 23:35:42,333 - CLIClient - INFO - Speak: An error occurred while processing a request in ContextSkill

        Input: context test
        2017-02-26 23:37:51,564 - CLIClient - INFO - Speak: the following contexts are available in adapt context manager
        2017-02-26 23:37:57,360 - CLIClient - INFO - Speak: ArticleTitle has value god
        2017-02-26 23:38:00,873 - CLIClient - INFO - Speak: Search has value dinosaur

        Input: personal context
        2017-02-26 23:38:16,144 - CLIClient - INFO - Speak: the following manually adquired contexts are available
        2017-02-26 23:38:21,399 - CLIClient - INFO - Speak: name context has value jarbas
        2017-02-26 23:38:24,697 - CLIClient - INFO - Speak: language context has value english
        2017-02-26 23:38:28,172 - CLIClient - INFO - Speak: last_heard_timestamp context has value Sun Feb 26 23:37:50 2017
        2017-02-26 23:38:40,443 - CLIClient - INFO - Speak: last_spoken_timestamp context has value Sun Feb 26 23:35:01 2017
        2017-02-26 23:38:52,079 - CLIClient - INFO - Speak: last_spoken context has value An error occurred while processing a request in ContextSkill
        2017-02-26 23:38:59,956 - CLIClient - INFO - Speak: last_heard context has value [u'context test']
        2017-02-26 23:39:04,435 - CLIClient - INFO - Speak: location context has value internet
        2017-02-26 23:39:08,279 - CLIClient - INFO - Speak: start up time context has value 1488169816.89


#author

jarbas

#aknowledgments

Thx mycroft team