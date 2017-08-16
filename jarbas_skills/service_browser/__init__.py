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
from os.path import dirname
import socket, os
socket.setdefaulttimeout(300)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
import logging
from time import sleep
from urllib import urlretrieve
from mycroft.skills.displayservice import DisplayService
# disable logs from easyprocess, or there is too much spam from display init
logging.getLogger("easyprocess").setLevel(logging.WARNING)
# disable selenium logger
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_log
selenium_log.setLevel(logging.WARNING)

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
        self.emitter.on("browser_elements_stored", self.end_wait)
        self.emitter.on("browser_element_text", self.end_wait)
        self.emitter.on("browser_element_clicked", self.end_wait)
        self.emitter.on("browser_element_cleared", self.end_wait)
        self.emitter.on("browser_closed", self.end_wait)
        self.emitter.on("browser_restart_result", self.end_wait)
        self.emitter.on("browser_go_back_result", self.end_wait)
        self.emitter.on("browser_current_url_result", self.end_wait)
        self.emitter.on("browser_url_opened", self.end_wait)
        self.emitter.on("browser_add_cookies_response", self.end_wait)
        self.emitter.on("browser_get_cookies_response", self.end_wait)
        self.emitter.on("browser_title_response", self.end_wait)
        self.emitter.on("browser_get_atr_response", self.end_wait)
        if autostart:
            self.start_browser()

    def get_attribute(self, atr, element):
        self.waiting_for = "browser_get_atr_response"
        self.emitter.emit(Message("browser_get_atr_request", {"atr":atr, "element_name":element}))
        self.wait()
        return self.result.get("result")

    def get_cookies(self):
        self.waiting_for = "browser_get_cookies_response"
        self.emitter.emit(Message("browser_get_cookies_request", {}))
        self.wait()
        return self.result.get("cookies", [])

    def get_title(self):
        self.waiting_for = "browser_title_response"
        self.emitter.emit(Message("browser_title_request", {}))
        self.wait()
        return self.result.get("title", None)

    def add_cookies(self, cookies):
        self.waiting_for = "browser_add_cookies_response"
        self.emitter.emit(Message("browser_add_cookies_request", {"cookies":cookies}))
        self.wait()
        return self.result.get("sucess", False)

    def go_back(self):
        self.waiting_for = "browser_go_back_result"
        self.emitter.emit(Message("browser_go_back_request", {}))
        self.wait()
        return self.result.get("sucess", False)

    def get_current_url(self):
        self.waiting_for = "browser_current_url_result"
        self.emitter.emit(Message("browser_current_url_request", {}))
        self.wait()
        return self.result.get("url", None)

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
        # TODO throw exception
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
        self.wait()
        return self.result.get("sucess", False)

    def close_browser(self):
        self.waiting_for = "browser_closed"
        self.emitter.emit(Message("browser_close_request", {}))
        return self.wait()

    def open_url(self, url):
        self.waiting_for = "browser_url_opened"
        self.emitter.emit(Message("browser_url_request", {"url":url}))
        self.wait()
        return self.result.get("result", None)

    def get_element(self, data, name="temp", type="name"):
        self.waiting_for = "browser_element_stored"
        self.emitter.emit(Message("browser_get_element", {"type":type, "data":data, "element_name":name}))
        self.wait()
        return self.result.get("sucess", False)

    def get_elements(self, data, name="temp", type="name"):
        self.waiting_for = "browser_elements_stored"
        self.emitter.emit(Message("browser_get_elements", {"type":type, "data":data, "element_name":name}))
        self.wait()
        return self.result.get("sucess", False)

    def get_element_text(self, name="temp"):
        self.waiting_for = "browser_element_text"
        self.emitter.emit(Message("browser_get_element_text", {"element_name":name}))
        self.wait()
        return self.result.get("text", None)

    def get_available_elements(self):
        self.waiting_for = "browser_available_elements"
        self.emitter.emit(Message("browser_available_elements_request", {}))
        self.wait()
        return self.result.get("elements", {})

    def reset_elements(self):
        self.waiting_for = "browser_elements_reset_result"
        self.emitter.emit(Message("browser_reset_elements", {}))
        return self.wait()

    def clear_element(self, name="temp"):
        self.waiting_for = "browser_element_cleared"
        self.emitter.emit(Message("browser_clear_element", {"element_name":name}))
        self.wait()
        return self.result.get("sucess", False)

    def click_element(self, name="temp"):
        self.waiting_for = "browser_element_clicked"
        self.emitter.emit(Message("browser_click_element", {"element_name":name}))
        self.wait()
        return self.result.get("sucess", False)

    def send_keys_to_element(self, text, name="temp", special=False):
        self.waiting_for = "browser_sent_keys"
        self.emitter.emit(Message("browser_send_keys_to_element", {"element_name": name, "special_key":special, "text":text}))
        self.wait()
        return self.result.get("sucess", False)


class BrowserService(MycroftSkill):
    def __init__(self):
        super(BrowserService, self).__init__(name="BrowserSkill")
        self.reload_skill = False
        # start virtual display
        display = Display(visible=0, size=(800, 600))
        display.start()
        self.driver = None
        self.elements = {}
        self.save_path = dirname(__file__) + "/inspirobot"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def initialize(self):
        started = self.start_browser()
        self.log.info("browser service started: " + str(started))
        self.emitter.on("browser_restart_request", self.handle_restart_browser)
        self.emitter.on("browser_close_request", self.handle_close_browser)
        self.emitter.on("browser_url_request", self.handle_go_to_url)
        self.emitter.on("browser_title_request", self.handle_title_request)
        self.emitter.on("browser_go_back_request", self.handle_go_back)
        self.emitter.on("browser_current_url_request", self.handle_current_url)
        self.emitter.on("browser_get_element", self.handle_get_element)
        self.emitter.on("browser_get_elements", self.handle_get_elements)
        self.emitter.on("browser_get_element_text", self.handle_get_element_text)
        self.emitter.on("browser_available_elements_request", self.handle_available_elements)
        self.emitter.on("browser_send_keys_to_element", self.handle_send_keys)
        self.emitter.on("browser_reset_elements", self.handle_reset_elements)
        self.emitter.on("browser_click_element", self.handle_click_element)
        self.emitter.on("browser_clear_element", self.handle_clear_element)
        self.emitter.on("browser_get_cookies_request", self.handle_get_cookies)
        self.emitter.on("browser_add_cookies_request", self.handle_add_cookies)
        self.emitter.on("browser_get_atr_request", self.handle_get_attribute)
        self.build_intents()

    def build_intents(self):
        ask_cleverbot_intent = IntentBuilder("AskCleverbotIntent") \
            .require("Ask").build()
        self.register_intent(ask_cleverbot_intent,
                             self.handle_ask_cleverbot_intent)

        inspirobot_intent = IntentBuilder("InspirobotIntent") \
            .require("inspirobot").build()
        self.register_intent(inspirobot_intent,
                             self.handle_inspirobot_intent)
        self.display_service = DisplayService(self.emitter)

    def handle_ask_cleverbot_intent(self, message):
        ask = message.data.get("Ask")
        # get a browser control instance, optionally set to auto-start/restart browser
        browser = BrowserControl(self.emitter)#, autostart=True)
        # restart webbrowser if it is open (optionally)
        #started = browser.start_browser()
        #if not started:
        #    # TODO throw some error
        #    return
        browser.reset_elements()
        # get clevebot url
        open = browser.open_url("www.cleverbot.com")
        if open is None:
            return
        # search this element by type and name it "input"
        browser.get_element(data="stimulus", name="input", type="name")
        # clear element named input
        #browser.clear_element("input")
        # send text to element named "input"
        browser.send_keys_to_element(text=ask, name="input", special=False)
        # send a key_press to element named "input"
        browser.send_keys_to_element(text="RETURN", name="input", special=True)

        # wait until you find element by xpath and name it sucess
        received = False
        fails = 0
        response = " "
        from time import sleep
        while response == " ":
            while not received and fails < 5:
                # returns false when element wasnt found
                # this appears only after cleverbot finishes answering
                received = browser.get_element(data=".//*[@id='snipTextIcon']", name="sucess", type="xpath")
                fails += 1
                sleep(0.5)

            # find element by xpath, name it "response"
            browser.get_element(data=".//*[@id='line1']/span[1]", name="response", type="xpath")
            # get text of the element named "response"
            response = browser.get_element_text("response")

        self.speak(response)
        # clean the used elements for this session
        browser.reset_elements()
        # optionally close the browser, but dont or other services may crash or take longer
        #browser.close_browser()

    def handle_inspirobot_intent(self, message):
        # get a browser control instance, optionally set to auto-start/restart browser
        browser = BrowserControl(self.emitter)  # , autostart=True)
        # restart webbrowser if it is open (optionally)
        # started = browser.start_browser()
        # if not started:
        #    # TODO throw some error
        #    return
        browser.reset_elements()
        # get clevebot url
        open = browser.open_url("http://inspirobot.me/")
        if open is None:
            return
        inspirobot = ".//*[@id='bot-dark']" #when this is gone pic is ready
        generate = ".//*[@id='top']/div[1]/div[2]/div/div[2]"
        pic = ".//*[@id='top']/div[1]/div[1]/img"

        # search generate button
        browser.get_element(data=generate, name="generate", type="xpath")
        # click generate button
        browser.click_element("generate")

        # wait until you find pic
        fails = 0
        sucess = False
        while fails < 5 and not sucess:
            browser.get_element(data="generated-image", name="pic", type="class")
            src = browser.get_attribute('src', 'pic')
            if "generated.inspirobot" not in src:
                fails += 1
                sleep(0.5)
            else:
                sucess = True
        if not sucess or not src:
            self.speak("could not get inspirobot generated picture")
            return

        out_path = self.save_path + "/" + time.asctime() + ".jpg"

        # download the image
        urlretrieve(src, out_path.replace(" ", "_"))

        self.speak("Here is your Inspirobot picture", metadata={"file":out_path, "url":src})
        self.display_service.display([out_path],
                                     utterance=message.data.get("utterance"))
        # clean the used elements for this session
        browser.reset_elements()
        # optionally close the browser, but dont or other services may crash or take longer
        # browser.close_browser()

    def handle_get_attribute(self, message):
        atr = message.data.get("atr")
        elem = message.data.get("element_name")
        if elem not in self.elements.keys():
            self.log.error("No such element")
            self.emitter.emit(Message("browser_get_atr_response", {"atr": atr, "result":None, "error":"No such element"}))
            return
        result = self.elements[elem].get_attribute(atr)
        self.emitter.emit(Message("browser_get_atr_response", {"atr": atr, "result":result}))

    def handle_get_cookies(self, message):
        cookies = self.driver.get_cookies()
        self.emitter.emit(Message("browser_get_cookies_response", {"cookies":cookies}))

    def handle_title_request(self, message):
        self.emitter.emit(Message("browser_title_response", {"title": self.driver.title}))

    def handle_add_cookies(self, message):
        cookies = message.data.get("cookies", [])
        if len(cookies) == 0:
            self.emitter.emit(Message("browser_add_cookies_response",
                                      {"sucess": False, "cookies": cookies, "cookie_number": len(cookies)}))
            return
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.emitter.emit(Message("browser_add_cookies_response", {"sucess":True, "cookies":cookies, "cookie_number":len(cookies)}))

    def handle_go_back(self, message):
        self.driver.back()
        self.emitter.emit(Message("browser_go_back_result", {"sucess": True, "url": self.driver.current_url}))

    def handle_current_url(self, message):
        self.emitter.emit(Message("browser_current_url_result", {"sucess": True, "url": self.driver.current_url, "title":self.driver.title}))

    def start_browser(self):

        try:
            self.driver.quit()
        except Exception as e:
            self.log.debug("tried to close driver but: " + str(e))

        try:
            self.driver = webdriver.Firefox(timeout=60)
            return True
        except Exception as e:
            self.log.error("Exception: " + str(e))
        return False

    def handle_clear_element(self, message):
        # TODO error checking, see if element in self.elemtns.keys()
        name = message.data.get("element_name")
        try:
            self.elements[name].clear()
            self.emitter.emit(Message("browser_element_cleared", {"sucess": True, "element": name}))
        except Exception as e:
            self.log.error(e)
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
        if key:
            if text == "RETURN":
                element.send_keys(Keys.RETURN)
            else:
                # TODO all keys
                self.emitter.emit(Message("browser_sent_keys", {"sucess":False, "name": name, "data": text, "error": "special key not yet implemented"}))
                return
        else:
            element.send_keys(text)
            # TODO change this, needed because text may be big
            time.sleep(1)
        self.emitter.emit(Message("browser_sent_keys", {"sucess":True, "name": name, "data": text}))

    def handle_get_elements(self, message):
        get_by = message.data.get("type") #xpath, css, name, id
        data = message.data.get("data") # name, xpath expression....
        name = message.data.get("element_name")# how to call this element later
        try:
            i = 0
            if get_by == "xpath":
                for e in self.driver.find_elements_by_xpath(data):
                    self.elements[name+str(i)] = e
                    i+=1
            elif get_by == "css":
                for e in self.driver.find_elements_by_css(data):
                    self.elements[name + str(i)] = e
                    i += 1
            elif get_by == "name":
                for e in self.driver.find_elements_by_name(data):
                    self.elements[name + str(i)] = e
                    i += 1
            elif get_by == "class":
                for e in self.driver.find_elements_by_class_name(data):
                    self.elements[name + str(i)] = e
                    i += 1
            elif get_by == "link_text":
                for e in self.driver.find_elements_by_link_text(data):
                    self.elements[name + str(i)] = e
                    i += 1
            elif get_by == "partial_link_text":
                for e in self.driver.find_elements_by_partial_link_text(data):
                    self.elements[name + str(i)] = e
                    i += 1
            elif get_by == "tag_name":
                for e in self.driver.find_elements_by_tag_name(data):
                    self.elements[name + str(i)] = e
                    i += 1
            elif get_by == "id":
                for e in self.driver.find_elements_by_id(data):
                    self.elements[name + str(i)] = e
                    i += 1
            else:
                self.log.error("Invalid element type: " + get_by)
                self.emitter.emit(
                    Message("browser_elements_stored", {"name": name, "type": get_by, "data": data, "sucess": False}))
                return
            self.emitter.emit(Message("browser_elements_stored", {"name":name, "type":get_by, "data":data, "sucess":True}))
        except Exception as e:
            self.log.error(e)
            self.emitter.emit(Message("browser_elements_stored", {"name": name, "type": get_by, "data": data, "sucess":False}))

    def handle_get_element(self, message):
        get_by = message.data.get("type") #xpath, css, name, id
        data = message.data.get("data").encode('ascii', 'ignore').decode('ascii') # name, xpath expression....
        name = message.data.get("element_name")# how to call this element later
        try:
            # todo extra
            if get_by == "xpath":
                self.elements[name] = self.driver.find_element_by_xpath(data)
            elif get_by == "css":
                self.elements[name] = self.driver.find_element_by_css(data)
            elif get_by == "name":
                self.elements[name] = self.driver.find_element_by_name(data)
            elif get_by == "class":
                self.elements[name] = self.driver.find_element_by_class_name(data)
            elif get_by == "link_text":
                self.elements[name] = self.driver.find_element_by_link_text(data)
            elif get_by == "partial_link_text":
                self.elements[name] = self.driver.find_element_by_partial_link_text(data)
            elif get_by == "tag_name":
                self.elements[name] = self.driver.find_element_by_tag_name(data)
            elif get_by == "id":
                self.elements[name] = self.driver.find_element_by_id(data)
            else:
                self.log.error("Invalid element type: " + get_by)
                self.emitter.emit(
                    Message("browser_element_stored", {"name": name, "type": get_by, "data": data, "sucess": False}))
                return
            self.emitter.emit(Message("browser_element_stored", {"name":name, "type":get_by, "data":data, "sucess":True}))
        except Exception as e:
            self.log.error(e)
            self.emitter.emit(Message("browser_element_stored", {"name": name, "type": get_by, "data": data, "sucess":False}))

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
        except Exception as e:
            self.log.error(e)
            self.emitter.emit(Message("browser_element_clicked", {"sucess": False, "element": name}))

    def handle_close_browser(self, message):
        try:
            self.driver.close()
        except Exception as e:
            self.log.error(e)
        self.emitter.emit(Message("browser_closed", {}))

    def handle_restart_browser(self, message):
        started = self.start_browser()
        self.emitter.emit(Message("browser_restart_result", {"sucess":started}))

    def handle_go_to_url(self, message):
        url = message.data.get("url")
        if "http" not in url:
            url = "http://"+url
        fails = 0
        while fails < 5:
            try:
                self.driver.get(url)
                self.log.info(u"url: " + self.driver.current_url)
                self.log.info(u"title: " + self.driver.title)
                break
            except Exception as e:
                self.log.error(e)
            time.sleep(0.5)
            fails += 1
        self.emitter.emit(Message("browser_url_opened", {"result": self.driver.current_url, "page_title": self.driver.title, "requested_url": url}))

    def stop(self):
        try:
            self.driver.quit()
            Display.close()
        except Exception as e:
            self.log.error(e)


def create_skill():
    return BrowserService()
