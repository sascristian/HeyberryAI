# List of all bus message types

WIP, this is a work in progress

# intent execution

    intent.execution.start - tell an intent started executing
    intent.execution.error - tell an intent errored during executing
    intent.execution.end - tell an intent finished executing

# converse method

    skill.converse.request - request converse method from skill
    skill.converse.response - response to converse method request
    active_skill_request - put a skill in converse skills list

# intent parser

    intent_request - request which intent an utterance will trigger
    intent_response - response to intent an utterance will trigger
    intent_to_skill_request - request  which skill this intent will trigger
    intent_to_skill_response - response to skill this intent will trigger

# skill control

    loaded_skills_request - request loaded skill manifest
    loaded_skills_response - response to loaded skill manifest
    shutdown_skill_request - request shutdown of skill
    shutdown_skill_response - status of shutdown skill operation
    reload_skill_request - request reload of skill
    reload_skill_response - status of reload skill operation

# intent control

    TODO enable / disable / register / vocab messages

# objectives messages

    TODO objectives service messages

# recognizer:loop

    TODO all voice reconition messages

# audio service

    speak - execute Text-To-Speech
    TODO all audio service messages

# display service

    TODO all display service messages

# context

    TODO all context manager messages

# configuration

    TODO all configuration messages

# enclosure api

    TODO all enclosure api messages

# browser service messages

    TODO message for all browser operations

# jarbas services messages

    TODO message for all individual skill operations, make own section for important skills