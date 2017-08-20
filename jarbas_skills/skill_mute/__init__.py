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
from mycroft.util.log import getLogger

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class MuteSkill(MycroftSkill):
    def __init__(self):
        super(MuteSkill, self).__init__(name="MuteSkill")
        self.reload_skill = False
        self.external_reload = False
        self.external_shutdown = False

    def initialize(self):

        speak_enable_intent = IntentBuilder("SpeakEnableIntent").require("SpeakEnableKeyword").build()
        self.register_intent(speak_enable_intent, self.handle_speak_enable_intent)

        speak_disable_intent = IntentBuilder("SpeakDisableIntent").require("SpeakDisableKeyword").build()
        self.register_intent(speak_disable_intent, self.handle_speak_disable_intent)

    def handle_speak_disable_intent(self, event):
        self.speak_dialog("speak_disabled")
        self.emitter.emit(
            Message("speak.disable"))

    def handle_speak_enable_intent(self, event):
        self.speak_dialog("speak_enabled")
        self.emitter.emit(
            Message("speak.enable"))

    def stop(self):
        pass


def create_skill():
    return MuteSkill()
