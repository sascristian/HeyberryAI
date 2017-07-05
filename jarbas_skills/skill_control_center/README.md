# Control Center Skill

Control which skills are active at any point, enforce run level at start-up

Skill names are rated and matched using fuzzy match, ratings bellow 60 wont be considered

# TODO

Change config values at runtime, voice showcase and selection

# usage

        number of loaded skills
        >> Number of loaded skills: 5

        skill manifest
        >> Loaded skills manifest. skill hello world, skill control center, skill personal, service objectives, skill mute

        current run level
        >> Currently at full run level

        go to level dev
        >> Changing run level to dev
        >> Run level changed

        unloaded skill manifest
        >> Unloaded skills manifest. skill hello world, service objectives, skill mute

        number of unloaded skills
        >> Number of unloaded skills: 3

        skill manifest
        >> Loaded skills manifest. skill personal, skill control center

        hello world
        2017-06-23 18:50:33,418 - Skills - DEBUG - {"type": "intent_failure", "data": {"lang": "en-us", "utterance": "hello world"}, "context": null}

        who are you
        >> My name is Jarbas and I'm an intelligent personal assistant

        shutdown personal skill
        >> Requesting shutdown of personal
        >> skill personal successfully shutdown

        who are you
        2017-06-23 18:51:37,539 - Skills - DEBUG - {"type": "intent_failure", "data": {"lang": "en-us", "utterance": "who are you"}, "context": null}

        reload personal skill
        >> Requesting reload of personal
        >> skill personal successfully reloaded

        who are you
        >> My name is Jarbas and I'm an intelligent personal assistant

        reload jhilh skill
        >> Requesting reload of jhilh
        >> I dont know that skill

        shutdown control center skill
        >> Requesting shutdown of control center
        >> skill control center shutdown is forbidden

        reload control center skill
        >> Requesting reload of control center
        >> skill control center reload is forbidden

# bad skill name logs

        2017-06-23 19:46:04,217 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["reload jhilh skill"]}, "context": null}
        2017-06-23 19:46:04,225 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 4, "utterances": ["reload jhilh skill"]}, "context": null}
        2017-06-23 19:46:04,228 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 4, "result": false}, "context": null}
        2017-06-23 19:46:04,243 - Skills - DEBUG - {"type": "4:SkillReloadIntent", "data": {"confidence": 0.25, "target": "cli", "mute": false, "intent_type": "4:SkillReloadIntent", "utterance": "reload jhilh skill", "Skill_Reload": "jhilh"}, "context": {"target": "cli"}}
        2017-06-23 19:46:04,246 - Skills - DEBUG - {"type": "loaded_skills_request", "data": {}, "context": null}
        2017-06-23 19:46:04,251 - Skills - DEBUG - {"type": "loaded_skills_response", "data": {"skills": [{"folder": "skill_hello_world", "name": "HelloWorldSkill", "id": 5}, {"folder": "skill_control_center", "name": "ControlCenterSkill", "id": 4}, {"folder": "skill_personal", "name": "PersonalSkill", "id": 3}, {"folder": "service_objectives", "name": "ObjectivesSkill", "id": 2}, {"folder": "skill_mute", "name": "MuteSkill", "id": 1}]}, "context": null}
        2017-06-23 19:46:04,345 - ControlCenterSkill - DEBUG - rating skill_hello_world:27
        2017-06-23 19:46:04,346 - ControlCenterSkill - DEBUG - rating skill_control_center:16
        2017-06-23 19:46:04,346 - ControlCenterSkill - DEBUG - rating skill_personal:21
        2017-06-23 19:46:04,347 - ControlCenterSkill - DEBUG - rating service_objectives:9
        2017-06-23 19:46:04,348 - ControlCenterSkill - DEBUG - rating skill_mute:27
        2017-06-23 19:46:04,349 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "Requesting reload of jhilh", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}
        2017-06-23 19:46:04,349 - ControlCenterSkill - ERROR - I dont know that skill
        2017-06-23 19:46:04,353 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "I dont know that skill", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}


# forbidden shutdown logs

        2017-06-23 20:28:07,702 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 4, "utterances": ["shutdown control center skill"]}, "context": null}
        2017-06-23 20:28:07,705 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 4, "result": false}, "context": null}
        2017-06-23 20:28:07,712 - Skills - DEBUG - {"type": "4:SkillShutdownIntent", "data": {"confidence": 0.25, "target": "cli", "mute": false, "intent_type": "4:SkillShutdownIntent", "Skill_Shutdown": "control center", "utterance": "shutdown control center skill"}, "context": {"target": "cli"}}
        2017-06-23 20:28:07,715 - Skills - DEBUG - {"type": "loaded_skills_request", "data": {}, "context": null}
        2017-06-23 20:28:07,720 - Skills - DEBUG - {"type": "loaded_skills_response", "data": {"skills": [{"folder": "skill_hello_world", "name": "HelloWorldSkill", "id": 5}, {"folder": "skill_control_center", "name": "ControlCenterSkill", "id": 4}, {"folder": "skill_personal", "name": "PersonalSkill", "id": 3}, {"folder": "service_objectives", "name": "ObjectivesSkill", "id": 2}, {"folder": "skill_mute", "name": "MuteSkill", "id": 1}]}, "context": null}
        2017-06-23 20:28:27,864 - ControlCenterSkill - DEBUG - rating skill_hello_world:23
        2017-06-23 20:28:27,864 - ControlCenterSkill - DEBUG - rating skill_control_center:97
        2017-06-23 20:28:27,865 - ControlCenterSkill - DEBUG - skill_control_center is the best candidate for control center
        2017-06-23 20:28:27,865 - ControlCenterSkill - DEBUG - rating skill_personal:26
        2017-06-23 20:28:27,866 - ControlCenterSkill - DEBUG - rating service_objectives:32
        2017-06-23 20:28:27,868 - ControlCenterSkill - DEBUG - rating skill_mute:32
        2017-06-23 20:28:27,869 - ControlCenterSkill - INFO - Requesting shutdown of skill_control_center with id: 4
        2017-06-23 20:28:27,869 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "Requesting shutdown of control center", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}
        2017-06-23 20:28:27,873 - Skills - DEBUG - {"type": "shutdown_skill_request", "data": {"skill_id": 4}, "context": null}
        2017-06-23 20:28:27,875 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "waiting", "skill_id": 4}, "context": null}
        2017-06-23 20:28:29,288 - Skills - DEBUG - Skill skill_control_center shutdown was requested
        2017-06-23 20:28:29,288 - Skills - DEBUG - External shutdown for skill_control_center is forbidden
        2017-06-23 20:28:29,290 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "forbidden", "skill_id": 4}, "context": null}
        2017-06-23 20:28:29,376 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "skill control center shutdown is forbidden", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}


# shutdown logs

        2017-06-23 19:11:31,891 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["shutdown personal skill"]}, "context": null}
        2017-06-23 19:11:31,901 - Skills - DEBUG - {"type": "4:SkillShutdownIntent", "data": {"confidence": 0.25, "target": "cli", "mute": false, "intent_type": "4:SkillShutdownIntent", "Skill_Shutdown": "personal", "utterance": "shutdown personal skill"}, "context": {"target": "cli"}}
        2017-06-23 19:11:31,903 - Skills - DEBUG - {"type": "loaded_skills_request", "data": {}, "context": null}
        2017-06-23 19:11:31,906 - Skills - DEBUG - {"type": "loaded_skills_response", "data": {"skills": [{"folder": "skill_hello_world", "name": "HelloWorldSkill", "id": 5}, {"folder": "skill_control_center", "name": "ControlCenterSkill", "id": 4}, {"folder": "skill_personal", "name": "PersonalSkill", "id": 3}, {"folder": "service_objectives", "name": "ObjectivesSkill", "id": 2}, {"folder": "skill_mute", "name": "MuteSkill", "id": 1}]}, "context": null}
        2017-06-23 19:11:32,003 - ControlCenterSkill - DEBUG - rating skill_hello_world:16
        2017-06-23 19:11:32,004 - ControlCenterSkill - DEBUG - rating skill_control_center:29
        2017-06-23 19:11:32,004 - ControlCenterSkill - DEBUG - rating skill_personal:73
        2017-06-23 19:11:32,005 - ControlCenterSkill - DEBUG - skill_personal is the best candidate for personal
        2017-06-23 19:11:32,005 - ControlCenterSkill - DEBUG - rating service_objectives:23
        2017-06-23 19:11:32,006 - ControlCenterSkill - DEBUG - rating skill_mute:22
        2017-06-23 19:11:32,006 - ControlCenterSkill - INFO - Requesting shutdown of 3 skill
        2017-06-23 19:11:32,007 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "Requesting shutdown of personal", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}
        2017-06-23 19:11:32,008 - Skills - DEBUG - {"type": "shutdown_skill_request", "data": {"skill_id": 3}, "context": null}
        2017-06-23 19:11:32,011 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "waiting", "skill_id": 3}, "context": null}
        2017-06-23 19:11:33,584 - Skills - DEBUG - Skill skill_personal shutdown was requested
        2017-06-23 19:11:33,588 - Skills - DEBUG - {"type": "detach_skill", "data": {"skill_id": "3:"}, "context": null}
        2017-06-23 19:11:33,590 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "shutdown", "skill_id": 3}, "context": null}


# reload logs

        2017-06-23 19:11:57,091 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["reload personal skill"]}, "context": null}
        2017-06-23 19:11:57,105 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 4, "utterances": ["reload personal skill"]}, "context": null}
        2017-06-23 19:11:57,107 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 4, "result": false}, "context": null}
        2017-06-23 19:11:57,119 - Skills - DEBUG - {"type": "4:SkillReloadIntent", "data": {"confidence": 0.25, "target": "cli", "mute": false, "intent_type": "4:SkillReloadIntent", "utterance": "reload personal skill", "Skill_Reload": "personal"}, "context": {"target": "cli"}}
        2017-06-23 19:11:57,121 - Skills - DEBUG - {"type": "loaded_skills_request", "data": {}, "context": null}
        2017-06-23 19:11:57,126 - Skills - DEBUG - {"type": "loaded_skills_response", "data": {"skills": [{"folder": "skill_hello_world", "name": "HelloWorldSkill", "id": 5}, {"folder": "skill_control_center", "name": "ControlCenterSkill", "id": 4}, {"folder": "skill_personal", "name": "unloaded", "id": 3}, {"folder": "service_objectives", "name": "ObjectivesSkill", "id": 2}, {"folder": "skill_mute", "name": "MuteSkill", "id": 1}]}, "context": null}
        2017-06-23 19:11:57,224 - ControlCenterSkill - DEBUG - rating skill_hello_world:16
        2017-06-23 19:11:57,224 - ControlCenterSkill - DEBUG - rating skill_control_center:29
        2017-06-23 19:11:57,225 - ControlCenterSkill - DEBUG - rating skill_personal:73
        2017-06-23 19:11:57,226 - ControlCenterSkill - DEBUG - skill_personal is the best candidate for personal
        2017-06-23 19:11:57,227 - ControlCenterSkill - DEBUG - rating service_objectives:23
        2017-06-23 19:11:57,226 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "Requesting reload of personal", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}
        2017-06-23 19:11:57,227 - ControlCenterSkill - DEBUG - rating skill_mute:22
        2017-06-23 19:11:57,228 - ControlCenterSkill - INFO - Requesting reload of 3 skill
        2017-06-23 19:11:57,231 - Skills - DEBUG - {"type": "reload_skill_request", "data": {"skill_id": 3}, "context": null}
        2017-06-23 19:11:57,235 - Skills - DEBUG - {"type": "reload_skill_response", "data": {"status": "waiting", "skill_id": 3}, "context": null}
        2017-06-23 19:11:57,647 - Skills - DEBUG - External reload for skill_personal requested
        2017-06-23 19:11:57,648 - Skills - DEBUG - Reloading Skill: skill_personal
        2017-06-23 19:11:57,648 - Skills - DEBUG - Shutting down Skill: skill_personal
        2017-06-23 19:11:57,648 - Skills - DEBUG - Skill skill_personal is already shutdown
        2017-06-23 19:11:57,648 - mycroft.skills.core - INFO - ATTEMPTING TO LOAD SKILL: skill_personal
        2017-06-23 19:11:57,650 - Skills - DEBUG - {"type": "reload_skill_response", "data": {"status": "reloading", "skill_id": 3}, "context": null}
        2017-06-23 19:11:57,655 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "when were you born", "end": "WhenWereYouBornKeyword"}, "context": null}
        2017-06-23 19:11:57,656 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "when were you created", "end": "WhenWereYouBornKeyword"}, "context": null}
        2017-06-23 19:11:57,662 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "where were you born", "end": "WhereWereYouBornKeyword"}, "context": null}
        2017-06-23 19:11:57,664 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "where were you created", "end": "WhereWereYouBornKeyword"}, "context": null}
        2017-06-23 19:11:57,666 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who are you", "end": "WhoAreYouKeyword"}, "context": null}
        2017-06-23 19:11:57,668 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "what are you", "end": "WhatAreYouKeyword"}, "context": null}
        2017-06-23 19:11:57,669 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who made you", "end": "WhoMadeYouKeyword"}, "context": null}
        2017-06-23 19:11:57,670 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who were you made by", "end": "WhoMadeYouKeyword"}, "context": null}
        2017-06-23 19:11:57,672 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who created you", "end": "WhoMadeYouKeyword"}, "context": null}
        2017-06-23 19:11:57,678 - mycroft.skills.core - INFO - Loaded skill_personal with ID 3
        2017-06-23 19:11:57,681 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who built you", "end": "WhoMadeYouKeyword"}, "context": null}
        2017-06-23 19:11:57,682 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhenWereYouBornKeyword", "WhenWereYouBornKeyword"]], "optional": [], "name": "3:WhenWereYouBornIntent"}, "context": null}
        2017-06-23 19:11:57,683 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhereWereYouBornKeyword", "WhereWereYouBornKeyword"]], "optional": [], "name": "3:WhereWereYouBornIntent"}, "context": null}
        2017-06-23 19:11:57,686 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhoMadeYouKeyWord", "WhoMadeYouKeyWord"]], "optional": [], "name": "3:WhoMadeYouIntent"}, "context": null}
        2017-06-23 19:11:57,718 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhoAreYouKeyword", "WhoAreYouKeyword"]], "optional": [], "name": "3:WhoAreYouIntent"}, "context": null}
        2017-06-23 19:11:57,719 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhatAreYouKeyword", "WhatAreYouKeyword"]], "optional": [], "name": "3:WhatAreYouIntent"}, "context": null}


# Change run level logs

        2017-06-23 18:33:15,536 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["go to level dev"]}, "context": null}
        2017-06-23 18:33:15,547 - Skills - DEBUG - {"type": "4:ChangeRunLevelIntent", "data": {"confidence": 0.25, "target": "cli", "Level": "dev", "intent_type": "4:ChangeRunLevelIntent", "mute": false, "utterance": "go to level dev"}, "context": {"target": "cli"}}
        2017-06-23 18:33:15,549 - Skills - DEBUG - {"type": "loaded_skills_request", "data": {}, "context": null}
        2017-06-23 18:33:15,553 - Skills - DEBUG - {"type": "loaded_skills_response", "data": {"skills": [{"folder": "skill_hello_world", "name": "HelloWorldSkill", "id": 5}, {"folder": "skill_control_center", "name": "ControlCenterSkill", "id": 4}, {"folder": "skill_personal", "name": "PersonalSkill", "id": 3}, {"folder": "service_objectives", "name": "ObjectivesSkill", "id": 2}, {"folder": "skill_mute", "name": "MuteSkill", "id": 1}]}, "context": null}
        2017-06-23 18:33:15,653 - ControlCenterSkill - DEBUG - Changing run level from full to dev
        2017-06-23 18:33:15,653 - ControlCenterSkill - DEBUG - full{u'skills': [], u'type': u'blacklist'}
        2017-06-23 18:33:15,653 - ControlCenterSkill - DEBUG - dev{u'skills': [u'skill_control_center', u'skill_joke', u'skill_facebook', u'skill_user_id', u'skill_personal'], u'type': u'whitelist'}
        2017-06-23 18:33:15,654 - ControlCenterSkill - INFO - Requesting shutdown of 5 skill
        2017-06-23 18:33:15,655 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "Changing run level to dev", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}
        2017-06-23 18:33:15,657 - Skills - DEBUG - {"type": "shutdown_skill_request", "data": {"skill_id": 5}, "context": null}
        2017-06-23 18:33:15,660 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "waiting", "skill_id": 5}, "context": null}
        2017-06-23 18:33:15,688 - Skills - DEBUG - Skill skill_hello_world shutdown was requested
        2017-06-23 18:33:15,690 - Skills - DEBUG - {"type": "detach_skill", "data": {"skill_id": "5:"}, "context": null}
        2017-06-23 18:33:15,730 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "shutdown", "skill_id": 5}, "context": null}
        2017-06-23 18:33:15,756 - ControlCenterSkill - INFO - Requesting reload of 3 skill
        2017-06-23 18:33:15,758 - Skills - DEBUG - {"type": "reload_skill_request", "data": {"skill_id": 3}, "context": null}
        2017-06-23 18:33:15,762 - Skills - DEBUG - {"type": "reload_skill_response", "data": {"status": "waiting", "skill_id": 3}, "context": null}
        2017-06-23 18:33:17,694 - Skills - DEBUG - External reload for skill_personal requested
        2017-06-23 18:33:17,694 - Skills - DEBUG - Reloading Skill: skill_personal
        2017-06-23 18:33:17,695 - Skills - DEBUG - Shutting down Skill: skill_personal
        2017-06-23 18:33:17,696 - mycroft.skills.core - INFO - ATTEMPTING TO LOAD SKILL: skill_personal
        2017-06-23 18:33:17,700 - Skills - DEBUG - {"type": "reload_skill_response", "data": {"status": "reloading", "skill_id": 3}, "context": null}
        2017-06-23 18:33:17,702 - Skills - DEBUG - {"type": "detach_skill", "data": {"skill_id": "3:"}, "context": null}
        2017-06-23 18:33:17,703 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "when were you born", "end": "WhenWereYouBornKeyword"}, "context": null}
        2017-06-23 18:33:17,708 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "when were you created", "end": "WhenWereYouBornKeyword"}, "context": null}
        2017-06-23 18:33:17,710 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "where were you born", "end": "WhereWereYouBornKeyword"}, "context": null}
        2017-06-23 18:33:17,713 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "where were you created", "end": "WhereWereYouBornKeyword"}, "context": null}
        2017-06-23 18:33:17,714 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who are you", "end": "WhoAreYouKeyword"}, "context": null}
        2017-06-23 18:33:17,716 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "what are you", "end": "WhatAreYouKeyword"}, "context": null}
        2017-06-23 18:33:17,718 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who made you", "end": "WhoMadeYouKeyword"}, "context": null}
        2017-06-23 18:33:17,723 - mycroft.skills.core - INFO - Loaded skill_personal with ID 3
        2017-06-23 18:33:17,725 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who were you made by", "end": "WhoMadeYouKeyword"}, "context": null}
        2017-06-23 18:33:17,726 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who created you", "end": "WhoMadeYouKeyword"}, "context": null}
        2017-06-23 18:33:17,761 - ControlCenterSkill - INFO - Requesting shutdown of 2 skill
        2017-06-23 18:33:17,762 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "who built you", "end": "WhoMadeYouKeyword"}, "context": null}
        2017-06-23 18:33:17,764 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhenWereYouBornKeyword", "WhenWereYouBornKeyword"]], "optional": [], "name": "3:WhenWereYouBornIntent"}, "context": null}
        2017-06-23 18:33:17,766 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhereWereYouBornKeyword", "WhereWereYouBornKeyword"]], "optional": [], "name": "3:WhereWereYouBornIntent"}, "context": null}
        2017-06-23 18:33:17,767 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhoMadeYouKeyWord", "WhoMadeYouKeyWord"]], "optional": [], "name": "3:WhoMadeYouIntent"}, "context": null}
        2017-06-23 18:33:17,769 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhoAreYouKeyword", "WhoAreYouKeyword"]], "optional": [], "name": "3:WhoAreYouIntent"}, "context": null}
        2017-06-23 18:33:17,770 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["WhatAreYouKeyword", "WhatAreYouKeyword"]], "optional": [], "name": "3:WhatAreYouIntent"}, "context": null}
        2017-06-23 18:33:17,802 - Skills - DEBUG - {"type": "shutdown_skill_request", "data": {"skill_id": 2}, "context": null}
        2017-06-23 18:33:17,804 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "waiting", "skill_id": 2}, "context": null}
        2017-06-23 18:33:19,726 - Skills - DEBUG - Skill service_objectives shutdown was requested
        2017-06-23 18:33:19,731 - Skills - DEBUG - {"type": "detach_skill", "data": {"skill_id": "2:"}, "context": null}
        2017-06-23 18:33:19,733 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "shutdown", "skill_id": 2}, "context": null}
        2017-06-23 18:33:19,765 - ControlCenterSkill - INFO - Requesting shutdown of 1 skill
        2017-06-23 18:33:19,768 - Skills - DEBUG - {"type": "shutdown_skill_request", "data": {"skill_id": 1}, "context": null}
        2017-06-23 18:33:19,771 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "waiting", "skill_id": 1}, "context": null}
        2017-06-23 18:33:21,738 - Skills - DEBUG - Skill skill_mute shutdown was requested
        2017-06-23 18:33:21,741 - Skills - DEBUG - {"type": "detach_skill", "data": {"skill_id": "1:"}, "context": null}
        2017-06-23 18:33:21,744 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "shutdown", "skill_id": 1}, "context": null}
        2017-06-23 18:33:21,770 - ControlCenterSkill - DEBUG - Run level Changed

# config file

              "skills": {
                // Directory to look for user skills
                "directory": "~/.mycroft/skills",
                 // blacklisted skills to not load
                "blacklisted_skills": ["template_skill", "service_context", "service_sound_analisys", "service_face"],
                // priority skills to be loaded first
                "priority_skills": ["skill_help", "skill_control_center", "service_objectives"],
                "default_run_level" : "full",
                "run_levels": {
                    // core skills only
                    "0":{
                        "type":"whitelist",
                        "skills": []
                    },
                    "core":{
                        "type":"whitelist",
                        "skills":["skill_alarm", "skill_configuration", "skill_date_time", "skill_desktop_launcher", "skill_hello_world",
                        "skill_joke", "skill_naptime", "skill_npr_news", "skill_pairing", "skill_personal", "skill_reminder",
                        "skill_speak", "skill_spelling", "skill_stock", "skill_stop", "skill_volume", "skill_weather", "skill_wiki",
                        "skill-ip", "skill-pairing", "skill-wolfram-alpha", "skill_control_center", "skill_help"]
                    },
                    // all skills that can run offline only
                    "offline":{
                        "type":"blacklist",
                        "skills":["objective_facebook_content", "objective_troll", "objective_wikipedia",
                                "skill_bitcoin_enhanced", "skill_articles", "skill_apod", "skill_cbc_news", "skill_daily_meditation",
                                "skill_dumpmon", "skill_earth_polychromatic_imaging_camera", "skill_proxy", "skill_quotes",
                                "skill_euromillions", "skill_facebook", "skill_facebook_posts", "skill_fox_news", "skill_metal_recomend",
                                "skill_music", "skill_near_earth_object_tracker", "skill_solar_times", "skill_sun_spots", "skill_traffic",
                                "skill_np_news", "skill_pairing", "skill_photolocation", "skill_pickup_line", "skill_picture_search",
                                "skill_ping", "skill_translate", "skill_weather", "skill_wiki",
                                "LILACS_core", "LILACS_knowledge", "LILACS_storage", "LILACS_rhymes","LILACS_teach", "LILACS_chatbot", "LILACS_curiosity"]
                    },
                    // minimal LILACS
                    "lilacs_minimal":{
                        "type":"whitelist",
                        "skills":["LILACS_core", "LILACS_knowledge", "LILACS_storage", "LILACS_teach"]
                    },
                    // offline LILACS #not available, TODO: need own spotlight server
                    //"LILACS_offline":{
                    //    "type":"whitelist",
                    //    "skills":[]
                    //},
                    // full LILACS
                    "lilacs":{
                        "type":"whitelist",
                        "skills":["LILACS_core", "LILACS_knowledge", "LILACS_storage", "LILACS_rhymes","LILACS_teach", "LILACS_chatbot", "LILACS_curiosity"]
                    },
                    // jarbas selection
                    "jarbas":{
                        "type":"blacklist",
                        "skills":["skill-ip", "skill_configuration", "skill_pairing", "skill-audio-record", "skill-wolfram-alpha" ]
                    },
                    // all skills
                    "full":{
                        "type":"blacklist",
                        "skills":[]
                    },
                    // censor some skills (facebook client, dont allow desktop launcher)
                    "restricted":{
                        "type":"blacklist",
                        "skills":["service_face", "skill_desktop_launcher", "skill_mute", "skill_dictation", "service_display", "service_audio", "service_vision", "skill_audio_record", "LILACS_teach", "skill_configuration", "skill_pairing", "skill_diagnostics","skill_deep_dream", "skill_control_center", "skill_cmd", "skill_wallpaper", "skill_reminder", "skill_alarm", "skill_playback_control", "skill_naptime"]
                    },
                    // only skills you are working on, dont load unecessary skills for what you are testing
                    "dev":{
                        "type":"whitelist",
                        "skills":["skill_control_center", "skill_joke", "skill_facebook", "skill_user_id", "skill_personal"]
                    },
                    // privacy enhanced skills selection,
                    "secure":{
                        "type":"blacklist",
                        "skills":["service_vision", "skill_desktop_launcher", "service_sound_analisys", "skill_ip", "skill_configuration", "skill-audio-record", "skill_pairing"]
                    }
                }
              },