from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.skills.displayservice import DisplayService

import unirest
import urllib2
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
            try:
                self.save_path = self.config["save_path"]
            except:
                self.save_path = os.path.dirname(__file__) + "/epic"

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.reload_skill = False
        self.current = 0
        self.lenght = 0
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

        fb_epic_intent = IntentBuilder("FbEPICIntent"). \
            require("fbEPICKeyword").build()

        self.register_intent(fb_epic_intent, self.handle_fb_epic_intent)

        self.disable_intent("PreviousEPICIntent")

        self.display_service = DisplayService(self.emitter)

    def handle_website_epic_intent(self, message):
        webbrowser.open("http://epic.gsfc.nasa.gov/")

    def handle_about_epic_intent(self, message):
        self.speak_dialog("aboutEPIC")

    def handle_epic_intent(self, message):
        self.current = self.lenght - 1
        self.EPIC(self.current, message.data["utterance"])

    def get_EPIC(self):
        url = "https://epic.gsfc.nasa.gov/api/natural"
        self.response = unirest.get(url)
        self.lenght = len(self.response.body)

    def EPIC(self, count=0, utterance = ""):
        url = "https://epic.gsfc.nasa.gov/epic-archive/jpg/" + self.response.body[count]["image"] + ".jpg"
        date = self.response.body[count]["date"]
        img = urllib2.Request(url)
        raw_img = urllib2.urlopen(img).read()
        save_path = self.save_path + "/" + date + ".jpg"
        f = open(save_path, 'wb')
        f.write(raw_img)
        f.close()
        self.speak_dialog("EPIC", {"date": date})
        self.display_service.display(save_path, utterance)

    def stop(self):
        pass


def create_skill():
    return EPICSkill()
