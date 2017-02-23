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
        context_key_result - emits result of requested context
        context_key_override - changes context to desired value


# usage

run main.py

# install

clone repo into mycroft-core folder

Warning: updates core.py to add results property 
Warning: updates wikipedia skill to add example usage of results

#author

jarbas

#aknowledgments

Thx mycroft team