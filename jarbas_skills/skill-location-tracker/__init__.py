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
from threading import Timer
import unirest
from mycroft.util import connected
#from wifi import Cell
#import requests
#import json
#import decimal
#from geopy.geocoders import Nominatim

__author__ = 'jarbas'

LOGGER = getLogger(__name__)

# TODO make configurable to get location from other sources (GPS)


class LocationTrackerSkill(MycroftSkill):
    def __init__(self):
        super(LocationTrackerSkill, self).__init__()
        self.config = self.config_core.get("location")
        self.minutes = self.config.get("update_mins", 15)
        # TODO list with prefered order ["wifi", "gps", "ip"]
        self.source = self.config.get("update_source", "ip")
        self.active = self.config.get("tracking", True)
        self.auto_context = self.config.get("auto_context", True)
        self.active = True
        self.timer = Timer(60 * self.minutes, self.get_location)
        self.timer.setDaemon(True)

        # wifi geolocate
        self.geolocateApiKey = ""
        self.googlemapsApiKey = ""

    def initialize(self):
        intent = IntentBuilder("UpdateLocationIntent") \
            .require("UpdateKeyword").require(
            "LocationKeyword").optionally("ConfigKeyword").build()
        self.register_intent(intent, self.handle_update_intent)

        intent = IntentBuilder("CurrentLocationIntent") \
            .require("CurrentKeyword").require("LocationKeyword").build()
        self.register_intent(intent, self.handle_current_location_intent)

        intent = IntentBuilder("UnSetLocationTrackingIntent") \
            .require("TrackingKeyword").require("LocationKeyword").require(
            "DeactivateKeyword").build()
        self.register_intent(intent, self.handle_deactivate_tracking_intent)

        intent = IntentBuilder("SetLocationTrackingIntent") \
            .require("TrackingKeyword").require("LocationKeyword").require(
            "ActivateKeyword").build()
        self.register_intent(intent, self.handle_activate_tracking_intent)

        intent = IntentBuilder("WhereAmIIntent") \
            .require("WhereAmIKeyword").build()
        self.register_intent(intent, self.handle_where_am_i_intent)

        intent = IntentBuilder("SetLocationContextIntent") \
            .require("InjectionKeyword").require(
            "LocationKeyword").require(
            "ActivateKeyword").build()
        self.register_intent(intent, self.handle_activate_context_intent)

        intent = IntentBuilder("UnsetLocationContextIntent") \
            .require("InjectionKeyword").require(
            "LocationKeyword").require(
            "DeactivateKeyword").build()
        self.register_intent(intent, self.handle_deactivate_context_intent)

        if self.active:
            self.timer.start()

    def handle_deactivate_context_intent(self, message):
        if not self.auto_context:
            self.speak("Location context injection is not active")
        else:
            self.auto_context = False
            self.speak("Location context injection deactivated")

    def handle_activate_context_intent(self, message):
        if self.auto_context:
            self.speak("Location context injection is already active")
        else:
            self.auto_context = True
            self.speak("Location context injection activated")

    def handle_deactivate_tracking_intent(self, message):
        if not self.active:
            self.speak("Location tracking from " + self.source + " is not active")
        else:
            self.active = False
            self.timer.cancel()
            self.speak("Location tracking from " + self.source + " deactivated")

    def handle_activate_tracking_intent(self, message):
        if self.active:
            self.speak("Location tracking from " + self.source + " is active")
        else:
            self.active = True
            self.timer.start()
            self.speak("Location tracking from " + self.source + " activated")

    def handle_current_location_intent(self, message):
        config = self.config_core.get("location")
        city = config.get("city", {}).get("name", "unknown city")
        country = config.get("city", {}).get("region").get("country").get(
            "name", "unknown country")
        self.speak("configuration location is " + city + ", " +
                   country)
        if self.auto_context:
            self.set_context('Location', city + ', ' + country)

    def handle_where_am_i_intent(self, message):
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
                    "region").get("country").get("name", "unknown country")
                self.speak(
                    "your ip adress says you are in " + city + " in " +
                    country)
        elif ":" in destinatary:
            sock = destinatary.split(":")[0]
            # TODO user from sock
            self.speak("ask me later")
            return
        else:
            config = self.get_location()
            if config != {}:
                city = config.get("location", {}).get("city", {}).get("name",
                                                                      "unknown city")
                country = config.get("location", {}).get("city", {}).get(
                    "region").get("country").get("name", "unknown country")
                self.speak(
                    "your ip adress says you are in " + city + " in " +
                    country)

    def handle_update_intent(self, message):
        if connected():
            self.speak("updating location from ip address")
            config = self.get_location("ip")
            city = config.get("city", {}).get("name", "unknown city")
            country = config.get("city", {}).get("region").get("country").get(
                "name", "unknow country")
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
                try:
                    # jarbas core skill function
                    self.config_update(config)
                except:
                    pass
            return config
        else:
            self.log.warning("No internet connection, could not update "
                             "location from ip adress")
            return {}

    def get_location(self, source=None):
        if source is None:
            source = self.source
        if source == "ip":
            config = self.from_ip()
            if config != {}:
                city = config.get("location", {}).get("city", {}).get("name",
                                                                      "unknown city")
                country = config.get("location", {}).get("city", {}).get(
                    "region").get("country").get("name", "unknown country")
                if self.auto_context:
                    self.set_context('Location', city + ', ' + country)
        else:
            self.log.info("Failed to retrieve location data from " + source)
            config = {}
        return config

    # TODO finish this

    def from_wifi(self, update=True):
        self.log.info("Retrieving location data from available wifi")
        if connected():
            url = "https://www.googleapis.com/geolocation/v1/geolocate" \
                       "?key=" + self.geolocateApiKey
            # TODO this only supports connected to networks, change
            available = Cell.all('wlan0')
            mac = []
            signal = []
            channel = []
            for wifi in available:
                channel.append(wifi.channel)
                mac.append(wifi.address)
                signal.append(wifi.signal)
            payload, headers = self.build_wifi_JSON(mac, signal, channel)

            try:
                response = requests.post(url,
                                              data=json.dumps(payload),
                                              headers=headers)
                text = json.loads(response.text)

                if response.ok == False:  # Check if the response was ok
                    if text['error']['errors'][0]['reason'] == 'dailyLimitExceeded':
                        self.log.error('You have exceeded you daily limit')
                    elif text['error']['errors'][0]['reason'] == 'keyInvalid':
                        self.log.error('Your API key is not valid for the '
                                       'Google Maps Geolocation API')
                    elif text['error']['errors'][0]['reason'] == 'userRateLimitExceeded':
                        self.log.error('You\'ve exceeded the requests per '
                                       'second per user limit that you configured in the Google Developers Console')
                    elif text['error']['errors'][0]['reason'] == 'notFound':
                        self.log.error('The request was valid, but no results were returned')
                    elif text['error']['errors'][0]['reason'] == 'parseError':
                        self.log.error('The request body is not valid JSON')
                    else:
                        self.log.error('Unknown error in the geolocation '
                                       'response. Might be caught in an exception.')
            except Exception, e:
                self.log.error( str(e))
                return

            decimal.getcontext().prec = 15  # Setting precision for lat/lng response
            lng = decimal.Decimal(text['location']['lng']) + 0
            lat = decimal.Decimal(text['location']['lat']) + 0
            accuracy = response['accuracy']
            geolocator = Nominatim()
            location = geolocator.reverse(str(lat) + ", " + str(lng))
            adress = location.adress
            # TODO config update and return

    def build_wifi_JSON(self, bssids, rssi, channel, considerIP='true'):

        headers = {'content-type': 'application/json'}
        payload = {}

        if len(bssids) < 3:
            self.log.warning('Atleast two BSSIDs are required for wifi '
                             'geolocation')
            self.log.debug('Current number of bssids: %i' % len(bssids))
            return payload, headers

        # Building payload as per google-guidelines
        payload['considerIp'] = considerIP
        payload['wifiAccessPoints'] = []
        for i in range(0,len(bssids)):
            payload["wifiAccessPoints"].append({})
            payload['wifiAccessPoints'][i]['macAddress'] = bssids[i]
            payload['wifiAccessPoints'][i]['signalStrength'] = rssi[i]
            payload['wifiAccessPoints'][i]['channel'] = channel[i]

        # Payload structure reference: https://developers.google.com/maps/documentation/geolocation/intro#body
        return payload, headers


def create_skill():
    return LocationTrackerSkill()
