from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import random

import requests
from bs4 import BeautifulSoup
import sys

__author__ = 'jarbas'

LOGGER = getLogger(__name__)

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
        #self.load_data_files(dirname(__file__))

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
        self.add_result("pickup_line_type", type)
        return self.pickupliner.get_line(type)

    def handle_line_intent(self, message):
        line = self.get_pickup("random")
        self.speak(line)
        self.add_result("pickup_line",line)
        self.emit_results()

    def handle_geek_line_intent(self, message):
        line = self.get_pickup("computer")
        self.speak(line)
        self.add_result("pickup_line", line)
        self.emit_results()

    def handle_dirty_line_intent(self, message):
        line = self.get_pickup("crude")
        self.speak(line)
        self.add_result("pickup_line", line)
        self.emit_results()

    def handle_math_line_intent(self, message):
        line = self.get_pickup("math")
        self.speak(line)
        self.add_result("pickup_line", line)
        self.emit_results()

    def handle_physics_line_intent(self, message):
        line = self.get_pickup("physics")
        self.speak(line)
        self.add_result("pickup_line", line)
        self.emit_results()

    def handle_scifi_line_intent(self, message):
        line = self.get_pickup("scifi")
        self.speak(line)
        self.add_result("pickup_line", line)
        self.emit_results()

### todo results and vocab for these
    def handle_cheesy_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="cheesy"))
        self.emit_results()

    def handle_women_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="women"))
        self.emit_results()

    def handle_harrypotter_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="harrypotter"))
        self.emit_results()

    def handle_biochem_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="biochem"))
        self.emit_results()

    def handle_music_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="musician"))
        self.emit_results()

    def handle_disney_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="disney"))
        self.emit_results()

    def handle_vegan_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="vegan"))
        self.emit_results()

    def handle_tinder_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="tinder"))
        self.emit_results()

    def handle_warcraft_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="warcraft"))
        self.emit_results()

    def handle_pokemon_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="pokemon"))
        self.emit_results()

    def handle_indian_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="desi"))
        self.emit_results()

    def handle_astronomy_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="astronomy"))
        self.emit_results()

    def handle_redneck_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="redneck"))
        self.emit_results()

    def handle_food_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="food"))
        self.emit_results()

    def handle_engineering_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="engineering"))
        self.emit_results()

    def handle_gameofthrones_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="gameofthrones"))
        self.emit_results()

    def handle_lotr_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="lotr"))
        self.emit_results()

    def handle_hungergames_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="hungergames"))
        self.emit_results()

    def handle_twilight_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="twilight"))
        self.emit_results()

    def handle_doctorwho_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="doctorwho"))
        self.emit_results()

    def handle_breakingbad_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="breakingbad"))
        self.emit_results()

    def handle_medieval_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="medieval"))
        self.emit_results()

    def handle_dog_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="dog"))
        self.emit_results()

    def handle_pirate_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="pirate"))
        self.emit_results()

    def handle_nye_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="nye"))
        self.emit_results()

    def handle_independence_line_intent(self, message):
        self.speak(self.pickupliner.get_line(type="independence"))
        self.emit_results()

    def stop(self):
        pass


def create_skill():
    return PickupLineSkill()

