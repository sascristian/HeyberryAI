external shutdown and skill reload allow for run levels

skills have a self.external_reload and self.external_shutdown that can be set to false to not allow this behaviour


# shutdown logs

        2017-06-23 18:09:51,037 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["shutdown mute skill"]}, "context": null}
        2017-06-23 18:09:51,048 - Skills - DEBUG - {"type": "4:SkillShutdownIntent", "data": {"confidence": 0.25, "target": "cli", "mute": false, "intent_type": "4:SkillShutdownIntent", "Skill_Shutdown": "mute", "utterance": "shutdown mute skill"}, "context": {"target": "cli"}}
        2017-06-23 18:09:51,060 - Skills - DEBUG - {"type": "loaded_skills_request", "data": {}, "context": null}
        2017-06-23 18:09:51,066 - Skills - DEBUG - {"type": "loaded_skills_response", "data": {"skills": [{"folder": "skill_hello_world", "name": "HelloWorldSkill", "id": 5}, {"folder": "skill_control_center", "name": "ControlCenterSkill", "id": 4}, {"folder": "skill_personal", "name": "PersonalSkill", "id": 3}, {"folder": "service_objectives", "name": "ObjectivesSkill", "id": 2}, {"folder": "skill_mute", "name": "MuteSkill", "id": 1}]}, "context": null}
        2017-06-23 18:09:51,068 - ControlCenterSkill - INFO - Requesting shutdown of 1 skill
        2017-06-23 18:09:51,073 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "Requesting shutdown of mute", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}
        2017-06-23 18:09:51,111 - Skills - DEBUG - {"type": "shutdown_skill_request", "data": {"skill_id": 1}, "context": null}
        2017-06-23 18:09:51,115 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "waiting", "skill_id": 1}, "context": null}
        2017-06-23 18:09:52,709 - Skills - DEBUG - Skill skill_mute shutdown was requested
        2017-06-23 18:09:52,713 - Skills - DEBUG - {"type": "detach_skill", "data": {"skill_id": "1:"}, "context": null}
        2017-06-23 18:09:52,715 - Skills - DEBUG - {"type": "shutdown_skill_response", "data": {"status": "shutdown", "skill_id": 1}, "context": null}


# reload logs


        2017-06-23 18:13:22,970 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["reload mute skill"]}, "context": null}
        2017-06-23 18:13:22,980 - Skills - DEBUG - {"type": "4:SkillReloadIntent", "data": {"confidence": 0.25, "target": "cli", "mute": false, "intent_type": "4:SkillReloadIntent", "utterance": "reload mute skill", "Skill_Reload": "mute"}, "context": {"target": "cli"}}
        2017-06-23 18:13:22,986 - Skills - DEBUG - {"type": "loaded_skills_request", "data": {}, "context": null}
        2017-06-23 18:13:22,991 - Skills - DEBUG - {"type": "loaded_skills_response", "data": {"skills": [{"folder": "skill_hello_world", "name": "HelloWorldSkill", "id": 5}, {"folder": "skill_control_center", "name": "ControlCenterSkill", "id": 4}, {"folder": "skill_personal", "name": "PersonalSkill", "id": 3}, {"folder": "service_objectives", "name": "ObjectivesSkill", "id": 2}, {"folder": "skill_mute", "name": "MuteSkill", "id": 1}]}, "context": null}
        2017-06-23 18:13:22,992 - ControlCenterSkill - INFO - Requesting reload of 1 skill
        2017-06-23 18:13:23,000 - Skills - DEBUG - {"type": "speak", "data": {"target": "cli", "mute": false, "expect_response": false, "more": false, "utterance": "Requesting reload of mute", "metadata": {"source_skill": "ControlCenterSkill"}}, "context": null}
        2017-06-23 18:13:23,040 - Skills - DEBUG - {"type": "reload_skill_request", "data": {"skill_id": 1}, "context": null}
        2017-06-23 18:13:23,043 - Skills - DEBUG - {"type": "reload_skill_response", "data": {"status": "waiting", "skill_id": 1}, "context": null}
        2017-06-23 18:13:24,920 - Skills - DEBUG - External reload for skill_mute requested
        2017-06-23 18:13:24,921 - Skills - DEBUG - Reloading Skill: skill_mute
        2017-06-23 18:13:24,921 - Skills - DEBUG - Shutting down Skill: skill_mute
        2017-06-23 18:13:24,923 - mycroft.skills.core - INFO - ATTEMPTING TO LOAD SKILL: skill_mute
        2017-06-23 18:13:24,926 - Skills - DEBUG - {"type": "reload_skill_response", "data": {"status": "reloading", "skill_id": 1}, "context": null}
        2017-06-23 18:13:24,927 - Skills - DEBUG - {"type": "detach_skill", "data": {"skill_id": "1:"}, "context": null}
        2017-06-23 18:13:24,931 - mycroft.skills.core - INFO - Loaded skill_mute with ID 1
        2017-06-23 18:13:24,933 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "speak enable", "end": "SpeakEnableKeyword"}, "context": null}
        2017-06-23 18:13:24,971 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "enable speak", "end": "SpeakEnableKeyword"}, "context": null}
        2017-06-23 18:13:24,972 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "speak disable", "end": "SpeakDisableKeyword"}, "context": null}
        2017-06-23 18:13:24,974 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "disable speak", "end": "SpeakDisableKeyword"}, "context": null}
        2017-06-23 18:13:24,978 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["SpeakEnableKeyword", "SpeakEnableKeyword"]], "optional": [], "name": "1:SpeakEnableIntent"}, "context": null}
        2017-06-23 18:13:24,979 - Skills - DEBUG - {"type": "register_intent", "data": {"at_least_one": [], "requires": [["SpeakDisableKeyword", "SpeakDisableKeyword"]], "optional": [], "name": "1:SpeakDisableIntent"}, "context": null}


# getting skills manifest

        def get_loaded_skills(self):
            # asks main for loaded skill names, ids
            self.emitter.emit(Message("loaded_skills_request", {}))
            self.waiting = True
            start_time = time()
            t = 0
            while self.waiting and t < self.time_out:
                t = time() - start_time
                sleep(0.1)
            self.waiting = False

        def handle_receive_loaded_skills(self, message):
            self.loaded_skills = message.data["skills"]
            self.skill_name_to_id = {}
            self.skill_id_to_name = {}
            for skill in self.loaded_skills:
                self.skill_name_to_id[skill["name"]] = skill["id"]
                self.skill_id_to_name[skill["id"]] = skill["name"]
            self.waiting = False

        def handle_manifest_intent(self, message):
            self.get_loaded_skills()
            text = "Loaded skills manifest. "
            for skill in self.loaded_skills:
                if skill["name"] != "unloaded":
                    text += skill["folder"] + ", "
            self.speak(text[:-2])

        def handle_unloaded_skills_intent(self, message):
            self.get_loaded_skills()
            text = "Unloaded skills manifest. "
            for skill in self.loaded_skills:
                if skill["name"] == "unloaded":
                    text += skill["folder"] + ", "
            self.speak(text[:-2])

# number of loaded skills

        def handle_skill_number_intent(self, message):
            self.get_loaded_skills()
            i = 0
            for skill in self.loaded_skills:
                if skill["name"] != "unloaded":
                    i += 1
            self.speak("Number of loaded skills: " + str(i))

        def handle_unloaded_skill_number_intent(self, message):
            self.get_loaded_skills()
            i = 0
            for skill in self.loaded_skills:
                if skill["name"] == "unloaded":
                    i += 1
            self.speak("Number of unloaded skills: " + str(i))


# shutdown a skill

        def handle_shutdown_skill_intent(self, message):
            self.get_loaded_skills()
            skill_name = message.data.get("Skill_Shutdown")
            self.speak("Requesting shutdown of " + skill_name)
            # if skill id was provided use it
            if skill_name.isdigit():
                skill_id = skill_name
            # else get skill_id from name
            else:
                skill_id = self.skill_name_to_id[skill_name]
            self.log.info("Requesting shutdown of " + str(skill_id) + " skill")
            # shutdown skill
            self.emitter.emit(Message("shutdown_skill_request", {"skill_id": skill_id}))


# reload a skill

        def handle_reload_skill_intent(self, message):
            self.get_loaded_skills()
            skill_name = message.data.get("Skill_Reload")
            self.speak("Requesting reload of " + skill_name)
            # if skill id was provided use it
            if skill_name.isdigit():
                skill_id = skill_name
            # else get skill_id from name
            else:
                skill_id = self.skill_name_to_id[skill_name]
            self.log.info("Requesting reload of " + str(skill_id) + " skill")
            # reload skill
            self.emitter.emit(Message("reload_skill_request", {"skill_id": skill_id}))