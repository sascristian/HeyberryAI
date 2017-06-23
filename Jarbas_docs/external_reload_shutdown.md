external shutdown and skill reload allow for run levels


# getting skills manifest


        def get_loaded_skills(self):
            # asks main for loaded skill names, ids
            self.emitter.emit(Message("loaded_skills_request", {}))
            self.waiting = True
            start_time = time()
            t = 0
            while self.waiting and t < self.time_out:
                t = time() - start_time
            self.waiting = False

        def handle_receive_loaded_skills(self, message):
            self.loaded_skills = message.data["skills"]
            self.skill_name_to_id = {}
            for skill in self.loaded_skills:
                self.skill_name_to_id[skill["name"]] = skill["id"]
            self.waiting = False

# number of loaded skills

        def handle_skill_number_intent(self, message):
            self.get_loaded_skills()
            self.speak("Number of loaded skills: " + str(len(self.skill_name_to_id)-1))

# number of skills NOT loaded

        def handle_unloaded_skills_intent(self, message):
            self.get_loaded_skills()
            text = "Unloaded skills manifest.\n"
            for skill in self.loaded_skills:
                if skill["name"] == "unloaded":
                    text += skill["folder"] + ".\n"
            self.speak(text)

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