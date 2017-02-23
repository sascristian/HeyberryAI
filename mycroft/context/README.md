# context manager service

listens on message bus for signals and keeps track of context

requests context update from services

on request emits current context to bus

# relevant signals

        speak - last spoken sentence
        utterance - last heard/received sentence
        results - context for results property from skills
        intent_failure - context for number of un-recognized intents
        freewill_result - context from freewill service
        vision_result - context from vision service
        register_vocab - context for all regex expressions in skills
        loaded_skills - context for available skills

# usage

run main.py

# install

clone repo into mycroft-core folder

#author

jarbas

#aknowledgments

Thx mycroft team