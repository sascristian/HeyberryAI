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
import time
from os.path import dirname, join
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
# so geckodriver can be found
sys.path.append(dirname(__file__))

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import subprocess

__author__ = 'jarbas'


class BrowserControl():
    def __init__(self, emitter, timeout=20, logger=None, autostart=False):
        self.emitter = emitter
        if logger is None:
            logger = getLogger("Mycroft-Browser")
        self.logger = logger
        self.timeout = timeout
        self.waiting = False
        self.result = {}
        self.waiting_for = ""
        self.emitter.on("browser_element_cleared", self.end_wait)
        self.emitter.on("browser_available_elements", self.end_wait)
        self.emitter.on("browser_elements_reset_result", self.end_wait)
        self.emitter.on("browser_sent_keys", self.end_wait)
        self.emitter.on("browser_element_stored", self.end_wait)
        self.emitter.on("browser_element_text", self.end_wait)
        self.emitter.on("browser_element_clicked", self.end_wait)
        self.emitter.on("browser_element_cleared", self.end_wait)
        self.emitter.on("browser_closed", self.end_wait)
        self.emitter.on("browser_restart_result", self.end_wait)
        self.emitter.on("browser_url_opened", self.end_wait)
        if autostart:
            self.start_browser()

    def end_wait(self, message):
        if message.type == self.waiting_for:
            self.waiting = False
            self.result = message.data

    def wait(self):
        self.waiting = True
        start = time.time()
        elapsed = 0
        while self.waiting and elapsed <= self.timeout:
            elapsed = time.time() - start
            time.sleep(0.3)
        if self.waiting:
            result = False
        else:
            result = True
        self.waiting = False
        return result

    def get_data(self):
        return self.result

    def start_browser(self):
        self.waiting_for = "browser_restart_result"
        self.emitter.emit(Message("browser_restart_request", {}))
        self.logger.info("Browser restart: " + str(self.wait()))
        try:
            return self.result["sucess"]
        except:
            return False

    def close_browser(self):
        self.waiting_for = "browser_closed"
        self.emitter.emit(Message("browser_close_request", {}))
        wait = self.wait()
        self.logger.info("Browser close: " + str(wait))
        return wait

    def open_url(self, url):
        self.waiting_for = "browser_url_opened"
        self.emitter.emit(Message("browser_url_request", {"url":url}))
        self.logger.info("Browser url open: " + str(self.wait()))
        try:
            return self.result["result"]
        except:
            return None

    def get_element(self, data, name="temp", type="name"):
        self.waiting_for = "browser_element_stored"
        self.emitter.emit(Message("browser_get_element", {"type":type, "data":data, "name":name}))
        self.logger.info("Browser get element: " + str(self.wait()))
        try:
            return self.result["sucess"]
        except:
            return False

    def get_element_text(self, name="temp"):
        self.waiting_for = "browser_element_text"
        self.emitter.emit(Message("browser_get_element_text", {"element_name":name}))
        self.logger.info("Browser get element text: " + str(self.wait()))
        try:
            return self.result["text"]
        except:
            return None

    def get_available_elements(self):
        self.waiting_for = "browser_available_elements"
        self.emitter.emit(Message("browser_available_elements_request", {}))
        self.logger.info("Browser available elements: " + str(self.wait()))
        try:
            return self.result["elements"]
        except:
            return {}

    def reset_elements(self):
        self.waiting_for = "browser_elements_reset_result"
        self.emitter.emit(Message("browser_reset_elements", {}))
        wait = self.wait()
        self.logger.info("Browser reset elements: " + str(wait))
        return wait

    def clear_element(self, name="temp"):
        self.waiting_for = "browser_element_cleared"
        self.emitter.emit(Message("browser_clear_element", {"element_name":name}))
        self.logger.info("Browser clear element: " + str(self.wait()))
        try:
            return self.result["sucess"]
        except:
            return False

    def click_element(self, name="temp"):
        self.waiting_for = "browser_element_clicked"
        self.emitter.emit(Message("browser_click_element", {"element_name":name}))
        self.logger.info("Browser click element: " + str(self.wait()))
        try:
            return self.result["sucess"]
        except:
            return False

    def send_keys_to_element(self, text, name="temp", special=False):
        self.waiting_for = "browser_sent_keys"
        self.emitter.emit(Message("browser_send_keys_to_element", {"element_name": name, "special_key":special, "text":text}))
        self.logger.info("Browser send keys element: " + str(self.wait()))
        try:
            return self.result["sucess"]
        except:
            return False


class BrowserService(MycroftSkill):
    def __init__(self):
        super(BrowserService, self).__init__(name="BrowserSkill")
        # start virtual display
        display = Display(visible=0, size=(800, 600))
        display.start()
        # start working variables
        self.driver = None
        self.elements = {}
        try:
            self.binary = FirefoxBinary("/usr/bin/firefox")
        except:
            self.log.error("Could not find firefox")

    def initialize(self):
        started = self.start_browser()
        self.log.info("browser service started: " + str(started))
        self.emitter.on("browser_restart_request", self.handle_restart_browser)
        self.emitter.on("browser_close_request", self.handle_close_browser)
        self.emitter.on("browser_url_request", self.handle_go_to_url)
        self.emitter.on("browser_get_element", self.handle_get_element)
        self.emitter.on("browser_get_element_text", self.handle_get_element_text)
        self.emitter.on("browser_available_elements_request", self.handle_available_elements)
        self.emitter.on("browser_send_keys_to_element", self.handle_send_keys)
        self.emitter.on("browser_reset_elements", self.handle_reset_elements)
        self.emitter.on("browser_click_element", self.handle_click_element)
        self.emitter.on("browser_clear_element", self.handle_clear_element)
        self.build_intents()

    def build_intents(self):
        ask_cleverbot_intent = IntentBuilder("AskCleverbotIntent") \
            .require("Ask").build()
        self.register_intent(ask_cleverbot_intent,
                             self.handle_ask_cleverbot_intent)

    def handle_ask_cleverbot_intent(self, message):
        ask = message.data.get("Ask")
        # get a browser control instance, optionally set to auto-start/restart browser
        browser = BrowserControl(self.emitter)#, autostart=True)
        # restart webbrowser if it is open (optionally)
        started = browser.start_browser()
        if not started:
            # TODO throw some error
            return
        # get clevebot url
        browser.open_url("www.cleverbot.com")
        # search this element by type and name it "input"
        browser.get_element(data="stimulus", name="input", type="name")
        # clear element named input
        browser.clear_element("input")
        # send text to element named "input"
        browser.send_keys_to_element(text=ask, name="input", special=False)
        # send a key_press to element named "input"
        browser.send_keys_to_element(text="RETURN", name="input", special=True)

        # wait until you find element by xpath and name it sucess
        received = False
        fails = 0
        while not received and fails < 5:
            # returns false when element wasnt found
            # this appears only after cleverbot finishes answering
            received = browser.get_element(data=".//*[@id='snipTextIcon']", name="sucess", type="xpath")
            fails += 1

        # find element by xpath, name it "response"
        browser.get_element(data=".//*[@id='line1']/span[1]", name="response", type="xpath")
        # get text of the element named "response"
        response = browser.get_element_text("response")
        self.speak(response)
        # clean the used elements for this session
        browser.reset_elements()
        # optionally close the browser
        browser.close_browser()

    def start_browser(self):
        try:
            self.driver.close()
        except Exception as e:
            self.log.debug("tried to close driver but: " + str(e))
        try:
            try:
                self.driver = webdriver.Firefox(firefox_binary=self.binary)
            except:
                self.driver = webdriver.Firefox()
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def handle_clear_element(self, message):
        # TODO error checking, see if element in self.elemtns.keys()
        name = message.data.get("element_name")
        try:
            self.elements[name].clear()
            self.emitter.emit(Message("browser_element_cleared", {"sucess": True, "element": name}))
        except:
            self.emitter.emit(Message("browser_element_cleared", {"sucess": False, "element": name}))

    def handle_reset_elements(self, message):
        self.elements = {}
        self.emitter.emit(Message("browser_elements_reset_result", {"elements": self.elements}))

    def handle_available_elements(self, message):
        self.emitter.emit(Message("browser_available_elements", {"elements": self.elements}))

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
                self.emitter.emit(Message("browser_sent_keys", {"sucess":False, "name": name, "data": text, "error": "special key not yet implemented"}))
                return
        else:
            element.send_keys(text)
        self.emitter.emit(Message("browser_sent_keys", {"sucess":True, "name": name, "data": text}))

    def handle_get_element(self, message):
        get_by = message.data.get("type") #xpath, css, name, id
        data = message.data.get("data") # name, xpath expression....
        name = message.data.get("element_name") # how to call this element later
        try:
            if get_by == "xpath":
                self.elements[name] = self.driver.find_element_by_xpath(data)
            elif get_by == "css":
                self.elements[name] = self.driver.find_element_by_css(data)
            elif get_by == "name":
                self.elements[name] = self.driver.find_element_by_name(data)
            elif get_by == "id":
                self.elements[name] = self.driver.find_element_by_id(data)
            self.emitter.emit(Message("browser_element_stored", {"name":name, "type":type, "data":data, "sucess":True}))
        except:
            self.emitter.emit(Message("browser_element_stored", {"name": name, "type": type, "data": data, "sucess":False}))

    def handle_get_element_text(self, message):
        # TODO error checking, see if element in self.elemtns.keys()
        name = message.data.get("element_name")
        element = self.elements[name]
        self.emitter.emit(Message("browser_element_text", {"name": name, "text": element.text}))

    def handle_click_element(self, message):
        name = message.data.get("element_name")
        try:
            self.elements[name].click()
            self.emitter.emit(Message("browser_element_clicked", {"sucess":True, "element": name}))
        except:
            self.emitter.emit(Message("browser_element_clicked", {"sucess": False, "element": name}))

    def handle_close_browser(self, message):
        try:
            self.driver.close()
        except:
            pass
        self.emitter.emit(Message("browser_closed", {}))

    def handle_restart_browser(self, message):
        started = self.start_browser()
        self.emitter.emit(Message("browser_restart_result", {"sucess":started}))

    def handle_go_to_url(self, message):
        url = message.data.get("url")
        self.driver.get(url)
        self.emitter.emit(Message("browser_url_opened", {"result": self.driver.current_url, "page_title": self.driver.title, "requested_url": url}))

    def stop(self):
        try:
            self.driver.close()
        except:
            pass


def create_skill():
    return BrowserService()
