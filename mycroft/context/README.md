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

# usage

run main.py

# install

clone repo into mycroft-core folder

#author

jarbas

#aknowledgments

Thx mycroft team