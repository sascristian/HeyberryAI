from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import unirest
import urllib2
import numpy as np
import cv2
import imutils
import os
import time

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class EPICSkill(MycroftSkill):

    def __init__(self):
        super(EPICSkill, self).__init__(name="EPICSkill")
        self.save = True
        try:
            self.save_path = self.config_core["database_path"] + "/epic"
        except:
            self.save_path = self.config["save_path"]

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def initialize(self):
        epic_intent = IntentBuilder("EPICIntent").\
                require("EPICKeyword").build()

        self.register_intent(epic_intent, self.handle_epic_intent)

        about_epic_intent = IntentBuilder("AboutEPICIntent"). \
            require("aboutEPICKeyword").build()

        self.register_intent(about_epic_intent, self.handle_about_epic_intent)

    def handle_about_epic_intent(self, message):
        self.speak_dialog("aboutEPIC")

    def handle_epic_intent(self, message):
        url = "https://epic.gsfc.nasa.gov/api/natural"
        response = unirest.get(url)
        url = "https://epic.gsfc.nasa.gov/epic-archive/jpg/" + response.body[0]["image"] + ".jpg"

        pic = urllib2.urlopen(url)
        pic = np.array(bytearray(pic.read()), dtype=np.uint8)
        pic = cv2.imdecode(pic, -1)

        if self.save:
            save_path = self.save_path + "/" + time.asctime() + ".jpg"
            cv2.imwrite(save_path, pic)
        pic = imutils.resize(pic, 500, 500)

        self.speak_dialog("EPIC")
        cv2.imshow("EPIC " + time.asctime(), pic)
        cv2.waitKey(120)
        cv2.destroyAllWindows()

    def stop(self):
        cv2.destroyAllWindows()


def create_skill():
    return EPICSkill()
