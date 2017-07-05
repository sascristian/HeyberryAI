# Konami Code Skill

this skill is meant to illustrate the IntentLayers Class

Upon sequential entry of konami code ( up, up, down, down, left, right, left, right, b, a) executes cheat_code.py

Wrong entry or timeout makes you start over

# usage

        up
        >> up

        up
        >> up

        down
        >> down

        down
        >> down

        left
        >> left

        right
        >> right

        left
        >> left

        right
        >> right

        b
        >> b

        a
        >> Cheat Code Unlocked
        >> God Mode Activated
        >> All right, I am looking for Konami Code
        >> The Konami Code  is a cheat code that appears in many Konami video games, although the code also appears in some non-Konami games.
        During the title screen before the game demo begins, the player could press the following sequence of buttons on the game controller to enable the cheat:
        ↑↑↓↓←→←→BA
        The code has also found a place in popular culture as a reference to the third generation of video game consoles.

# loading log

        2017-06-23 21:34:01,327 - mycroft.skills.core - INFO - ATTEMPTING TO LOAD SKILL: skill_konami_code
        2017-06-23 21:34:01,331 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "enable speak", "end": "SpeakEnableKeyword"}, "context": null}
        2017-06-23 21:34:01,333 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "speak disable", "end": "SpeakDisableKeyword"}, "context": null}
        2017-06-23 21:34:01,334 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "disable speak", "end": "SpeakDisableKeyword"}, "context": null}
        2017-06-23 21:34:01,336 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["SpeakEnableKeyword", "SpeakEnableKeyword"]], "optional": [], "name": "1:SpeakEnableIntent"}, "context": null}
        2017-06-23 21:34:01,343 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["SpeakDisableKeyword", "SpeakDisableKeyword"]], "optional": [], "name": "1:SpeakDisableIntent"}, "context": null}
        2017-06-23 21:34:01,344 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "when were you born", "end": "WhenWereYouBornKeyword"}, "context": null}
        2017-06-23 21:34:01,346 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "when were you created", "end": "WhenWereYouBornKeyword"}, "context": null}
        2017-06-23 21:34:01,348 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "where were you born", "end": "WhereWereYouBornKeyword"}, "context": null}
        2017-06-23 21:34:01,349 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "where were you created", "end": "WhereWereYouBornKeyword"}, "context": null}
        2017-06-23 21:34:01,353 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiUpIntent']
        2017-06-23 21:34:01,353 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiUpIntent']
        2017-06-23 21:34:01,353 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiDownIntent']
        2017-06-23 21:34:01,354 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiDownIntent']
        2017-06-23 21:34:01,354 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiLeftIntent']
        2017-06-23 21:34:01,354 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiRightIntent']
        2017-06-23 21:34:01,354 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiLeftIntent']
        2017-06-23 21:34:01,355 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiRightIntent']
        2017-06-23 21:34:01,355 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiBIntent']
        2017-06-23 21:34:01,355 - mycroft.skills.intent_service - INFO - Adding layer to tree ['KonamiAIntent']
        2017-06-23 21:34:01,355 - mycroft.skills.intent_service - INFO - Disabling intent layers
        2017-06-23 21:34:01,355 - mycroft.skills.intent_service - INFO - Deactivating Layer 0
        2017-06-23 21:34:01,355 - mycroft.skills.intent_service - INFO - Deactivating Layer 1
        2017-06-23 21:34:01,356 - mycroft.skills.intent_service - INFO - Deactivating Layer 2
        2017-06-23 21:34:01,356 - mycroft.skills.intent_service - INFO - Deactivating Layer 3
        2017-06-23 21:34:01,356 - mycroft.skills.intent_service - INFO - Deactivating Layer 4
        2017-06-23 21:34:01,357 - mycroft.skills.intent_service - INFO - Deactivating Layer 5
        2017-06-23 21:34:01,364 - mycroft.skills.intent_service - INFO - Deactivating Layer 6
        2017-06-23 21:34:01,365 - mycroft.skills.intent_service - INFO - Deactivating Layer 7
        2017-06-23 21:34:01,365 - mycroft.skills.intent_service - INFO - Deactivating Layer 8
        2017-06-23 21:34:01,367 - mycroft.skills.intent_service - INFO - Deactivating Layer 9
        2017-06-23 21:34:01,413 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "up", "end": "KonamiUpKeyword"}, "context": null}
        2017-06-23 21:34:01,413 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "right", "end": "KonamiRightKeyword"}, "context": null}
        2017-06-23 21:34:01,415 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "down", "end": "KonamiDownKeyword"}, "context": null}
        2017-06-23 21:34:01,417 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "a", "end": "KonamiAKeyword"}, "context": null}
        2017-06-23 21:34:01,418 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "left", "end": "KonamiLeftKeyword"}, "context": null}
        2017-06-23 21:34:01,419 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "b", "end": "KonamiBKeyword"}, "context": null}
        2017-06-23 21:34:01,420 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiUpKeyword", "KonamiUpKeyword"]], "optional": [], "name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:34:01,422 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiDownKeyword", "KonamiDownKeyword"]], "optional": [], "name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:34:01,423 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiLeftKeyword", "KonamiLeftKeyword"]], "optional": [], "name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:34:01,424 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiRightKeyword", "KonamiRightKeyword"]], "optional": [], "name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:34:01,425 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiBKeyword", "KonamiBKeyword"]], "optional": [], "name": "4:KonamiBIntent"}, "context": null}
        2017-06-23 21:34:01,426 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiAKeyword", "KonamiAKeyword"]], "optional": [], "name": "4:KonamiAIntent"}, "context": null}
        2017-06-23 21:34:01,427 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:34:01,428 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:34:01,431 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:34:01,432 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:34:01,436 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:34:01,437 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:34:01,440 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:34:01,441 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:34:01,444 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:34:01,445 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:34:01,447 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:34:01,448 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:34:01,454 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:34:01,455 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:34:01,458 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:34:01,458 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:34:01,461 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiBIntent"}, "context": null}
        2017-06-23 21:34:01,462 - mycroft.skills.core - DEBUG - Disabling intent KonamiBIntent
        2017-06-23 21:34:01,464 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiAIntent"}, "context": null}
        2017-06-23 21:34:01,465 - mycroft.skills.core - DEBUG - Disabling intent KonamiAIntent
        2017-06-23 21:34:01,469 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:34:01,470 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:34:01,471 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:34:01,471 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:34:01,472 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:34:01,473 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:34:01,474 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:34:01,475 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:34:01,476 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiBIntent"}, "context": null}
        2017-06-23 21:34:01,477 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiAIntent"}, "context": null}
        2017-06-23 21:34:01,669 - mycroft.skills.intent_service - INFO - Activating Layer 0
        2017-06-23 21:34:01,669 - mycroft.skills.core - INFO - Loaded skill_konami_code with ID 4
        2017-06-23 21:34:01,673 - Skills - DEBUG - {"type": "enable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:34:01,675 - mycroft.skills.core - INFO - Enabling Intent KonamiUpIntent

# usage logs

        2017-06-23 21:47:01,320 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["up"]}, "context": null}
        2017-06-23 21:47:01,330 - Skills - DEBUG - {"type": "4:KonamiUpIntent", "data": {"confidence": 1.0, "target": "cli", "mute": false, "intent_type": "4:KonamiUpIntent", "KonamiUpKeyword": "up", "utterance": "up"}, "context": {"target": "cli"}}
        2017-06-23 21:47:01,331 - mycroft.skills.intent_service - INFO - Going to next Tree Layer
        2017-06-23 21:47:01,331 - mycroft.skills.intent_service - INFO - Stopping previous timer
        2017-06-23 21:47:01,336 - mycroft.skills.intent_service - INFO - Disabling intent layers
        2017-06-23 21:47:01,337 - mycroft.skills.intent_service - INFO - Deactivating Layer 0
        2017-06-23 21:47:01,342 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:01,343 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:47:01,346 - mycroft.skills.intent_service - INFO - New Timer Started
        2017-06-23 21:47:01,346 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:01,347 - mycroft.skills.intent_service - INFO - Deactivating Layer 1
        2017-06-23 21:47:01,350 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:01,351 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:47:01,353 - mycroft.skills.intent_service - INFO - Deactivating Layer 2
        2017-06-23 21:47:01,354 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:01,356 - mycroft.skills.intent_service - INFO - Deactivating Layer 3
        2017-06-23 21:47:01,358 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:01,359 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:47:01,360 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:01,362 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:47:01,357 - mycroft.skills.intent_service - INFO - Deactivating Layer 4
        2017-06-23 21:47:01,365 - mycroft.skills.intent_service - INFO - Deactivating Layer 5
        2017-06-23 21:47:01,365 - mycroft.skills.intent_service - INFO - Deactivating Layer 6
        2017-06-23 21:47:01,371 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:01,373 - mycroft.skills.intent_service - INFO - Deactivating Layer 7
        2017-06-23 21:47:01,374 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:01,383 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:01,384 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:47:01,377 - mycroft.skills.intent_service - INFO - Deactivating Layer 8
        2017-06-23 21:47:01,385 - mycroft.skills.intent_service - INFO - Deactivating Layer 9
        2017-06-23 21:47:01,388 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:01,389 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:47:01,390 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:01,391 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:47:01,392 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:01,393 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:47:01,394 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:01,396 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiBIntent"}, "context": null}
        2017-06-23 21:47:01,396 - mycroft.skills.core - DEBUG - Disabling intent KonamiBIntent
        2017-06-23 21:47:01,398 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiAIntent"}, "context": null}
        2017-06-23 21:47:01,399 - mycroft.skills.core - DEBUG - Disabling intent KonamiAIntent
        2017-06-23 21:47:01,400 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:01,401 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:01,403 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:01,404 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiBIntent"}, "context": null}
        2017-06-23 21:47:01,440 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiAIntent"}, "context": null}
        2017-06-23 21:47:01,688 - mycroft.skills.intent_service - INFO - Activating Layer 1
        2017-06-23 21:47:01,692 - Skills - DEBUG - {"type": "enable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:01,698 - mycroft.skills.core - INFO - Enabling Intent KonamiUpIntent
        2017-06-23 21:47:01,699 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "up", "metadata": {"source_skill": "KonamiCode"}}, "context": null}
        2017-06-23 21:47:01,701 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiUpKeyword", "KonamiUpKeyword"]], "optional": [], "name": "4:KonamiUpIntent"}, "context": null}

        2017-06-23 21:47:03,954 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["up"]}, "context": null}
        2017-06-23 21:47:03,963 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 4, "utterances": ["up"]}, "context": null}
        2017-06-23 21:47:03,971 - Skills - DEBUG - {"type": "intent_request", "data": {"lang": "en-us", "utterance": "up"}, "context": null}
        2017-06-23 21:47:03,976 - Skills - DEBUG - {"type": "intent_response", "data": {"lang": "en-us", "skill_id": 4, "intent_name": "KonamiUpIntent", "utterance": "up"}, "context": null}
        2017-06-23 21:47:04,007 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 4, "result": false}, "context": null}
        2017-06-23 21:47:04,029 - Skills - DEBUG - {"type": "4:KonamiUpIntent", "data": {"confidence": 1.0, "target": "cli", "mute": false, "intent_type": "4:KonamiUpIntent", "KonamiUpKeyword": "up", "utterance": "up"}, "context": {"target": "cli"}}
        2017-06-23 21:47:04,029 - mycroft.skills.intent_service - INFO - Going to next Tree Layer
        2017-06-23 21:47:04,029 - mycroft.skills.intent_service - INFO - Stopping previous timer
        2017-06-23 21:47:04,034 - mycroft.skills.intent_service - INFO - Disabling intent layers
        2017-06-23 21:47:04,035 - mycroft.skills.intent_service - INFO - Deactivating Layer 0
        2017-06-23 21:47:04,037 - mycroft.skills.intent_service - INFO - Deactivating Layer 1
        2017-06-23 21:47:04,037 - mycroft.skills.intent_service - INFO - Deactivating Layer 2
        2017-06-23 21:47:04,039 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:04,041 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:47:04,043 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:04,044 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:47:04,045 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:04,046 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:04,047 - mycroft.skills.intent_service - INFO - Deactivating Layer 3
        2017-06-23 21:47:04,048 - mycroft.skills.intent_service - INFO - Deactivating Layer 4
        2017-06-23 21:47:04,048 - mycroft.skills.intent_service - INFO - Deactivating Layer 5
        2017-06-23 21:47:04,049 - mycroft.skills.intent_service - INFO - Deactivating Layer 6
        2017-06-23 21:47:04,050 - mycroft.skills.intent_service - INFO - Deactivating Layer 7
        2017-06-23 21:47:04,050 - mycroft.skills.intent_service - INFO - Deactivating Layer 8
        2017-06-23 21:47:04,052 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:04,054 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:47:04,055 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:04,056 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:47:04,058 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:04,051 - mycroft.skills.intent_service - INFO - Deactivating Layer 9
        2017-06-23 21:47:04,059 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:47:04,061 - mycroft.skills.intent_service - INFO - New Timer Started
        2017-06-23 21:47:04,062 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:04,063 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:47:04,065 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:04,065 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:47:04,067 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:04,067 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:47:04,069 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiBIntent"}, "context": null}
        2017-06-23 21:47:04,069 - mycroft.skills.core - DEBUG - Disabling intent KonamiBIntent
        2017-06-23 21:47:04,076 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:04,111 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:04,112 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:04,113 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiAIntent"}, "context": null}
        2017-06-23 21:47:04,115 - mycroft.skills.core - DEBUG - Disabling intent KonamiAIntent
        2017-06-23 21:47:04,117 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:04,119 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:04,120 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:04,121 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiBIntent"}, "context": null}
        2017-06-23 21:47:04,122 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiAIntent"}, "context": null}
        2017-06-23 21:47:04,361 - mycroft.skills.intent_service - INFO - Activating Layer 2
        2017-06-23 21:47:04,365 - Skills - DEBUG - {"type": "enable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:04,368 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "up", "metadata": {"source_skill": "KonamiCode"}}, "context": null}
        2017-06-23 21:47:04,369 - mycroft.skills.core - INFO - Enabling Intent KonamiDownIntent
        2017-06-23 21:47:04,371 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiDownKeyword", "KonamiDownKeyword"]], "optional": [], "name": "4:KonamiDownIntent"}, "context": null}

        2017-06-23 21:47:06,657 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["down"]}, "context": null}
        2017-06-23 21:47:06,707 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 4, "utterances": ["down"]}, "context": null}
        2017-06-23 21:47:06,717 - Skills - DEBUG - {"type": "intent_request", "data": {"lang": "en-us", "utterance": "down"}, "context": null}
        2017-06-23 21:47:06,909 - Skills - DEBUG - {"type": "intent_response", "data": {"lang": "en-us", "skill_id": 4, "intent_name": "KonamiDownIntent", "utterance": "down"}, "context": null}
        2017-06-23 21:47:07,033 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 4, "result": false}, "context": null}
        2017-06-23 21:47:07,040 - Skills - DEBUG - {"type": "4:KonamiDownIntent", "data": {"confidence": 1.0, "target": "cli", "mute": false, "intent_type": "4:KonamiDownIntent", "utterance": "down", "KonamiDownKeyword": "down"}, "context": {"target": "cli"}}
        2017-06-23 21:47:07,041 - mycroft.skills.intent_service - INFO - Going to next Tree Layer
        2017-06-23 21:47:07,041 - mycroft.skills.intent_service - INFO - Stopping previous timer
        2017-06-23 21:47:07,046 - mycroft.skills.intent_service - INFO - Disabling intent layers
        2017-06-23 21:47:07,048 - mycroft.skills.intent_service - INFO - Deactivating Layer 0
        2017-06-23 21:47:07,063 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:07,065 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:47:07,069 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:07,070 - mycroft.skills.intent_service - INFO - Deactivating Layer 1
        2017-06-23 21:47:07,071 - mycroft.skills.intent_service - INFO - Deactivating Layer 2
        2017-06-23 21:47:07,071 - mycroft.skills.intent_service - INFO - Deactivating Layer 3
        2017-06-23 21:47:07,072 - mycroft.skills.intent_service - INFO - Deactivating Layer 4
        2017-06-23 21:47:07,072 - mycroft.skills.intent_service - INFO - Deactivating Layer 5
        2017-06-23 21:47:07,073 - mycroft.skills.intent_service - INFO - Deactivating Layer 6
        2017-06-23 21:47:07,073 - mycroft.skills.intent_service - INFO - Deactivating Layer 7
        2017-06-23 21:47:07,080 - mycroft.skills.intent_service - INFO - Deactivating Layer 8
        2017-06-23 21:47:07,080 - mycroft.skills.intent_service - INFO - New Timer Started
        2017-06-23 21:47:07,081 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:07,084 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:47:07,088 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:07,089 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:07,090 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:07,091 - mycroft.skills.intent_service - INFO - Deactivating Layer 9
        2017-06-23 21:47:07,092 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:47:07,092 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:47:07,099 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:47:07,101 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:07,103 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:47:07,105 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:07,109 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:47:07,118 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:07,125 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiBIntent"}, "context": null}
        2017-06-23 21:47:07,126 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:47:07,127 - mycroft.skills.core - DEBUG - Disabling intent KonamiBIntent
        2017-06-23 21:47:07,130 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:07,134 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:07,138 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:07,140 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiAIntent"}, "context": null}
        2017-06-23 21:47:07,141 - mycroft.skills.core - DEBUG - Disabling intent KonamiAIntent
        2017-06-23 21:47:07,145 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:07,147 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:07,151 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:07,153 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:07,154 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiBIntent"}, "context": null}
        2017-06-23 21:47:07,183 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiAIntent"}, "context": null}
        2017-06-23 21:47:07,397 - mycroft.skills.intent_service - INFO - Activating Layer 3
        2017-06-23 21:47:07,402 - Skills - DEBUG - {"type": "enable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:07,404 - mycroft.skills.core - INFO - Enabling Intent KonamiDownIntent
        2017-06-23 21:47:07,405 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "down", "metadata": {"source_skill": "KonamiCode"}}, "context": null}
        2017-06-23 21:47:07,444 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiDownKeyword", "KonamiDownKeyword"]], "optional": [], "name": "4:KonamiDownIntent"}, "context": null}

        2017-06-23 21:47:09,734 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["left"]}, "context": null}
        2017-06-23 21:47:09,743 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 4, "utterances": ["left"]}, "context": null}
        2017-06-23 21:47:09,753 - Skills - DEBUG - {"type": "intent_request", "data": {"lang": "en-us", "utterance": "left"}, "context": null}
        2017-06-23 21:47:09,775 - mycroft.skills.intent_service - ERROR -
        Traceback (most recent call last):
          File "/home/user/jarbas_stable/JarbasAI/mycroft/skills/intent_service.py", line 108, in handle_intent_request
            normalize(utterance, lang), 100))
        StopIteration
        2017-06-23 21:47:09,850 - Skills - DEBUG - {"type": "intent_response", "data": {"lang": "en-us", "skill_id": 0, "intent_name": "", "utterance": "left"}, "context": null}
        2017-06-23 21:47:09,921 - KonamiCode - INFO - Wrong cheat code entry, reseting layers
        2017-06-23 21:47:09,943 - mycroft.skills.intent_service - INFO - Reseting Tree
        2017-06-23 21:47:09,944 - mycroft.skills.intent_service - INFO - Stopping previous timer
        2017-06-23 21:47:09,944 - mycroft.skills.intent_service - INFO - Disabling intent layers
        2017-06-23 21:47:09,944 - mycroft.skills.intent_service - INFO - Deactivating Layer 0
        2017-06-23 21:47:09,945 - mycroft.skills.intent_service - INFO - Deactivating Layer 1
        2017-06-23 21:47:09,945 - mycroft.skills.intent_service - INFO - Deactivating Layer 2
        2017-06-23 21:47:09,946 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:09,947 - mycroft.skills.intent_service - INFO - Deactivating Layer 3
        2017-06-23 21:47:09,947 - mycroft.skills.intent_service - INFO - Deactivating Layer 4
        2017-06-23 21:47:09,948 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:09,949 - mycroft.skills.intent_service - INFO - Deactivating Layer 5
        2017-06-23 21:47:09,951 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:09,951 - mycroft.skills.intent_service - INFO - Deactivating Layer 6
        2017-06-23 21:47:09,952 - mycroft.skills.intent_service - INFO - Deactivating Layer 7
        2017-06-23 21:47:09,953 - mycroft.skills.intent_service - INFO - Deactivating Layer 8
        2017-06-23 21:47:09,954 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:09,954 - mycroft.skills.intent_service - INFO - Deactivating Layer 9
        2017-06-23 21:47:09,960 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:09,989 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:47:09,998 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:09,999 - mycroft.skills.core - DEBUG - Disabling intent KonamiUpIntent
        2017-06-23 21:47:10,000 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:47:10,000 - mycroft.skills.core - DEBUG - Disabling intent KonamiDownIntent
        2017-06-23 21:47:10,000 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:47:10,003 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:10,005 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:10,006 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:47:10,006 - mycroft.skills.core - DEBUG - Disabling intent KonamiLeftIntent
        2017-06-23 21:47:10,011 - mycroft.skills.core - DEBUG - Disabling intent KonamiRightIntent
        2017-06-23 21:47:10,012 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiBIntent"}, "context": null}
        2017-06-23 21:47:10,013 - mycroft.skills.core - DEBUG - Disabling intent KonamiBIntent
        2017-06-23 21:47:10,015 - Skills - DEBUG - {"type": "disable_intent", "data": {"intent_name": "KonamiAIntent"}, "context": null}
        2017-06-23 21:47:10,016 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:10,017 - mycroft.skills.core - DEBUG - Disabling intent KonamiAIntent
        2017-06-23 21:47:10,018 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:10,023 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:10,024 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiDownIntent"}, "context": null}
        2017-06-23 21:47:10,030 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:10,031 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:10,032 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiLeftIntent"}, "context": null}
        2017-06-23 21:47:10,070 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiRightIntent"}, "context": null}
        2017-06-23 21:47:10,110 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiBIntent"}, "context": null}
        2017-06-23 21:47:10,165 - Skills - DEBUG - {"type": "detach_intent", "data": {"intent_name": "4:KonamiAIntent"}, "context": null}
        2017-06-23 21:47:10,277 - mycroft.skills.intent_service - INFO - Activating Layer 0
        2017-06-23 21:47:10,391 - Skills - DEBUG - {"type": "enable_intent", "data": {"intent_name": "KonamiUpIntent"}, "context": null}
        2017-06-23 21:47:10,394 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 4, "result": false}, "context": null}
        2017-06-23 21:47:10,394 - mycroft.skills.core - INFO - Enabling Intent KonamiUpIntent
        2017-06-23 21:47:10,395 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["KonamiUpKeyword", "KonamiUpKeyword"]], "optional": [], "name": "4:KonamiUpIntent"}, "context": null}


# problems

too much normalization does not allow "a" to trigger in standard mycroft

# changing cheat code

just edit the method execute_cheat_code in cheat_code.py