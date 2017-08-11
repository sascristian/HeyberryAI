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
from time import sleep
import time

__author__ = 'jarbas'


class TTSSkill(MycroftSkill):
    def __init__(self):
        super(TTSSkill, self).__init__()
        self.reload_skill = False
        self.current_module = None
        self.current_module_settings = {}
        self.mimic = {}
        self.espeak = {}
        self.morse = {}
        self.google = {}
        self.fatts = {}
        self.marytts = {}
        self.spdsay = {}
        self.available_modules = []

    def initialize(self):
        # get current settings
        self.get_current_tts()
        # build dicts
        self.build_mimic_dict()
        self.build_espeak_dict()
        self.build_fatts_dict()
        self.build_google_dict()
        self.build_marytts_dict()
        self.build_morse_dict()
        self.build_spdsay_dict()
        # get configured modules
        self.available_modules = self.get_available_modules()
        # build intents
        self.build_intents()
        self.emitter.on("recognizer_loop:audio_output_end", self.end_wait)

    def end_wait(self):
        self.waiting = False

    def wait(self):
        self.waiting = True
        start = time.time()
        timeout = 10
        elapsed = 0
        while self.waiting and elapsed < timeout:
            sleep(0.1)
            elapsed = time.time() - start

    def build_intents(self):
        intent = IntentBuilder("CurrentTTSIntent") \
               .require("CurrentKeyword").require("TTSKeyword") \
               .build()
        self.register_intent(intent, self.handle_current_module_intent)

        intent = IntentBuilder("AvailableVoicesIntent") \
            .require("AvailableKeyword").require("VoiceKeyword") \
            .optionally("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_available_voices_intent)

        intent = IntentBuilder("AvailableTTSIntent") \
            .require("AvailableKeyword").require("TTSKeyword") \
            .build()
        self.register_intent(intent, self.handle_available_modules_intent)

        intent = IntentBuilder("AvailableTTSLangsIntent") \
            .require("AvailableKeyword").require("LangKeyword") \
            .optionally("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_available_langs_intent)

        intent = IntentBuilder("ChangeTTSIntent") \
            .require("ChangeKeyword")\
            .require("TTSKeyword") \
            .optionally("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_change_module_intent)

        intent = IntentBuilder("ChangeVoiceIntent") \
            .require("ChangeKeyword") \
            .require("VoiceKeyword") \
            .optionally("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_change_voice_intent)

        intent = IntentBuilder("ChangeLangIntent") \
            .require("ChangeKeyword") \
            .require("LangKeyword") \
            .optionally("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_change_lang_intent)

        intent = IntentBuilder("DemoTTSIntent") \
            .require("DemoKeyword").require("TTSKeyword") \
            .build()
        self.register_intent(intent, self.handle_demo_tts_intent)

        intent = IntentBuilder("PermanentTTSIntent") \
            .require("PermanentKeyword").require("TTSKeyword") \
            .build()
        self.register_intent(intent, self.handle_permanent_tts_intent)

    # intents
    def handle_permanent_tts_intent(self, message):
        self.speak("Making cached configuration permanent")
        self.config_update(save=True)

    def handle_current_module_intent(self, message):
        if self.current_module:
            self.speak("Current voice module is " + self.current_module)
        else:
            self.get_current_tts()
            if self.current_module:
                self.speak("Current voice module is " + self.current_module)
            else:
                self.speak("I could not get current voice module from "
                       "configuration file")

    def handle_available_modules_intent(self, message):
        modules = self.available_modules
        self.speak("Available voice modules are ")
        for module in modules:
            self.speak(module)

    def handle_available_voices_intent(self, message):
        module = message.data.get("TargetKeyword", self.current_module)
        if module == "mimic":
            voices = self.mimic["voices"]
        elif module == "espeak":
            voices = self.espeak["voices"]
        elif module == "morse":
            voices = self.morse["voices"]
        else:
            self.speak(module + " doesn't have any voices")
            return
        self.speak("Available voices for " + module + " are")
        for voice in voices:
            self.speak(voice)

    def handle_available_langs_intent(self, message):
        module = message.data.get("TargetKeyword", self.current_module)
        if module == "espeak":
            langs = self.espeak["langs"]
        else:
            self.speak(module + " doesn't have any languages")
            return
        self.speak("Available languages for " + module + " are")
        for lang in langs:
            self.speak(lang)
        if module == "espeak":
            self.speak("Espeak can also be configured for non english languages "
                       "but those were not listed")

    def handle_change_module_intent(self, message):
        module = message.data.get("TargetKeyword")
        if not module:
            self.speak("Change to what module?")
            return
        if module not in self.available_modules:
            self.speak(module + " was not configured to be changed at runtime")
            return
        tts = self.get_current_tts()
        tts["module"] = module
        tts[module] = self.get_module_settings(module)
        config = {"tts": tts}
        self.update_configs(config)
        sleep(2)
        self.speak("Module changed to " + module)

    def handle_change_voice_intent(self, message):
        voice = message.data.get("TargetKeyword")
        if not voice:
            self.speak("Change to what voice?")
            return
        if self.current_module == "mimic":
            voices = self.mimic["voices"]
        elif self.current_module == "espeak":
            voices = self.espeak["voices"]
        elif self.current_module == "morse":
            voices = self.morse["voices"]
        else:
            self.speak(self.current_module + " does not support voice change "
                                             "at runtime")
            return
        if voice not in voices:
            # TODO fuzzymatch and nicknames
            self.speak(voice + " is not available")
        else:
            module_dict = self.get_module_settings(self.current_module)
            module_dict["voice"] = voice
            tts = self.get_current_tts()
            tts[self.current_module] = module_dict
            config = {"tts": tts}
            self.update_configs(config)
        self.speak("voice changed to " + voice)

    def handle_change_lang_intent(self, message):
        lang = message.data.get("TargetKeyword")
        if not lang:
            self.speak("Change to what language?")
            return
        if self.current_module == "espeak":
            langs = self.espeak["langs"]
        else:
            self.speak(self.current_module + " does not support language "
                                             "change "
                                             "at runtime")
            return
        if lang not in langs:
            # TODO fuzzymatch and nicknames
            self.speak(lang + " is not available")
        else:
            module_dict = self.get_module_settings(self.current_module)
            module_dict["lang"] = lang
            tts = self.get_current_tts()
            tts[self.current_module] = module_dict
            config = {"tts": tts}
            self.update_configs(config)
            self.speak("language changed to " + lang)


    def handle_demo_tts_intent(self, message):
        if self.current_module == "mimic":
            voices = self.mimic["voices"]
            langs = []
        elif self.current_module == "morse":
            voices = self.morse["voices"]
            langs = []
        elif self.current_module == "espeak":
            voices = self.espeak["voices"]
            langs = self.espeak["langs"]
        else:
            self.speak(self.current_module + " has no pre - configured voices")
            return

        original_dict = self.get_module_settings(self.current_module)
        for voice in voices:
            self.log.info("Changing voice to " + voice)
            module_dict = self.get_module_settings(self.current_module)
            module_dict["voice"] = voice
            tts = self.get_current_tts()
            tts[self.current_module] = module_dict
            config = {"tts": tts}
            self.update_configs(config)
            sleep(1)
            self.speak("This is voice " + voice)
            self.wait()
            for lang in langs:
                self.log.info("Changing lang to " + lang)
                module_dict["lang"] = lang
                tts = self.get_current_tts()
                tts[self.current_module] = module_dict
                config = {"tts": tts}
                self.update_configs(config)
                sleep(1)
                self.speak("Using language " + lang)
                self.wait()
        self.log.info("Reverting to original tts module")
        tts = self.get_current_tts()
        tts[self.current_module] = original_dict
        config = {"tts": tts}
        self.update_configs(config)


    # dicts with possible choices for each stt engine
    def build_mimic_dict(self):
        self.mimic["name"] = "mimic"
        self.mimic["voices"] = ["ap", "slt", "kal", "awb", "kal16", "rms",
                             "awb_time"]

    def build_espeak_dict(self):
        self.espeak["name"] = "espeak"
        self.espeak["voices"] = ["m1", "m2", "m3", "m4", "m5", "m6", "croak",
                              "whisper", "f1", "f2", "f3", "f4", "f5"]
        self.espeak["langs"] = ["en", "en-us", "en-sc", "en-n", "en-rp", "en-wm"]

    def build_morse_dict(self):
        self.morse["name"] = "morse"
        self.morse["voices"] = ["recording"]

    def build_google_dict(self):
        pass

    def build_fatts_dict(self):
        pass

    def build_marytts_dict(self):
        pass

    def build_spdsay_dict(self):
        pass

    # get config info for module
    def get_module_settings(self, tts_module):
        tts = self.config_core.get("tts")
        if not tts:
            self.log.error("could not get tts settings")
            self.speak("could not get tts settings")
            return {}
        tts_module = tts.get(tts_module)
        if not tts_module:
            self.log.error("could not get target tts module")
            self.speak("could not get target tts module")
            return {}
        return tts_module

    def get_current_tts(self):
        tts = self.config_core.get("tts")
        if not tts:
            self.log.error("could not get tts settings")
            tts = {}
        else:
            self.current_module = tts.get("module")
            if not self.current_module:
                self.log.error("could not get current tts module")
            else:
                self.current_module_settings = self.get_module_settings(
                    self.current_module)
        return tts

    def get_available_modules(self):
        # available == configured in this skill
        dicts = [self.mimic, self.espeak, self.morse, self.google,
                 self.fatts, self.marytts, self.spdsay]
        modules = []
        for module in dicts:
            if len(module.keys()):
                modules.append(module["name"])
        return modules

    # send bus message to update all configs
    def update_configs(self, config):
        # change config message
        self.config_update(config=config)
        sleep(1)
        self.get_current_tts()
        return True

    def stop(self):
        pass


def create_skill():
    return TTSSkill()
