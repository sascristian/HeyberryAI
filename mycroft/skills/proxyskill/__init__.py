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

from os.path import dirname
import os
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import grey_harvest
from string import capwords
from time import gmtime, strftime

__author__ = 'jarbas'

logger = getLogger(__name__)


class ProxySkill(MycroftSkill):

    def __init__(self):
        super(ProxySkill, self).__init__(name="ProxySkill")

        self.path =  os.path.dirname(__file__) + "/harvest"
        self.limit = 50

    def initialize(self):
        self.load_data_files(dirname(__file__))

        prefixes = [
            'proxy from', 'proxy form' ]
        self.__register_prefixed_regex(prefixes, "(?P<Country>.*)")

        proxyfrom_intent = IntentBuilder("ProxyfromIntent").require("Country").build()
        self.register_intent(proxyfrom_intent, self.handle_proxyfrom_intent)

        proxy_intent = IntentBuilder("ProxyIntent"). \
            require("proxy").build()
        self.register_intent(proxy_intent, self.handle_proxy_intent)

        single_proxy_intent = IntentBuilder("SingleProxyIntent"). \
            require("singleproxy").build()
        self.register_intent(single_proxy_intent, self.handle_single_proxy_intent)

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    def handle_proxy_intent(self, message):
        self.speak_dialog("proxy")
        path = self.harvestproxy()
        self.speak("proxies sucefully harvested and saved at "+path)


    def handle_single_proxy_intent(self, message):

        proxy , c = self.harvestsingleproxy()
        txt = "here is a proxy from "+c+" : " + proxy
        self.speak(txt)

    def handle_proxyfrom_intent(self, message):
        country = message.data.get("Country")
        country = capwords(country)
        print country
        ######
        proxy , c = self.harvestsingleproxy(country)
        txt = "proxy from " + country + " " + proxy
        if len(proxy) < 13:
            proxy , c = self.harvestsingleproxy()
            txt = "proxy from " + country + " wasn't found maybe this one from " + c +" serves your purpose anyway  " + proxy
        self.speak(txt)

    def harvestsingleproxy(self, country="any"):

        proxies = []
        ''' spawn a harvester '''
        if country == "any":
            harvester = grey_harvest.GreyHarvester(
                #https_only=True,
                #allowed_countries=[country],
                denied_countries=['China', 'Hong Kong'],
                # ports=['ports'],
                max_timeout=20  # errors on small numbers, if connection is good can be as low as 1
            )
        else:
            harvester = grey_harvest.GreyHarvester(
                #https_only=True,
                allowed_countries=[country],
                denied_countries=[],
                # ports=['ports'],
                max_timeout=20  # errors on small numbers, if connection is good can be as low as 1
            )
        ''' harvest some proxies from teh interwebz '''
        p = ""
        c = ""
        count = 0
        for proxy in harvester.run():
            print "harvesting proxy number: " + str(count + 1)
            p = str(proxy)
            c = proxy['country']
            break

        return p , c

    def harvestproxy(self):
        proxies = []
        ''' spawn a harvester '''
        harvester = grey_harvest.GreyHarvester(
            https_only=True,
            # allowed_countries=["France"],
            denied_countries=['China', 'Hong Kong'],
            # ports=['ports'],
            max_timeout=20 #errors on small numbers, if connection is good can be as low as 1
        )
        ''' harvest some proxies from teh interwebz '''

        count = 0
        for proxy in harvester.run():
            print "harvesting proxy number: " + str(count+1)
            try:
                proxies.append(proxy)
                if count >= self.limit:
                    break
            except:
                print "error harvesting proxy number " + str(count+1)
            count +=1

        '''save to file'''
        timestamp = strftime("%d, %b, %Y, %H, %M, %S", gmtime())
        path = self.path+"/proxies " + timestamp + ".txt"
        wfile = open(path, "w")
        for proxy in proxies:
            wfile.write(str(proxy) + "\n")
        wfile.close()
        return path

    def stop(self):
        pass


def create_skill():
    return ProxySkill()
