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
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from time import sleep
__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class SelfDestructSkill(MycroftSkill):
    def __init__(self):
        super(SelfDestructSkill, self).__init__()

    def initialize(self):
        intent = IntentBuilder("SelfDestructIntent").require("SelfDestructHotword").build()
        self.register_intent(intent, self.handle_intent)

    def handle_intent(self, message):
        sleep(4)
        self.speak("self destruct in t minus")
        i = 5
        while i > 0:
            self.speak(str(i))
            sleep(1)
            i -= 1
        self.speak("I'm sorry, im afraid i can't do that")

    def stop(self):
        pass


def create_skill():
    return SelfDestructSkill()
