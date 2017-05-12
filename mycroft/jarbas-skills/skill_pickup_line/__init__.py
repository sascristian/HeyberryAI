from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message
import random

import requests
from bs4 import BeautifulSoup
import sys

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class FbPost():
    def __init__(self, emitter):
        self.emitter = emitter

    def post_text(self, text, id="me", speech= "Making a post on face book", link= None):
        self.emitter.emit(Message("fb_post_request", {"type":"text", "id":id, "link":link, "text":text, "speech":speech}))

    def post_link(self, link,  text="", id="me", speech= "Sharing a link on face book"):
        self.emitter.emit(Message("fb_post_request", {"type":"link", "id":id, "link":link, "text":text, "speech":speech}))


def get_soup(url):
    try:
        return BeautifulSoup(requests.get(url).text,"html.parser")
    except Exception as SockException:
        print SockException
        sys.exit(1)


class PickupLine(object):
    def get_line(self, type="random"):

        if type=="random":
            self.url = "http://www.pickuplinegen.com/"
        else:
            self.url = "http://www.pickuplinesgalore.com/"
            self.url+=type+".html"


        if type=="random":
            return get_soup(self.url).select("body > section > div#content")[0].text.strip(" ")
        else:
            soup = get_soup(self.url)
            lines = "".join([i.text for i in soup.select("main > p.action-paragraph.paragraph > span.paragraph-text-7")]).split("\n\n")
            return random.choice(lines)


class PickupLineSkill(MycroftSkill):
    def __init__(self):
        super(PickupLineSkill, self).__init__(name="PickupLineSkill")
        self.pickupliner = PickupLine()

    def initialize(self):
        self.poster = FbPost(self.emitter)

        fb_intent = IntentBuilder("FbPickupLinePostIntent") \
            .require("fblineKeyword").build()

        self.register_intent(fb_intent,
                             self.handle_fb)

        line_intent = IntentBuilder("PKlineIntent"). \
            require("lineKeyword").build()

        self.register_intent(line_intent, self.handle_line_intent)

        geek_line_intent = IntentBuilder("GeekPKlineIntent"). \
            require("geeklineKeyword").build()

        self.register_intent(geek_line_intent, self.handle_geek_line_intent)

        dirty_line_intent = IntentBuilder("dirtyPKlineIntent"). \
            require("dirtylineKeyword").build()

        self.register_intent(dirty_line_intent, self.handle_dirty_line_intent)

        math_line_intent = IntentBuilder("mathPKlineIntent"). \
            require("mathlineKeyword").build()

        self.register_intent(math_line_intent, self.handle_math_line_intent)

        physics_line_intent = IntentBuilder("physicsPKlineIntent"). \
            require("physicslineKeyword").build()

        self.register_intent(physics_line_intent, self.handle_physics_line_intent)

        scifi_line_intent = IntentBuilder("scifiPKlineIntent"). \
            require("scifilineKeyword").build()

        self.register_intent(scifi_line_intent, self.handle_scifi_line_intent)

    def get_pickup(self, type = "random"):
        return self.pickupliner.get_line(type)

    def handle_fb(self, message):
        line = self.get_pickup("random")
        self.poster.post_text(line, speech="Posting a Pick up Line in Face book")

    def handle_line_intent(self, message):
        line = self.get_pickup("random")
        self.speak(line)

    def handle_geek_line_intent(self, message):
        line = self.get_pickup("computer")
        self.speak(line)

    def handle_dirty_line_intent(self, message):
        line = self.get_pickup("crude")
        self.speak(line)

    def handle_math_line_intent(self, message):
        line = self.get_pickup("math")
        self.speak(line)

    def handle_physics_line_intent(self, message):
        line = self.get_pickup("physics")
        self.speak(line)

    def handle_scifi_line_intent(self, message):
        line = self.get_pickup("scifi")
        self.speak(line)

### todo results and vocab for these
    def handle_cheesy_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="cheesy"))

    def handle_women_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="women"))

    def handle_harrypotter_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="harrypotter"))

    def handle_biochem_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="biochem"))

    def handle_music_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="musician"))

    def handle_disney_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="disney"))

    def handle_vegan_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="vegan"))

    def handle_tinder_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="tinder"))

    def handle_warcraft_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="warcraft"))

    def handle_pokemon_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="pokemon"))

    def handle_indian_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="desi"))

    def handle_astronomy_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="astronomy"))

    def handle_redneck_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="redneck"))

    def handle_food_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="food"))

    def handle_engineering_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="engineering"))

    def handle_gameofthrones_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="gameofthrones"))

    def handle_lotr_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="lotr"))

    def handle_hungergames_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="hungergames"))

    def handle_twilight_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="twilight"))

    def handle_doctorwho_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="doctorwho"))

    def handle_breakingbad_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="breakingbad"))

    def handle_medieval_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="medieval"))

    def handle_dog_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="dog"))

    def handle_pirate_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="pirate"))

    def handle_nye_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="nye"))

    def handle_independence_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="independence"))

    def stop(self):
        pass


def create_skill():
    return PickupLineSkill()

