# random wikipedia objective

this is a simple skill to show how to use objectives skills

searches wikipedia for stuff from the wordbank

# usage

        random wiki
        >> Okay, I am looking for Chrysosplenium
        >> Chrysosplenium  is a genus of 57 species of flowering plants in the family Saxifragaceae. Species can be found throughout the arctic and northern temperate parts of the Northern Hemisphere, with the highest species diversity in eastern Asia; two species are found disjunctly in South America.

        random wiki
        >> Okay, I am searching for Marvin_Neil_Simon
        >> Marvin Neil Simon  is an American playwright, screenwriter and author. He has written more than thirty plays and nearly the same number of movie screenplays, mostly adaptations of his plays.

# logs

        2017-06-23 20:57:33,758 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["random wiki"]}, "context": null}
        2017-06-23 20:57:33,767 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 2, "utterances": ["random wiki"]}, "context": null}
        2017-06-23 20:57:33,807 - Skills - DEBUG - {"type": "intent_request", "data": {"lang": "en-us", "utterance": "random wiki"}, "context": null}
        2017-06-23 20:57:33,882 - Skills - DEBUG - {"type": "intent_response", "data": {"lang": "en-us", "skill_id": 6, "intent_name": "wikiObjectiveIntent", "utterance": "random wiki"}, "context": null}
        2017-06-23 20:57:33,981 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 2, "result": false}, "context": null}
        2017-06-23 20:57:34,076 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 6, "utterances": ["random wiki"]}, "context": null}
        2017-06-23 20:57:34,110 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 6, "result": false}, "context": null}
        2017-06-23 20:57:34,132 - Skills - DEBUG - {"type": "6:wikiObjectiveIntent", "data": {"confidence": 1.0, "target": "cli", "mute": false, "intent_type": "6:wikiObjectiveIntent", "WikiObjectiveKeyword": "random wiki", "utterance": "random wiki"}, "context": {"target": "cli"}}
        2017-06-23 20:57:34,134 - Skills - DEBUG - {"type": "execute_objective", "data": {"Objective": "wiki"}, "context": null}
        2017-06-23 20:57:34,139 - service_objectives - INFO - objective: wiki
        2017-06-23 20:57:34,140 - service_objectives - INFO - goal: Search_Wikipedia
        2017-06-23 20:57:34,140 - service_objectives - INFO - way: WikipediaIntent
        2017-06-23 20:57:34,140 - service_objectives - INFO - way data :{u'ArticleTitle': u'Marvin_Neil_Simon'}
        2017-06-23 20:57:34,140 - service_objectives - INFO - goal weight: 45
        2017-06-23 20:57:34,140 - service_objectives - INFO - way weight: 45
        2017-06-23 20:57:34,226 - Skills - DEBUG - {"type": "intent_to_skill_request", "data": {"intent_name": "WikipediaIntent"}, "context": null}
        2017-06-23 20:57:34,248 - Skills - DEBUG - {"type": "intent_to_skill_response", "data": {"skill_id": 7, "intent_name": "WikipediaIntent"}, "context": null}
        2017-06-23 20:57:34,254 - Skills - DEBUG - {"type": "7:WikipediaIntent", "data": {"ArticleTitle": "Marvin_Neil_Simon"}, "context": null}
        2017-06-23 20:57:34,264 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "objectives_skill", "utterances": ["bump objectives to active skill list"]}, "context": null}
        2017-06-23 20:57:34,377 - Skills - DEBUG - {"type": "speak", "data": {"target": "all", "mute": false, "expect_response": false, "more": true, "utterance": "Okay, I am searching for Marvin_Neil_Simon", "metadata": {"source_skill": "WikipediaSkill"}}, "context": null}
        2017-06-23 20:57:34,420 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 6, "utterances": ["bump objectives to active skill list"]}, "context": null}
        2017-06-23 20:57:34,427 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 6, "result": false}, "context": null}
        2017-06-23 20:57:34,437 - Skills - DEBUG - {"type": "converse_status_request", "data": {"lang": "en-us", "skill_id": 2, "utterances": ["bump objectives to active skill list"]}, "context": null}
        2017-06-23 20:57:34,462 - Skills - DEBUG - {"type": "intent_request", "data": {"lang": "en-us", "utterance": "bump objectives to active skill list"}, "context": null}
        2017-06-23 20:57:34,471 - Skills - DEBUG - {"type": "intent_response", "data": {"lang": "en-us", "skill_id": 2, "intent_name": "ActiveSkillIntent", "utterance": "bump objectives to active skill list"}, "context": null}
        2017-06-23 20:57:34,576 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 2, "result": false}, "context": null}
        2017-06-23 20:57:34,592 - Skills - DEBUG - {"type": "2:ActiveSkillIntent", "data": {"confidence": 1.0, "target": "objectives_skill", "mute": false, "intent_type": "2:ActiveSkillIntent", "ActivateKeyword": "bump objectives to active skill list", "utterance": "bump objectives to active skill list"}, "context": {"target": "objectives_skill"}}
        2017-06-23 20:57:43,903 - Skills - DEBUG - {"type": "speak", "data": {"target": "all", "mute": false, "expect_response": false, "more": false, "utterance": "Marvin Neil Simon  is an American playwright, screenwriter and author. He has written more than thirty plays and nearly the same number of movie screenplays, mostly adaptations of his plays.", "metadata": {"source_skill": "WikipediaSkill"}}, "context": null}
