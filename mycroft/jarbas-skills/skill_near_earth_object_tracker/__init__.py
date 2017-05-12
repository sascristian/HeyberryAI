from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import unirest
import os
import time
import webbrowser

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class NEOSkill(MycroftSkill):

    def __init__(self):
        super(NEOSkill, self).__init__(name="NEOSkill")
        try:
            self.key = self.config_apis["NASAAPI"]
        except:
            try:
                self.key = self.config["NASAAPI"]
            except:
                self.key = "DEMO_KEY"

        self.save = True
        try:
            self.save_path = self.config_core["database_path"] + "/neos"
        except:
            try:
                self.save_path = self.config["save_path"]
            except:
                self.save_path = os.path.dirname(__file__) + "/neos"

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        ### near_earth_objects_tracker data
        self.neos = []
        self.neo_num = 0
        self.current_neo = 0

        self.reload_skill = False

    def initialize(self):
        neo_intent = IntentBuilder("NeoIntent").\
                require("NEOKeyword").build()

        self.register_intent(neo_intent, self.handle_nearest_neo_intent)

        neo_num_intent = IntentBuilder("NeoNumIntent"). \
            require("NEOnumKeyword").build()

        self.register_intent(neo_num_intent, self.handle_neo_num_intent)

        next_neo_intent = IntentBuilder("NextNeoIntent"). \
            require("nextNEOKeyword").build()

        self.register_intent(next_neo_intent, self.handle_next_neo_intent)

        neo_page_intent = IntentBuilder("NeoPageIntent"). \
            require("NEOpageKeyword").build()

        self.register_intent(neo_page_intent, self.handle_neo_page_intent)

        try:
            self.disable_intent("NeoPageIntent")
            self.disable_intent("NextNeoIntent")
        except:
            pass

    def handle_neo_num_intent(self, message):
       self.get_neo_info()
       self.speak_dialog("neo_num", {"neo_num":self.neo_num})

    def handle_nearest_neo_intent(self, message):
        self.current_neo = 0
        self.get_neo_info()
        self.speak_dialog("nearest_neo",
                          {"name":self.neos[0]["name"],\
                           "velocity":self.neos[0]["velocity"],\
                           "distance":self.neos[0]["miss_d"],\
                           "min_d":self.neos[0]["min_d"],\
                           "max_d":self.neos[0]["max_d"],\
                           "date":self.neos[0]["ap_date"]})
        hazard = "not"
        if self.neos[0]["hazard"]:
            hazard = ""
        self.speak_dialog("hazard", {"name":self.neos[0]["name"], "hazard":hazard})

        try:
            self.enable_intent("NeoPageIntent")
            self.enable_intent("NextNeoIntent")
        except:
            pass

    def handle_neo_page_intent(self, message):
        self.speak_dialog("neo_page")
        webbrowser.open(self.neos[self.current_neo]["nasa_url"])

    def handle_next_neo_intent(self, message):
        self.current_neo += 1
        if self.current_neo > self.neo_num:
            self.speak("going back to first near_earth_objects_tracker")
            self.current_neo = 0

        self.speak_dialog("next_neo", {"name": self.neos[self.current_neo]["name"],
                                          "velocity": self.neos[self.current_neo]["velocity"],
                                          "distance": self.neos[self.current_neo]["miss_d"],
                                          "min_d": self.neos[self.current_neo]["min_d"],
                                          "max_d": self.neos[self.current_neo]["max_d"],
                                          "date": self.neos[self.current_neo]["ap_date"]})
        hazard = "not"
        if self.neos[self.current_neo]["hazard"]:
            hazard = ""
        self.speak_dialog("hazard", {"name": self.neos[self.current_neo]["name"], "hazard": hazard})
        try:
            self.enable_intent("NeoPageIntent")
            self.enable_intent("NextNeoIntent")
        except:
            pass

    def get_neo_info(self):
        start_date = time.strftime("%Y-%m-%d", time.gmtime())
        neo_url = "https://api.nasa.gov/neo/rest/v1/feed?start_date=" + start_date + "&api_key=" + self.key

        response = unirest.get(neo_url)
        self.neos = []
        print response.body
        neos = response.body["near_earth_objects"]
        self.neo_num = len(neos)
        for date in neos:
            neo = neos[date][0]
            name = [neo][0]["name"].replace("(", "").replace(")", "")
            id = str(neo["neo_reference_id"])
            nasa_url = neo["nasa_jpl_url"]
            abs_mag = str(neo["absolute_magnitude_h"])
            max_d = str(neo["estimated_diameter"]["meters"]["estimated_diameter_max"])
            min_d = str(neo["estimated_diameter"]["meters"]["estimated_diameter_min"])
            miss_d = str(neo["close_approach_data"][0]["miss_distance"]["kilometers"])
            ap_date = neo["close_approach_data"][0]["close_approach_date"]
            velocity = str(neo["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"])
            hazard = neo["is_potentially_hazardous_asteroid"]
            neo = {"name":name, "id":id, "abs_mag":abs_mag, "max_d":max_d, "min_d":min_d, "miss_d":miss_d,
                   "ap_date":ap_date, "velocity":velocity, "hazard":hazard, "nasa_url":nasa_url}
            if self.save:
                save_path = self.save_path + "/" + name + ".txt"
                # save neo data
                f = open(save_path, 'wb')
                for key in neo:
                    f.write(key + " : " + str(neo[key]) + "\n")
                f.close()
            self.neos.append(neo)

    def converse(self, transcript, lang="en-us"):
        if "page" not in transcript[0]:
            try:
                self.disable_intent("NeoPageIntent")
            except:
                pass
        return False

    def stop(self):
        pass


def create_skill():
    return NEOSkill()
