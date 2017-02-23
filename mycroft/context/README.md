# context manager service

listens on message bus for signals and keeps track of context

requests context update from services

on request emits current context to bus

# relevant signals

        speak - last spoken sentence
        utterance - last heard/received sentence
        results - results property from skills
        intent_failure - number of un-recognized intents
        freewill_result - context from freewill service
        vision_result - context from vision service
        register_vocab - context for all regex expressions in skills

# usage

run main.py

# dev usage
        WORK IN PROGRESS
        dont know how to register context with adapt yet, this seems to be the wrong place
check [intent skill](https://github.com/JarbasAI/jarbas-core/blob/dev/mycroft/skills/intent/__init__.py)

# install

clone repo into mycroft-core folder

#author

jarbas

#aknowledgments

Thx mycroft team