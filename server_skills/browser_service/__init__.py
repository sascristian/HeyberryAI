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
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from time import sleep
from pyvirtualdisplay import Display


__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class BrowserService(MycroftSkill):
    def __init__(self):
        super(BrowserService, self).__init__(name="BrowserSkill")
        # start vitual display
        display = Display(visible=0, size=(800, 600))
        display.start()
        self.driver = None

    def initialize(self):
        started = self.start_browser()
        self.log.info("browser started: " + str(started))
        sleep(200)
       # hello_world_intent = IntentBuilder("HelloWorldIntent"). \
       #     require("HelloWorldKeyword").build()
       # self.register_intent(hello_world_intent,
        #                     self.handle_hello_world_intent)

    def start_browser(self):
        try:
            self.driver.close()
        except:
            pass
        try:
            self.driver = webdriver.Firefox()
            return True
        except:
            return False

    def handle_hello_world_intent(self, message):
        self.speak_dialog("hello.world")

    def stop(self):
        pass


def create_skill():
    return BrowserService()
