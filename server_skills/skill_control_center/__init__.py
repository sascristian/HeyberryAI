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

from time import time

from adapt.intent import IntentBuilder

from mycroft.configuration import ConfigurationManager
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill

__author__ = 'jarbas'


class ControlCenterSkill(MycroftSkill):
    def __init__(self):
        super(ControlCenterSkill, self).__init__(name="ControlCenterSkill")
        # initialize your variables
        self.current_level = "full"
        self.reload_skill = False
        self.external_reload = False
        self.external_shutdown = False
        self.skill_name_to_id = {}
        self.loaded_skills = []  # [{"name":skill_name, "id":skill_id, "folder":skill_folder}] #if name = unloaded <- blacklisted or shutdown
        self.time_out = 20
        self.run_levels = self.config_core["skills"]["run_levels"]
        self.default_level = self.config_core["skills"]["default_run_level"]
        if self.default_level not in self.run_levels.keys():
            self.default_level = "core"
        # TODO get from subprocess mimic -lv
        self.mimic_voices = ["ap", "slt", "kal", "awb", "kal16", "rms", "awb_time"]
        self.espeak_langs = ["en", "en-us", "en-sc", "en-n", "en-rp", "en-wm"]
        self.espeak_voices = ["m1", "m2", "m3", "m4", "m5", "m6", "croak", "whisper", "f1", "f2", "f3", "f4", "f5"]

    def initialize(self):
        self.build_intents()
        if self.default_level != "full":
            self.emitter.emit(Message(str(self.skill_id) + ":ChangeRunLevelIntent", {"Level": self.default_level}))
        self.emitter.on("loaded_skills_response", self.handle_receive_loaded_skills)
        self.manager = ConfigurationManager()
        self.manager.init(self.emitter)
        self.reset_config()
        self.change_voice()

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

        unloaded_intent = IntentBuilder("SkillUnloadedManifestIntent") \
            .require("UnloadManifestKeyword").build()
        self.register_intent(unloaded_intent,
                             self.handle_unloaded_skills_intent)

        level_intent = IntentBuilder("RunLevelIntent") \
            .require("RunLevelKeyword").build()
        self.register_intent(level_intent,
                             self.handle_current_run_level_intent)

        voice_intent = IntentBuilder("VoiceIntent") \
            .require("CurrentvoiceKeyword").build()
        self.register_intent(voice_intent,
                             self.handle_current_voice_intent)

        go_to_level_intent = IntentBuilder("ChangeRunLevelIntent") \
            .require("Level").build()
        self.register_intent(go_to_level_intent,
                             self.handle_go_to_run_level_intent)

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
        self.skill_name_to_id = {}
        for skill in self.loaded_skills:
            self.skill_name_to_id[skill["name"].lower().replace("_", " ").replace(" skill", "").replace("skill", "")] = \
                skill["id"]
        self.waiting = False

    def update_config_field(self, key, data):
        self.runtime_config[key] = data
        self.emitter.emit(Message("configuration.updated", self.runtime_config))

    def reset_config(self):
        self.manager.load_defaults()
        self.runtime_config = self.manager.get()
        self.emitter.emit(Message("configuration.updated", self.runtime_config))

    def change_voice(self, module="espeak", voice="m1"):
        tts = self.runtime_config["tts"]
        current_module = tts["module"]
        current_voice = tts[current_module]["voice"]
        tts["module"] = module
        tts[module]["voice"] = voice
        self.runtime_config["tts"] = tts
        self.emitter.emit(Message("configuration.updated", self.runtime_config))

    # intents
    def handle_current_voice_intent(self, message):
        self.runtime_config = self.manager.get()
        tts = self.runtime_config["tts"]
        current_module = tts["module"]
        current_voice = tts[current_module]["voice"]
        voice = current_module + " " + current_voice
        self.speak_dialog("current.voice", {"voice": voice})

    def handle_skill_number_intent(self, message):
        self.get_loaded_skills()
        self.speak("Number of loaded skills: " + str(len(self.skill_name_to_id) - 1))

    def handle_current_run_level_intent(self, message):
        self.speak_dialog("current_run_level", {"level": self.current_level})
        for level in self.run_levels.keys():
            print "level: " + level
            print str(self.run_levels[level]["type"]) + "ed skills: " + str(self.run_levels[level]["skills"])

    def handle_go_to_run_level_intent(self, message):
        self.get_loaded_skills()
        level = message.data["Level"]
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
                    # self.log.info("Requesting shutdown of " + str(skill_id) + " skill")
                    self.emitter.emit(Message("shutdown_skill_request", {"skill_id": skill_id}))
                else:
                    # reload
                    # self.log.info("Requesting reload of " + str(skill_id) + " skill")
                    self.emitter.emit(Message("reload_skill_request", {"skill_id": skill_id}))
            elif skill_id != self.skill_id:  # blacklist
                if skill in self.run_levels[level]["skills"]:
                    # shutdown
                    # self.log.info("Requesting shutdown of " + str(skill_id) + " skill")
                    self.emitter.emit(Message("shutdown_skill_request", {"skill_id": skill_id}))
                else:
                    # reload
                    # self.log.info("Requesting reload of " + str(skill_id) + " skill")
                    self.emitter.emit(Message("reload_skill_request", {"skill_id": skill_id}))
        self.current_level = level
        self.log.debug("Run level Changed")
        # self.speak("Run level change request finished")

    def handle_reload_skill_intent(self, message):
        self.get_loaded_skills()
        skill_name = str(message.data["Skill_Reload"]).lower().replace(" skill", "").replace("skill", "").replace("_",
                                                                                                                  " ")
        possible_names = [skill_name, skill_name.lower() + " "]
        self.speak("Requesting reload of " + skill_name)
        # if skill id was provided use it
        if skill_name.isdigit():
            skill_id = skill_name
        # else get skill_id from name
        else:
            flag = False
            skill_id = 0
            for p in possible_names:
                try:
                    skill_id = self.skill_name_to_id[p]
                    flag = True
                    break
                except:
                    pass
            if not flag:
                self.speak("Skill " + skill_name + " isn't loaded")
                return
        self.log.info("Requesting reload of " + str(skill_id) + " skill")
        # reload skill
        self.emitter.emit(Message("reload_skill_request", {"skill_id": skill_id}))

    def handle_shutdown_skill_intent(self, message):
        self.get_loaded_skills()
        skill_name = str(message.data["Skill_Shutdown"]).lower().replace(" skill", "").replace("skill", "").replace("_",
                                                                                                                    " ")
        possible_names = [skill_name, skill_name.lower() + " "]
        self.speak("Requesting shutdown of " + skill_name)
        # if skill id was provided use it
        if skill_name.isdigit():
            skill_id = skill_name
        # else get skill_id from name
        else:
            flag = False
            skill_id = 0
            for p in possible_names:
                try:
                    skill_id = self.skill_name_to_id[p]
                    flag = True
                    break
                except:
                    pass
            if not flag:
                self.speak("Skill " + skill_name + " isn't loaded")
                return
        self.log.info("Requesting shutdown of " + str(skill_id) + " skill")
        # reload skill
        self.emitter.emit(Message("shutdown_skill_request", {"skill_id": skill_id}))

    def handle_manifest_intent(self, message):
        self.get_loaded_skills()
        text = "Loaded skills manifest.\n"
        for skill in self.skill_name_to_id.keys():
            if skill not in text and skill != "unloaded":
                text += skill + ".\n"
        self.speak(text)

    def handle_unloaded_skills_intent(self, message):
        self.get_loaded_skills()
        text = "Unloaded skills manifest.\n"
        for skill in self.loaded_skills:
            if skill["name"] == "unloaded":
                text += skill["folder"] + ".\n"
        self.speak(text)

    def stop(self):
        pass

    def converse(self, transcript, lang="en-us"):
        return False


def create_skill():
    return ControlCenterSkill()
