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


# TODO check listener hash and redo wuw / hotword in listener.py to allow
# changes like in TTS

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from time import sleep
import webbrowser
import base64
import requests


def get_wave(fname):
    with open(fname) as infile:
        return base64.b64encode(infile.read())

__author__ = 'jarbas'


class HotwordSkill(MycroftSkill):
    def __init__(self):
        super(HotwordSkill, self).__init__()
        self.reload_skill = False
        self.snowboy_token = self.config_core.get("APIS", {}).get("Snowboy")
        self.snowboy_age_group = self.config_core.get("listener", {}).get("snowboy_age", "20_29")
        self.snowboy_gender = self.config_core.get("listener", {}).get("snowboy_gender", "M")
        if not self.snowboy_token:
            self.log.warn("No snowboy token, you can not create new hot words")

    def initialize(self):
        # get current settings
        self.get_listener_config()
        # build intents
        self.build_intents()

    def build_intents(self):

        intent = IntentBuilder("SoundWuWStatusIntent") \
            .require("StatusKeyword") \
            .require("SoundKeyword") \
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_status_sound_wuw_intent)

        intent = IntentBuilder("SaveWuWStatusIntent") \
            .require("StatusKeyword") \
            .require("SaveKeyword") \
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_status_save_wuw_intent)

        intent = IntentBuilder("EnableSaveWuWIntent") \
            .require("EnableKeyword")\
            .require("SaveKeyword")\
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_disable_save_wuw_intent)

        intent = IntentBuilder("DisableSaveWuWIntent") \
            .require("DisableKeyword")\
            .require("SaveKeyword")\
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_disable_save_wuw_intent)

        intent = IntentBuilder("DisableHotWSoundIntent") \
            .require("DisableKeyword")\
            .require("SoundKeyword")\
            .require("HotWKeyword")\
            .require("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_disable_hot_sound_intent)

        intent = IntentBuilder("EnableWuWSoundIntent") \
            .require("EnableKeyword")\
            .require("SoundKeyword")\
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_enable_wuw_sound_intent)

        intent = IntentBuilder("DisableWuWSoundIntent") \
            .require("DisableKeyword")\
            .require("SoundKeyword")\
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_disable_wuw_sound_intent)

        intent = IntentBuilder("CurrentWuWIntent") \
            .require("CurrentKeyword")\
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_current_wuw_intent)

        intent = IntentBuilder("AvailableWuWIntent") \
            .require("AvailableKeyword")\
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_available_wuw_intent)

        intent = IntentBuilder("AvailableHotWordsIntent") \
            .require("AvailableKeyword")\
            .require("HotWKeyword") \
            .build()
        self.register_intent(intent, self.handle_available_hot_intent)

        intent = IntentBuilder("ChangeWuWIntent") \
            .require("ChangeKeyword")\
            .require("WuWKeyword") \
            .optionally("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_change_wuw_intent)

        intent = IntentBuilder("EnableHotWIntent") \
            .require("EnableKeyword") \
            .require("HotWKeyword") \
            .optionally("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_enable_hot_intent)

        intent = IntentBuilder("DisableHotWIntent") \
            .require("DisableKeyword") \
            .require("HotWKeyword") \
            .optionally("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_disable_hot_intent)

        intent = IntentBuilder("CreateHotWIntent") \
            .require("CreateKeyword") \
            .require("HotWKeyword") \
            .require("TargetKeyword") \
            .build()
        self.register_intent(intent, self.handle_new_hotword_intent)

        intent = IntentBuilder("DemoHotWIntent") \
            .require("DemoKeyword")\
            .require("HotWKeyword") \
            .build()
        self.register_intent(intent, self.handle_demo_wuw_intent)

        intent = IntentBuilder("PermanentHotWIntent") \
            .require("PermanentKeyword")\
            .require("HotWKeyword") \
            .build()
        self.register_intent(intent, self.handle_permanent_wuw_intent)

        intent = IntentBuilder("DemoWuWIntent") \
            .require("DemoKeyword")\
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_demo_wuw_intent)

        intent = IntentBuilder("PermanentWuWIntent") \
            .require("PermanentKeyword")\
            .require("WuWKeyword") \
            .build()
        self.register_intent(intent, self.handle_permanent_wuw_intent)

    # intents
    def handle_new_hotword_intent(self, message):
        if not self.snowboy_token:
            self.speak("You need to create a snowboy token first")
            return
        # TODO request and record 3 samples of word
        waves = ["wave.wav", "wave2.wav", "wave3.wav"]
        hot_word = message.data["TargetKeyword"]
        new_model_path = self.new_snowboy_model(waves, hot_word)
        if new_model_path is not None:
            # TODO build hot word config
            config = {}
            self.speak("New hot word enabled")
            # save
            self.update_configs(config)
        else:
            self.speak("Could not create a new hot word")

    def handle_permanent_wuw_intent(self, message):
        self.speak("Making cached configuration permanent")
        self.config_update(save=True)

    def handle_current_wuw_intent(self, message):
        if not self.current_wuw:
            self.get_listener_config()
            if not self.current_wuw:
                self.speak("I could not get current wake word module from "
                       "configuration file")
                return
        self.speak("Current wake word module is " + self.current_wuw)

    def handle_available_hot_intent(self, message):
        if self.hot_words == {}:
            self.get_listener_config()
        for hot_word in self.hot_words.keys():
            module = self.hot_words[hot_word]["module"]
            active = self.hot_words[hot_word].get("active", True)
            self.speak("Available hot word for " + module + ". " + hot_word)
            if not active:
                self.speak("but is not activated")

    def handle_available_wuw_intent(self, message):
        self.speak("wake word is " + self.current_wuw)
        if not self.snowboy_models == {}:
            for hot_word in self.snowboy_models.keys():
                self.speak("Available wake word for snowboy. " + hot_word)

    def handle_change_wuw_intent(self, message):
        module = message.data.get("TargetKeyword").replace(" ","")
        if not module:
            self.speak("Change to what module?")
            return
        modules = ["snowboy", "pocketsphinx"]
        if module not in modules:
            self.speak("I dont know " + module + " module")
            return
        listener = self.get_listener_config()
        listener["module"] = module
        config = {"listener": listener}
        self.update_configs(config)
        sleep(2)
        self.speak("Wake Word module changed to " + module)

    def handle_enable_hot_intent(self, message):
        module = message.data.get("TargetKeyword")
        if not module:
            self.speak("Enable what hot word?")
            return
        listener = self.get_listener_config()
        if module in self.hot_words:
            if self.hot_words[module].get("active", True):
                self.speak(module + " is already active")
                return
            else:
                self.hot_words[module]["active"] = True
        else:
            self.speak("No such hot word")
            return
        listener["hot_words"] = self.hot_words
        config = {"listener": listener}
        self.update_configs(config)
        sleep(2)
        self.speak("Enabled " + module)

    def handle_disable_hot_intent(self, message):
        module = message.data.get("TargetKeyword")
        if not module:
            self.speak("disable what hot word?")
            return
        listener = self.get_listener_config()
        if module in self.hot_words:
            if not self.hot_words[module].get("active"):
                self.speak(module + " is already deactivated")
                return
            else:
                self.hot_words[module]["active"] = False
        else:
            self.speak("No such hot word")
            return

        listener["hot_words"] = self.hot_words
        config = {"listener": listener}
        self.update_configs(config)
        sleep(2)
        self.speak("disabled " + module)

    def handle_disable_hot_sound_intent(self, message):
        module = message.data.get("TargetKeyword")
        if not module:
            self.speak("disable what hot word?")
            return
        listener = self.get_listener_config()
        if module in self.hot_words:
            if not self.hot_words[module].get("sound"):
                self.speak(module + " sound is already deactivated")
                return
            else:
                self.hot_words[module]["sound"] = None
        else:
            self.speak("No such hot word")
            return

        listener["hot_words"] = self.hot_words
        config = {"listener": listener}
        self.update_configs(config)
        sleep(2)
        self.speak("disabled " + module)

    def handle_disable_wuw_sound_intent(self, message):
        config = {"confirm_listening": False}
        self.update_configs(config)
        sleep(2)
        self.speak("disabled wake word sound")

    def handle_enable_wuw_sound_intent(self, message):
        config = {"confirm_listening": True}
        self.update_configs(config)
        sleep(2)
        self.speak("enabled wake word sound")

    def handle_disable_save_wuw_intent(self, message):
        listener = self.get_listener_config()
        if listener.get("record_wake_words") == True:
            listener["record_wake_words"] = False
        else:
            self.speak("wake word saving already disabled")
            return
        config = {"listener": listener}
        self.update_configs(config)
        sleep(2)
        self.speak("disabled save wake words")

    def handle_enable_save_wuw_intent(self, message):
        listener = self.get_listener_config()
        if listener.get("record_wake_words") == True:
            self.speak("wake word saving already enabled")
        else:
            listener["record_wake_words"] = True
            return
        config = {"listener": listener}
        self.update_configs(config)
        sleep(2)
        self.speak("enabled wake word sound")

    def handle_status_save_wuw_intent(self, message):
        listener = self.get_listener_config()
        if listener.get("record_wake_words"):
            self.speak("wake word saving enabled")
        else:
            self.speak("wake word saving disabled")

    def handle_status_sound_wuw_intent(self, message):
        sound = self.config_core.get("confirm_listening")
        if sound:
            self.speak("wake word sound enabled")
        else:
            self.speak("wake word sound disabled")

    def handle_demo_wuw_intent(self, message):
        self.speak("Check this demo on youtube")
        webbrowser.open("https://youtu.be/GIkBh0VFmbc")

    # internal
    def get_listener_config(self):
        listener = self.config_core.get("listener")
        if not listener:
            self.log.error("could not get listener settings")
            listener = {}
        else:
            self.current_wuw_module = listener.get("module", "pocketsphinx")
            self.current_wuw = listener.get("wake_word", "hey jarbas")
            self.record = listener.get("record_wake_words", False)
            self.hot_words = listener.get("hot_words", {})
            self.snowboy_models = listener.get("models")

        return listener

    def new_snowboy_model(self, wav_files, hotword_name):
        out = hotword_name + ".pmdl"
        endpoint = "https://snowboy.kitt.ai/api/v1/train/"
        data = {
            "name": hotword_name,
            "language": self.lang,
            "age_group": self.snowboy_age_group,
            "gender": self.snowboy_gender,
            "microphone": '??',
            "token": self.snowboy_token,
            "voice_samples": [
                {"wave": get_wave(wav_files[0])},
                {"wave": get_wave(wav_files[1])},
                {"wave": get_wave(wav_files[2])}
            ]
        }
        response = requests.post(endpoint, json=data)
        if response.ok:
            with open(out, "w") as outfile:
                outfile.write(response.content)
            self.log("Saved snowboy model to '%s'." % out)
            return out
        else:
            self.log.error("Snowboy model request failed " + response.text)
            return None

    # send bus message to update all configs
    def update_configs(self, config):
        # change config message
        self.config_update(config=config, isSystem=True)
        sleep(1)
        self.get_listener_config()
        return True

    def stop(self):
        pass


def create_skill():
    return HotwordSkill()
