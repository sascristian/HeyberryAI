from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import unirest
import urllib2
import numpy as np
import cv2
import imutils
import os

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class AstronomyPicSkill(MycroftSkill):

    def __init__(self):
        super(AstronomyPicSkill, self).__init__(name="AstronomyPicSkill")
        try:
            self.key = self.config_apis["NASAAPI"]
        except:
            self.key = self.config["NASAAPI"]
        self.save = True
        try:
            self.save_path = self.config_core["database_path"] + "/astronomy_picture_of_the_day"
        except:
            self.save_path = self.config["save_path"]

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def initialize(self):
        apod_intent = IntentBuilder("ApodIntent").\
                require("APODKeyword").build()

        self.register_intent(apod_intent, self.handle_apod_intent)

    def handle_apod_intent(self, message):
        apod_url = "https://api.nasa.gov/planetary/astronomy_picture_of_the_day?api_key=" + self.key
        response = unirest.get(apod_url)
        title = response.body["title"]
        url = response.body["url"]
        summary = response.body["explanation"]

        apod = urllib2.urlopen(url)
        apod = np.array(bytearray(apod.read()), dtype=np.uint8)
        apod = cv2.imdecode(apod, -1)

        if self.save:
            save_path = self.save_path + "/" + title.replace(" ", "_") + ".jpg"
            cv2.imwrite(save_path, apod)
            # save description
            f = open(self.save_path+"/"+title.replace(" ", "_")+".txt", 'wb')
            f.write(summary)
            f.close()
        apod = imutils.resize(apod, 500, 500)

        self.speak(title)
        cv2.imshow("Astronomy Picture of the Day", apod)
        self.speak(summary)
        cv2.waitKey(120)
        cv2.destroyAllWindows()

    def stop(self):
        cv2.destroyAllWindows()


def create_skill():
    return AstronomyPicSkill()
