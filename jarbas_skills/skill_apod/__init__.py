from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.skills.displayservice import DisplayService

import unirest
import urllib2
import os

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class AstronomyPicSkill(MycroftSkill):
    def __init__(self):
        super(AstronomyPicSkill, self).__init__(name="AstronomyPicSkill")
        try:
            self.key = self.config_core.get("APIS").get("NASA")
        except:
            try:
                self.key = self.config["NASAAPI"]
            except:
                self.key = "DEMO_KEY"
        self.save_text = True
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

    def initialize(self):
        apod_intent = IntentBuilder("ApodIntent").\
                require("APODKeyword").build()
        self.register_intent(apod_intent, self.handle_apod_intent)

        self.display_service = DisplayService(self.emitter, self.name)

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
        self.display_service.display([save_path],
                                     utterance=message.data.get("utterance"))
        self.speak(summary, metadata={"url":
                                          "https://api.nasa.gov/planetary/apod"})

        if self.save_text:
            save_path = self.txt_save_path + "/" + title.replace(" ", "_") + ".txt"
            # save description
            f = open(save_path, 'wb')
            summary = summary.encode('utf-8')
            f.write(summary)
            f.close()

    def stop(self):
        pass


def create_skill():
    return AstronomyPicSkill()
