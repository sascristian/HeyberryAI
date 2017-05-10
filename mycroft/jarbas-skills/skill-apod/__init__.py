from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

try:
    # try to load display service
    import sys
    from os.path import dirname

    sys.path.append(dirname(dirname(__file__)))

    from service_display.displayservice import DisplayService
except:
    # not installed, use webrowser
    import webbrowser

import unirest
import urllib2
import os

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class FbPost():
    def __init__(self, emitter):
        self.emitter = emitter

    def post_text(self, text, id="me", speech= "Making a post on face book", link= None):
        self.emitter.emit(Message("fb_post_request", {"type":"text", "id":id, "link":link, "text":text, "speech":speech}))

    def post_link(self, link,  text="", id="me", speech= "Sharing a link on face book"):
        self.emitter.emit(Message("fb_post_request", {"type":"link", "id":id, "link":link, "text":text, "speech":speech}))


class AstronomyPicSkill(MycroftSkill):

    def __init__(self):
        super(AstronomyPicSkill, self).__init__(name="AstronomyPicSkill")
        try:
            self.key = self.config_apis["NASAAPI"]
        except:
            try:
                self.key = self.config["NASAAPI"]
            except:
                self.key = "DEMO_KEY"
        self.save = True
        try:
            self.save_path = self.config_core["database_path"] + "/astronomy_picture_of_the_day"
            self.txt_save_path = self.config_core["database_path"] + "/astronomy_picture_of_the_day_descriptions"
        except:
            try:
                self.save_path = self.config["save_path"]
                self.txt_save_path = self.config["txt_path"]
            except:
                self.save_path = os.path.dirname(__file__) + "/apod"
                self.txt_save_path = os.path.dirname(__file__) + "/apod"


        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        if not os.path.exists(self.txt_save_path):
            os.makedirs(self.txt_save_path)
        self.use_browser = False

    def initialize(self):
        apod_intent = IntentBuilder("ApodIntent").\
                require("APODKeyword").build()

        self.register_intent(apod_intent, self.handle_apod_intent)

        fb_apod_intent = IntentBuilder("FbApodIntent"). \
            require("fbAPODKeyword").build()

        self.register_intent(fb_apod_intent, self.handle_fb_apod_intent)

        try:
            self.display_service = DisplayService(self.emitter)
        except:
            self.use_browser = True
        self.poster = FbPost(self.emitter)

    def handle_apod_intent(self, message):
        apod_url = "https://api.nasa.gov/planetary/apod?api_key=" + self.key
        response = unirest.get(apod_url)
        title = response.body["title"]
        url = response.body["url"]
        summary = response.body["explanation"]

        apod = urllib2.Request(url)
        raw_img = urllib2.urlopen(apod).read()
        save_path = self.save_path + "/" + title.replace(" ", "_") + ".jpg"
        f = open(save_path, 'wb')
        f.write(raw_img)
        f.close()

        self.speak(title)
        if not self.use_browser:
            self.display_service.show(save_path, message.data["utterance"])
        else:
            webbrowser.open(save_path)
        self.speak(summary)

        if self.save:
            save_path = self.txt_save_path + "/" + title.replace(" ", "_") + ".txt"
            # save description
            f = open(save_path, 'wb')
            summary = summary.encode('utf-8')
            f.write(summary)
            f.close()

    def handle_fb_apod_intent(self, message):
        apod_url = "https://api.nasa.gov/planetary/apod?api_key=" + self.key
        response = unirest.get(apod_url)
        text = response.body["title"]
        url = response.body["url"]
        text += "\n" + response.body["explanation"]
        self.poster.post_link(link=url, text=text, speech="Sharing astronomy picture of the day on face book")

    def stop(self):
        pass


def create_skill():
    return AstronomyPicSkill()
