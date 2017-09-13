# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

# TODO
# - change (some) config file fields (voice)
# - msm uninstall skill
# - restart / shutdown mycroft service

from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.configuration import ConfigurationManager
from fuzzywuzzy import fuzz
from time import time, sleep

__author__ = 'jarbas'


class ControlCenterSkill(MycroftSkill):

    def __init__(self):
        super(ControlCenterSkill, self).__init__(name="ControlCenterSkill")
        # initialize your variables
        self.current_level = "full"
        self.status = "forbidden"
        self.reload_skill = False
        self.external_reload = False
        self.external_shutdown = False
        self.skill_name_to_id = {}
        self.loaded_skills = [] # [{"name":skill_name, "id":skill_id, "folder":skill_folder}] #if name = unloaded <- blacklisted or shutdown
        self.time_out = 20
        self.run_levels = self.config_core["skills"]["run_levels"]
        self.default_level = self.config_core["skills"]["default_run_level"]
        if self.default_level not in self.run_levels.keys():
            self.default_level = "full"

    def initialize(self):
        self.build_intents()
        if self.default_level != "full":
            self.emitter.emit(Message(str(self.skill_id) +
                                      ":ChangeRunLevelIntent", {"Level": self.default_level, "wait":False}))

        self.emitter.on("reload_skill_response", self.end_wait)
        self.emitter.on("shutdown_skill_response", self.end_wait)
        self.emitter.on("skill.loaded.fail", self.end_wait)
        self.emitter.on("skill.loaded", self.end_wait)
        self.emitter.on("loaded_skills_response", self.handle_receive_loaded_skills)

    def build_intents(self):
        manifest_intent = IntentBuilder("SkillManifestIntent") \
            .require("ManifestKeyword").build()
        self.register_intent(manifest_intent,
                             self.handle_manifest_intent)

        reload_intent = IntentBuilder("SkillReloadIntent") \
            .require("Skill_Reload").build()
        self.register_intent(reload_intent,
                             self.handle_reload_skill_intent)

        shutdown_intent = IntentBuilder("SkillShutdownIntent") \
            .require("Skill_Shutdown").build()
        self.register_intent(shutdown_intent,
                             self.handle_shutdown_skill_intent)

        number_intent = IntentBuilder("SkillNumberIntent") \
            .require("SkillNumberKeyword").build()
        self.register_intent(number_intent,
                             self.handle_skill_number_intent)

        unloaded_number_intent = IntentBuilder("UnloadedSkillNumberIntent") \
            .require("UnloadedSkillNumberKeyword").build()
        self.register_intent(unloaded_number_intent,
                             self.handle_unloaded_skill_number_intent)

        unloaded_intent = IntentBuilder("SkillUnloadedManifestIntent") \
            .require("UnloadManifestKeyword").build()
        self.register_intent(unloaded_intent,
                             self.handle_unloaded_skills_intent)

        level_intent = IntentBuilder("RunLevelIntent") \
            .require("RunLevelKeyword").build()
        self.register_intent(level_intent,
                             self.handle_current_run_level_intent)

        go_to_level_intent = IntentBuilder("ChangeRunLevelIntent") \
            .require("Level").build()
        self.register_intent(go_to_level_intent,
                             self.handle_go_to_run_level_intent)

    # internal

    def get_loaded_skills(self):
        # asks main for loaded skill names, ids
        self.emitter.emit(Message("loaded_skills_request", {}))
        self.wait()

    def handle_receive_loaded_skills(self, message):
        self.loaded_skills = message.data["skills"]
        self.skill_name_to_id = {}
        self.skill_id_to_name = {}
        for skill in self.loaded_skills:
            self.skill_name_to_id[skill["name"]] = skill["id"]
            self.skill_id_to_name[skill["id"]] = skill["name"]
        self.waiting = False

    def end_wait(self, message):
        status = message.data.get("status")
        if status == "forbidden" or status == "shutdown" or status == \
                "reloading" or "skill.loaded" in message.type:
            self.status = status
            self.waiting = False

    def wait(self):
        self.waiting = True
        start_time = time()
        t = 0
        while self.waiting and t < self.time_out:
            t = time() - start_time
            sleep(0.1)
        self.waiting = False

    # intents

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

    def handle_current_run_level_intent(self, message):
        self.speak_dialog("current_run_level", {"level": self.current_level})
        for level in self.run_levels.keys():
            print "level: " + level
            print str(self.run_levels[level]["type"]) + "ed skills: " + str(self.run_levels[level]["skills"])

    def handle_go_to_run_level_intent(self, message):
        self.get_loaded_skills()
        level = message.data["Level"]
        wait = message.data.get("wait", True)
        if level not in self.run_levels.keys():
            self.speak_dialog("invalid_level")
            return

        self.speak_dialog("changing_run_level", {"level": level})
        self.log.debug("Changing run level from " + self.current_level + " to " + level)
        self.log.debug(self.current_level + str(self.run_levels[self.current_level]))
        self.log.debug(level + str(self.run_levels[level]))
        for s in self.loaded_skills:
            skill_id = s["id"]
            skill = s["folder"]
            if self.run_levels[level]["type"] == "whitelist" and skill_id != self.skill_id:
                if skill not in self.run_levels[level]["skills"]:
                    # shutdown
                    self.log.info("Requesting shutdown of " + str(skill_id) + " skill")
                    self.emitter.emit(Message("shutdown_skill_request", {"skill_id": skill_id}))
                    if wait:
                        self.wait()
                else:
                    # reload
                    self.log.info("Requesting reload of " + str(skill_id) + " skill")
                    self.emitter.emit(Message("reload_skill_request", {"skill_id": skill_id}))
                    if wait:
                        self.wait()
            elif skill_id != self.skill_id:#blacklist
                if skill in self.run_levels[level]["skills"]:
                    # shutdown
                    self.log.info("Requesting shutdown of " + str(skill_id) + " skill")
                    self.emitter.emit(Message("shutdown_skill_request", {"skill_id": skill_id}))
                    if wait:
                        self.wait()
                else:
                    # reload
                    self.log.info("Requesting reload of " + str(skill_id) + " skill")
                    self.emitter.emit(Message("reload_skill_request", {"skill_id": skill_id}))
                    if wait:
                        self.wait()
        self.current_level = level
        self.log.debug("Run level Changed")
        self.speak("Run level changed")

    def handle_reload_skill_intent(self, message):
        self.get_loaded_skills()
        skill_name = str(message.data["Skill_Reload"])
        self.speak("Requesting reload of " + skill_name)
        # if skill id was provided use it
        if skill_name.isdigit():
            skill_id = skill_name
            skill_folder = self.skill_id_to_name[int(skill_id)]
        # else get skill_id from name
        else:
            skill_id = 0
            skill_folder = ""
            best = 0
            for skill in self.loaded_skills:
                rating = fuzz.ratio(skill["folder"].lower().replace("skill", "").replace("service", "").replace("_"," "), skill_name.lower())
                self.log.debug("rating " + skill["folder"] + ":" + str(rating))
                if rating > best and rating > 40:
                    best = rating
                    skill_id = skill["id"]
                    skill_folder = skill["folder"]
                    self.log.debug(skill["folder"] + " is the best candidate for " + skill_name)
        if skill_id == 0:
            self.log.error("I dont know that skill")
            self.speak("I dont know that skill")
            return
        self.log.info("Requesting reload of " + skill_folder + " with id: " + str(skill_id))
        # reload skill
        self.emitter.emit(Message("reload_skill_request", {"skill_id": skill_id}))
        self.wait()
        if self.status == "forbidden":
            self.speak("skill " + skill_name + " reload is forbidden")
        else:
            self.speak("skill " + skill_name + " successfully reloaded")

    def handle_shutdown_skill_intent(self, message):
        self.get_loaded_skills()
        skill_name = str(message.data["Skill_Shutdown"])
        self.speak("Requesting shutdown of " + skill_name)
        # if skill id was provided use it
        if skill_name.isdigit():
            skill_id = skill_name
            skill_folder = self.skill_id_to_name[int(skill_id)]
        # else get skill_id from name
        else:
            skill_id = 0
            skill_folder = ""
            best = 0
            for skill in self.loaded_skills:
                rating = fuzz.ratio(skill["folder"].lower().replace("skill", "").replace("_", " ").replace("service", ""), skill_name.lower())
                self.log.debug("rating " + skill["folder"] + ":" + str(rating))
                if rating > best and rating > 40:
                    best = rating
                    skill_id = skill["id"]
                    skill_folder = skill["folder"]
                    self.log.debug(skill["folder"] + " is the best candidate for " + skill_name)

        if skill_id == 0:
            self.log.error("I dont know that skill")
            self.speak("I dont know that skill")
            return
        self.log.info("Requesting shutdown of " + skill_folder + " with id: " + str(skill_id))
        # reload skill
        self.emitter.emit(Message("shutdown_skill_request", {"skill_id": skill_id}))
        self.wait()
        if self.status == "forbidden":
            self.speak("skill " + skill_name + " shutdown is forbidden")
        else:
            self.speak("skill " + skill_name + " successfully shutdown")

    def handle_manifest_intent(self, message):
        self.get_loaded_skills()
        text = "Loaded skills manifest. "
        for skill in self.loaded_skills:
            if skill["name"] != "unloaded":
                text += skill["folder"].replace("_"," ").replace("-"," ") + ", "
        self.speak(text[:-2])

    def handle_unloaded_skills_intent(self, message):
        self.get_loaded_skills()
        text = "Unloaded skills manifest. "
        for skill in self.loaded_skills:
            if skill["name"] == "unloaded":
                text += skill["folder"].replace("_"," ").replace("-"," ") + ", "
        self.speak(text[:-2])

    def stop(self):
        pass

    def converse(self, utterances, lang="en-us"):
        return False


def create_skill():
    return ControlCenterSkill()