from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.skills.displayservice import DisplayService

import unirest
import urllib2
import os
from os.path import dirname
import webbrowser

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class EPICSkill(MycroftSkill):

    def __init__(self):
        super(EPICSkill, self).__init__(name="EPICSkill")
        self.save = True
        self.save_path = os.path.dirname(__file__) + "/epic"

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.reload_skill = False
        self.get_EPIC()

    def initialize(self):
        epic_intent = IntentBuilder("EPICIntent").\
                require("EPICKeyword").build()

        self.register_intent(epic_intent, self.handle_epic_intent)

        about_epic_intent = IntentBuilder("AboutEPICIntent"). \
            require("aboutEPICKeyword").build()

        self.register_intent(about_epic_intent, self.handle_about_epic_intent)

        website_epic_intent = IntentBuilder("WebsiteEPICIntent"). \
            require("websiteEPICKeyword").require("EPICKeyword").build()

        self.register_intent(website_epic_intent, self.handle_website_epic_intent)

        self.disable_intent("PreviousEPICIntent")

        self.display_service = DisplayService(self.emitter, self.name)

    def handle_website_epic_intent(self, message):
        webbrowser.open("http://epic.gsfc.nasa.gov/")

    def handle_about_epic_intent(self, message):
        self.display_service.display([dirname(__file__)+"/epic.jpg"],
                                     utterance=message.data.get("utterance"))
        self.speak_dialog("aboutEPIC")

    def handle_epic_intent(self, message):
        self.EPIC(message.data.get("utterance"))

    def get_EPIC(self):
        url = "https://epic.gsfc.nasa.gov/api/natural"
        self.response = unirest.get(url)

    def EPIC(self, utterance = ""):
        date = self.response.body[-1]["date"]
        url = "https://epic.gsfc.nasa.gov/epic-archive/jpg/" + \
              self.response.body[-1]["image"] + ".jpg"
        img = urllib2.Request(url)
        raw_img = urllib2.urlopen(img).read()
        save_path = self.save_path + "/" + date + ".jpg"
        f = open(save_path, 'wb')
        f.write(raw_img)
        f.close()
        # TODO format date for decent speech
        self.speak_dialog("EPIC", {"date": date})
        self.display_service.display([save_path], utterance=utterance)
        for num in range(1, len(self.response.body)):
            num = len(self.response.body) - num
            url = "https://epic.gsfc.nasa.gov/epic-archive/jpg/" + self.response.body[num]["image"] + ".jpg"
            img = urllib2.Request(url)
            raw_img = urllib2.urlopen(img).read()
            date = self.response.body[num]["date"]
            save_path = self.save_path + "/" + date + ".jpg"
            f = open(save_path, 'wb')
            f.write(raw_img)
            f.close()
            self.display_service.add_pictures([save_path], utterance=utterance)

    def stop(self):
        pass


def create_skill():
    return EPICSkill()
