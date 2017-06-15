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
from os.path import dirname, join
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

sys.path.append(join(dirname(__file__), 'geckodriver'))

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class BrowserService(MycroftSkill):
    def __init__(self):
        super(BrowserService, self).__init__(name="BrowserSkill")
        # start virtual display
        display = Display(visible=0, size=(800, 600))
        display.start()
        # start working variables
        self.driver = None
        self.elements = {}

    def initialize(self):
        started = self.start_browser()
        self.log.info("browser started: " + str(started))
        self.emitter.on("browser_restart_request", self.handle_restart_browser)
        self.emitter.on("browser_close_request", self.handle_close_browser)
        self.emitter.on("browser_url_request", self.handle_go_to_url)
        self.emitter.on("browser_get_element", self.handle_get_element)
        self.emitter.on("browser_get_element_text", self.handle_get_element_text)
        self.emitter.on("browser_available_elements", self.handle_available_elements)
        self.emitter.on("browser_send_keys_to_element", self.handle_send_keys)
        self.emitter.on("browser_reset_elements", self.handle_reset_elements)
        self.emitter.on("browser_click_element", self.handle_click_element)
        self.build_intents()

    def build_intents(self):
        pass

    def start_browser(self):
        try:
            self.driver.close()
        except:
            pass
        try:
            self.driver = webdriver.Firefox()
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def handle_clear_element(self, message):
        # TODO error checking, see if element in self.elemtns.keys()
        name = message.data.get("element_name")
        self.elements[name].clear()
        self.emitter.emit("browser_element_cleared", {"element": name})

    def handle_reset_elements(self, message):
        self.elements = {}
        self.emitter.emit("browser_elements_reset", {"elements": self.elements})

    def handle_available_elements(self, message):
        self.emitter.emit("browser_available_elements", {"elements": self.elements})

    def handle_send_keys(self, message):
        # TODO error checking, see if element in self.elemtns.keys()
        name = message.data.get("element_name")
        key = message.data.get("special_key")
        text = message.data.get("text")
        element = self.elements[name]
        if key is not None:
            if key == "RETURN":
                element.send_keys(Keys.RETURN)
            else:
                # TODO all keys
                self.emitter.emit("browser_keys_fail", {"name": name, "data": text, "error": "special key not yet implemented"})
                return
        else:
            element.send_keys(text)
        self.emitter.emit("browser_sent_keys", {"name": name, "data": text})

    def handle_get_element(self, message):
        # TODO error handling in case element not exist
        get_by = message.data.get("type") #xpath, css, name
        data = message.data.get("data") # name, xpath expression....
        name = message.data.get("element_name") # how to call this element later
        if get_by == "xpath":
            self.elements[name] = self.driver.find_element_by_xpath(data)
        elif get_by == "css":
            self.elements[name] = self.driver.find_element_by_css(data)
        elif get_by == "name":
            self.elements[name] = self.driver.find_element_by_name(data)
        elif get_by == "id":
            self.elements[name] = self.driver.find_element_by_id(data)
        self.emitter.emit("browser_element_stored", {"name":name, "type":type, "data":data})

    def handle_get_element_text(self, message):
        # TODO error checking, see if element in self.elemtns.keys()
        name = message.data.get("element_name")
        element = self.elements[name]
        self.emitter.emit("browser_element_text", {"name": name, "text": element.text})

    def handle_click_element(self, message):
        # TODO error checking, see if element in self.elemtns.keys()
        name = message.data.get("element_name")
        self.elements[name].click()
        self.emitter.emit("browser_element_clicked", {"element": name})

    def handle_close_browser(self, message):
        self.driver.close()
        self.emitter.emit("browser_closed", {})

    def handle_restart_browser(self, message):
        started = self.start_browser()
        self.emitter.emit("browser_restart_result", {"result":started})

    def handle_go_to_url(self, message):
        url = message.data.get("url")
        self.driver.get(url)
        self.emitter.emit("browser_url_opened", {"result": self.driver.current_url, "page_title": self.driver.title, "requested_url": url})

    def stop(self):
        try:
            self.driver.close()
        except:
            pass


def create_skill():
    return BrowserService()
