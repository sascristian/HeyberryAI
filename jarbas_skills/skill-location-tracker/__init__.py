# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message
from threading import Timer
import unirest
from mycroft.util import connected

__author__ = 'jarbas'

LOGGER = getLogger(__name__)

# TODO make configurable to get location from other sources (GPS)


class LocationTrackerSkill(MycroftSkill):
    def __init__(self):
        super(LocationTrackerSkill, self).__init__()
        self.minutes = 15
        self.source = "ip"
        self.timer = Timer(60 * self.minutes, self.get_location)
        self.timer.setDaemon(True)

    def initialize(self):
        intent = IntentBuilder("UpdateLocationIntent") \
            .require("UpdateKeyword").require(
            "LocationKeyword").optionally("ConfigKeyword").build()
        self.register_intent(intent, self.handle_update_intent)

        intent = IntentBuilder("CurrentLocationIntent") \
            .require("CurrentKeyword").require(
            "LocationKeyword").build()
        self.register_intent(intent, self.handle_current_location_intent)

        intent = IntentBuilder("CurrentLocationIntent") \
            .require("WhereAmIKeyword").build()
        self.register_intent(intent, self.handle_current_location_intent)

        self.timer.start()

    def handle_current_location_intent(self, message):
        ip = message.context.get("ip")
        destinatary = message.context.get("destinatary")
        if "fbchat" in destinatary:
            # TODO check profile page
            self.speak("I don't know you location and i won't check your "
                       "profile for it")
            return
        if ip:
            config = self.from_ip(update=False)
            if config != {}:
                city = config.get("location", {}).get("city", {}).get("name","unknown city")
                country = config.get("location", {}).get("city", {}).get(
                    "region").get("country").get("name", "unknow country")
                self.speak(
                    "your ip adress says you are in " + city + " in " +
                    country)
        elif ":" in destinatary:
            sock = destinatary.split(":")[0]
            # TODO user from sock
            self.speak("ask me later")
            return
        else:
            config = self.config_core.get("location")
            city = config.get("city", {}).get("name","unknown city")
            country = config.get("city", {}).get( "region").get("country").get("name", "unknow country")
            self.speak("your configuration says you are in " + city + " in " +
                       country)

    def handle_update_intent(self, message):
        if connected():
            self.speak("updating location from ip address")
            self.get_location("ip")
        else:
            self.speak("Cant do that offline")

    def from_ip(self, update = True):
        self.log.info("Retrieving location data from ip adress")
        if connected():
            response = unirest.get("https://ipapi.co/json/")
            city = response.body.get("city")
            region_code = response.body.get("region_code")
            country = response.body.get("country")
            country_name = response.body.get("country_name")
            region = response.body.get("region")
            lon = response.body.get("longitude")
            lat = response.body.get("latitude")
            timezone = response.body.get("timezone")

            region_data = {"code": region_code, "name": region, "country": {
                "code": country, "name": country_name}}
            city_data = {"code": city, "name": city, "state": region_data,
                         "region": region_data}
            timezone_data = {"code": timezone, "name": timezone,
                             "dstOffset": 3600000,
                             "offset": -21600000}
            coordinate_data = {"latitude": float(lat), "longitude": float(lon)}
            location_data = {"city": city_data, "coordinate": coordinate_data,
                             "timezone": timezone_data}
            config = {"location": location_data}
            if update:
                self.config_update(config)
            return config
        else:
            self.log.warning("No internet connection, could not update "
                             "location from ip adress")
            return {}

    def get_location(self, source=None):
        if source is None:
            source = self.source
        if source == "ip":
            self.from_ip()
        else:
            self.log.info("Failed to retrieve location data from " + source)
        return


def create_skill():
    return LocationTrackerSkill()
