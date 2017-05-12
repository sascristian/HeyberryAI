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


from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill

from time import time

__author__ = 'jarbas'


class ControlCenterSkill(MycroftSkill):

    def __init__(self):
        super(ControlCenterSkill, self).__init__(name="ControlCenterSkill")
        # initialize your variables
        self.reload_skill = False
        self.skill_name_to_id = {}
        self.loaded_skills = [] # [{"name":skill_name, "id":skill_id, "folder":skill_folder}]
        self.time_out = 20

    def initialize(self):
        self.emitter.on("loaded_skills_response", self.handle_receive_loaded_skills)
        # register intents
        self.build_intents()

    def build_intents(self):
        manifest_intent = IntentBuilder("SkillManifestIntent") \
            .require("ManifestKeyword").build()
        self.register_intent(manifest_intent,
                             self.handle_manifest_intent)

        reload_intent = IntentBuilder("SkillReloadIntent") \
            .require("ReloadKeyword").build()
        self.register_intent(reload_intent,
                             self.handle_reload_skill_intent)

        shutdown_intent = IntentBuilder("SkillShutdownIntent") \
            .require("ShutdownKeyword").build()
        self.register_intent(shutdown_intent,
                             self.handle_shutdown_skill_intent)

    # internal

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
        for skill in self.loaded_skills:
            self.skill_name_to_id[skill["name"]] = skill["id"]
            self.skill_name_to_id[skill["name"].lower()] = skill["id"]
            self.skill_name_to_id[skill["name"]+"skill"] = skill["id"]
            self.skill_name_to_id[skill["name"].lower()+"skill"] = skill["id"]
            self.skill_name_to_id[skill["name"] + "Skill"] = skill["id"]
            self.skill_name_to_id[skill["name"].lower() + "Skill"] = skill["id"]
        self.waiting = False

   # intents

    # intents
    def handle_skill_number_intent(self, message):
        self.get_loaded_skills()
        # speak how many skills are loaded

    def handle_reload_skill_intent(self, message):
        self.get_loaded_skills()
        # TODO regex skill name
        #skill_name = message.data["skill"]
        skill_name = "CBCNews"
        possible_names = [skill_name, skill_name.lower(), skill_name + "Skill", skill_name.lower()+"Skill", skill_name + "skill", skill_name.lower()+"skill"]
        # if skill id was provided use it
        if skill_name.isdigit():
            skill_id = skill_name
        # else get skill_id from name
        else:
            skill_id = 0
            try:
                for p in possible_names:
                    try:
                        skill_id = self.skill_name_to_id[p]
                        break
                    except:
                        pass
            except:
                self.speak("Skill " + skill_name + " isn't loaded")
                return
        self.log.info("Requesting reload of " + str(skill_id))
        # reload skill
        self.emitter.emit(Message("reload_skill_request", {"skill_id": skill_id}))

    def handle_shutdown_skill_intent(self, message):
        self.get_loaded_skills()
        # TODO regex skill name
        #skill_name = message.data["skill"]
        skill_name = "CBCNews"
        possible_names = [skill_name, skill_name.lower(), skill_name + "Skill", skill_name.lower() + "Skill",
                          skill_name + "skill", skill_name.lower() + "skill"]
        # if skill id was provided use it
        if skill_name.isdigit():
            skill_id = skill_name
        # else get skill_id from name
        else:
            skill_id = 0
            try:
                for p in possible_names:
                    try:
                        skill_id = self.skill_name_to_id[p]
                        break
                    except:
                        pass
            except:
                self.speak("Skill " + skill_name + " isn't loaded")
                return
        self.log.info("Requesting shutdown of " + str(skill_id))
        # reload skill
        self.emitter.emit(Message("shutdown_skill_request", {"skill_id": skill_id}))

    def handle_manifest_intent(self, message):
        self.get_loaded_skills()
        text = "Loaded skills manifest. "
        for skill in self.loaded_skills:
            s = skill["name"].lower().replace("skill", "")
            if s not in text and s != "blacklisted":
                text += s + ". "
        self.speak(text)

    def stop(self):
        pass

    def converse(self, transcript, lang="en-us"):
        return False


def create_skill():
    return ControlCenterSkill()