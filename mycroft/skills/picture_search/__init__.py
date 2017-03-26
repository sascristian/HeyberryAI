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

import random
from bs4 import BeautifulSoup
import urllib2
import os
import json
import cloudsight
import time

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.skills.displayservice import DisplayService

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class PictureSkill(MycroftSkill):

    def __init__(self):
        super(PictureSkill, self).__init__(name="PictureSkill")
        apikey = self.config_apis["CloudsightAPI"]
        apisecret = self.config_apis["CloudsightSecret"]
        auth = cloudsight.OAuth(apikey, apisecret)
        self.api = cloudsight.API(auth)
        self.save_path = self.config_core["database_path"] + "/pictures"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def initialize(self):
        #self.load_data_files(dirname(__file__))

        prefixes = [
            'search picture of', 'show picture of', 'picture of', 'picture search ', 'ps']
        self.__register_prefixed_regex(prefixes, "(?P<Search>.*)")

        picsearch_intent = IntentBuilder("PicturenSearchItent"). \
            require("Search").build()
        self.register_intent(picsearch_intent, self.handle_search_picture_intent)

        picture_intent = IntentBuilder("Picturentent").\
            require("pic").build()
        self.register_intent(picture_intent, self.handle_picture_intent)

        pictureiden_intent = IntentBuilder("PictureIDintent"). \
            require("idet").build()
        self.register_intent(pictureiden_intent, self.handle_identify_picture_intent)

        self.display_service = DisplayService(self.emitter)

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    def handle_identify_picture_intent(self, message):
        path = os.path.dirname(__file__) + '/sources.txt'
        with open(path) as f:
            urls = f.readlines()
        sucess = False
        while not sucess:
            try:
                image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
                chosenurl = random.choice(image_urls.split('\n'))
                label = self.identifypicture(chosenurl)
                LOGGER.info(chosenurl)
                # save pic
                img = urllib2.Request(chosenurl)
                raw_img = urllib2.urlopen(img).read()
                save_path = self.save_path + "/random/" + time.asctime() + ".jpg"
                f = open(save_path, 'wb')
                f.write(raw_img)
                f.close()
                sucess = True
                self.display_service.show(save_path, message.data["utterance"])
                self.speak_dialog("iden")
                self.speak(label)

            except Exception as e:
                LOGGER.error(str(e))

    def identifypicture(self, picture):
        url = picture
        #response = self.api.remote_image_request(url, {'image_request[locale]': 'en-US', })
        with open(picture, 'rb') as f:
            response = self.api.image_request(f, picture, {
                'image_request[locale]': 'en-US',
            })
        status = self.api.wait(response['token'], timeout=30)
        return status['name']

    def handle_picture_intent(self, message):
        self.speak_dialog("pic")
        path = os.path.dirname(__file__) + '/sources.txt'
        with open(path) as f:
            urls = f.readlines()
        sucess = False
        while not sucess:
            try:
                image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
                chosenurl = random.choice(image_urls.split('\n'))
                LOGGER.info(chosenurl)
                # save pic
                img = urllib2.Request(chosenurl)
                raw_img = urllib2.urlopen(img).read()
                save_path = self.save_path + "/random/" + time.asctime() + ".jpg"
                f = open(save_path, 'wb')
                f.write(raw_img)
                f.close()
                sucess = True
                self.display_service.show(save_path, message.data["utterance"])

            except Exception as e:
                LOGGER.error(str(e))

    def handle_search_picture_intent(self,message):
        #search = "anal porn lesbian"
        search = message.data.get("Search")
        self.add_result("Search", search)
        self.speak("please wait while i search google pictures for "+ search)
        DIR = self.save_path + "/search"
        self.searchanddl(search, DIR)
        pics = []
        search = search.replace(' ', '+')
        path = DIR + "/"+search
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                pics.append(os.path.join(path, f))
        pic = random.choice(pics)
        self.display_service.show(pic, message.data["utterance"])
        self.speak("heres your picture")

    def get_soup(self, url, header):
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')

    def searchanddl(self, searchkey, DIR, dlnum=3):
        query = searchkey  # raw_input("query image")# you can change the query for the image  here
        image_type = "ActiOn"
        query = query.split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
        print url
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
            }
        soup = self.get_soup(url, header)
        i=0
        ActualImages = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            ActualImages.append((link, Type))
            i+=1
            if i >= dlnum:
                break

        print  "collecting ", len(ActualImages), " images"

        if not os.path.exists(DIR):
            os.mkdir(DIR)
        DIR = os.path.join(DIR, query.split()[0])

        if not os.path.exists(DIR):
            os.mkdir(DIR)
        ###print images
        for i, (img, Type) in enumerate(ActualImages):
            try:
                req = urllib2.Request(img, headers={'User-Agent': header})
                raw_img = urllib2.urlopen(req).read()

                cntr = len([i for i in os.listdir(DIR) if image_type in i]) + 1
                print cntr
                if len(Type) == 0:
                    f = open(os.path.join(DIR, image_type + "_" + str(cntr) + ".jpg"), 'wb')
                else:
                    f = open(os.path.join(DIR, image_type + "_" + str(cntr) + "." + Type), 'wb')

                f.write(raw_img)
                f.close()
                if dlnum <= cntr:
                    return
            except Exception as e:
                print "could not load : " + img
                print e

    def stop(self):
        pass


def create_skill():
    return PictureSkill()
