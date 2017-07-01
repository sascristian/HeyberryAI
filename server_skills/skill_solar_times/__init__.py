from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import arrow
import tzlocal

from solartime import SolarTime

__author__ = 'msev'

LOGGER = getLogger(__name__)
# TODO make origin configurable
from geopy.geocoders import Nominatim

class SunSkill(MycroftSkill):
    def __init__(self):
        super(SunSkill, self).__init__(name="SunSkill")

    def initialize(self):
        #self.load_data_files(dirname(__file__))
        sunrise_intent = IntentBuilder("SunRiseIntent"). \
            require("SunRiseKeyword").build()
        sunset_intent = IntentBuilder("SunSetIntent"). \
            require("SunSetKeyword").build()
        dawn_intent = IntentBuilder("DawnIntent"). \
            require("DawnKeyword").build()
        dusk_intent = IntentBuilder("DuskIntent"). \
            require("DuskKeyword").build()
        noon_intent = IntentBuilder("SolarNoonIntent"). \
            require("NoonKeyword").build()

        self.register_intent(sunrise_intent, self.handle_sunrise_intent)
        self.register_intent(sunset_intent, self.handle_sunset_intent)
        self.register_intent(dawn_intent, self.handle_dawn_intent)
        self.register_intent(dusk_intent, self.handle_dusk_intent)
        self.register_intent(noon_intent, self.handle_noon_intent)

        today = arrow.now().date()
        self.localtz = tzlocal.get_localzone()
        
        city = self.config_core.get("location")
        if isinstance(city, str): # city is city name
            geolocator = Nominatim()
            location = geolocator.geocode(city)
            lat = location.latitude
            lon = location.longitude
        else: # city is a dict of location information
            lat = city['coordinate']['latitude']
            lon = city['coordinate']['longitude']

        sun = SolarTime()
        self.schedule = sun.sun_utc(today, lat, lon)

    def handle_sunrise_intent(self, message):
        sunrise = self.schedule['sunrise'].astimezone(self.localtz)
        self.speak_dialog("sunrise", {"sunrise": str(sunrise)[10:16]})


    def handle_sunset_intent(self, message):
        sunset = self.schedule['sunset'].astimezone(self.localtz)
        self.speak_dialog("sunset", {"sunset": str(sunset)[10:16]})

    def handle_dawn_intent(self, message):
        dawn = self.schedule['dawn'].astimezone(self.localtz)
        self.speak_dialog("dawn", {"dawn": str(dawn)[10:16]})

    def handle_dusk_intent(self, message):
        dusk = self.schedule['dusk'].astimezone(self.localtz)
        self.speak_dialog("dusk", {"dusk": str(dusk)[10:16]})

    def handle_noon_intent(self, message):
        noon = self.schedule['noon'].astimezone(self.localtz)
        self.speak_dialog("noon", {"noon": str(noon)[10:16]})

    def stop(self):
        pass


def create_skill():
    return SunSkill()
