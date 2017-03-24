from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import unirest
import urllib2
import numpy as np
import cv2
import imutils
import os
import webbrowser

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

        self.reload_skill = False
        self.current = 0
        self.get_EPIC()

    def initialize(self):
        epic_intent = IntentBuilder("EPICIntent").\
                require("EPICKeyword").build()

        self.register_intent(epic_intent, self.handle_epic_intent)

        previous_epic_intent = IntentBuilder("PreviousEPICIntent"). \
            require("PreviousEPICKeyword").build()

        self.register_intent(previous_epic_intent, self.handle_previous_epic_intent)

        next_epic_intent = IntentBuilder("NextEPICIntent"). \
            require("NextEPICKeyword").build()

        self.register_intent(next_epic_intent, self.handle_next_epic_intent)

        about_epic_intent = IntentBuilder("AboutEPICIntent"). \
            require("aboutEPICKeyword").build()

        self.register_intent(about_epic_intent, self.handle_about_epic_intent)

        website_epic_intent = IntentBuilder("WebsiteEPICIntent"). \
            require("websiteEPICKeyword").build()

        self.register_intent(website_epic_intent, self.handle_website_epic_intent)

        try:
            self.disable_intent("PreviousEPICIntent")
        except:
            pass

    def handle_website_epic_intent(self, message):
        webbrowser.open("http://epic.gsfc.nasa.gov/")

    def handle_about_epic_intent(self, message):
        self.speak_dialog("aboutEPIC")

    def handle_epic_intent(self, message):
        self.current = 0
        self.EPIC(self.current)
        try:
            self.enable_intent("PreviousEPICIntent")
        except:
            pass


    def handle_previous_epic_intent(self, message):
        self.current += 1
        self.EPIC(self.current)

    def handle_next_epic_intent(self, message):
        self.current -= 1
        if self.current < 0:
            self.current = 0
            self.speak_dialog("maxEPIC")
            return

        self.EPIC(self.current)
        try:
            self.enable_intent("PreviousEPICIntent")
        except:
            pass


    def get_EPIC(self):
        url = "https://epic.gsfc.nasa.gov/api/natural"
        self.response = unirest.get(url)

    def EPIC(self, count=0):
        url = "https://epic.gsfc.nasa.gov/epic-archive/jpg/" + self.response.body[count]["image"] + ".jpg"

        pic = urllib2.urlopen(url)
        pic = np.array(bytearray(pic.read()), dtype=np.uint8)
        pic = cv2.imdecode(pic, -1)
        date = self.response.body[count]["date"]
        if self.save:
            save_path = self.save_path + "/" + date + ".jpg"
            cv2.imwrite(save_path, pic)
        pic = imutils.resize(pic, 500, 500)

        self.speak_dialog("EPIC", {"date": date})
        cv2.imshow("EPIC " + date, pic)
        cv2.waitKey(120)
        cv2.destroyAllWindows()

    def converse(self, transcript, lang="en-us"):
        try:
            if "previous" not in transcript[0]:
                self.disable_intent("PreviousEPICIntent")
                if "next" not in transcript[0]:
                    self.current = 0
        except:
            pass
        return False

    def stop(self):
        cv2.destroyAllWindows()


def create_skill():
    return EPICSkill()
