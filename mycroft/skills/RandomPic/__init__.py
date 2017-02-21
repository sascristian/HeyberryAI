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

import random
import cv2
import numpy as np
from bs4 import BeautifulSoup
import urllib2
import os
import json
import cloudsight

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class PictureSkill(MycroftSkill):

    def __init__(self):
        super(PictureSkill, self).__init__(name="PictureSkill")
        apikey = self.config["cloudsight_key"]
        apisecret = self.config["secret"]
        auth = cloudsight.OAuth(apikey, apisecret)
        self.api = cloudsight.API(auth)

    def initialize(self):
        self.load_data_files(dirname(__file__))

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

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    def handle_identify_picture_intent(self, message):
        if not os.path.exists('RandomPic/pictures'):
            os.makedirs('RandomPic/pictures')
        path = os.path.dirname(__file__) + '/sources.txt'
        with open(path) as f:
            urls = f.readlines()
        sucess = False
        #only keep 50 pictures for amuzing
        i = 0
        for f in os.listdir("RandomPic/pictures"):
            if os.path.isfile(os.path.join("RandomPic/pictures", f)):
                i += 1
        if i <= 50:
            pic_num = i + 1
        else:
            pic_num = random.choice(range(0,50,1))
        while not sucess:
            try:
                image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
                chosenurl = random.choice(image_urls.split('\n'))
                LOGGER.info(chosenurl)
                #print(chosenurl)
                url_response = urllib2.urlopen(chosenurl)
                img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
                img = cv2.imdecode(img_array, -1)
                savepath = "RandomPic/pictures/" + str(pic_num) + ".jpg"
                LOGGER.info('Resizing and saving image to ' + savepath)
                img = cv2.resize(img, (640, 480))
                # img = cv2.resize(img, (200, 200))
                cv2.imwrite(savepath, img)
                sucess = True
                chosenurl =  savepath
                label = self.identifypicture(chosenurl)
                self.speak_dialog("iden")
                self.speak(label)
                cv2.imshow(label, img)
                cv2.waitKey(20000)

            except Exception as e:
                LOGGER.error(str(e))
                #print(str(e))

        cv2.destroyWindow('random picture')

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
        if not os.path.exists('RandomPic/pictures'):
            os.makedirs('RandomPic/pictures')
        path = os.path.dirname(__file__) + '/sources.txt'
        with open(path) as f:
            urls = f.readlines()
        sucess = False
        #only keep 50 pictures for amuzing
        i = 0
        for f in os.listdir("RandomPic/pictures"):
            if os.path.isfile(os.path.join("RandomPic/pictures", f)):
                i += 1
        if i <= 50:
            pic_num = i + 1
        else:
            pic_num = random.choice(range(0,50,1))
        while not sucess:
            try:
                image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
                chosenurl = random.choice(image_urls.split('\n'))
                LOGGER.info(chosenurl)
                #print(chosenurl)
                url_response = urllib2.urlopen(chosenurl)
                img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
                img = cv2.imdecode(img_array, -1)
                LOGGER.info('Resizing and saving image to ' + "random pic/" + str(pic_num) + ".jpg")
                img = cv2.resize(img, (640, 480))
                # img = cv2.resize(img, (200, 200))
                cv2.imwrite("RandomPic/pictures/" + str(pic_num) + ".jpg", img)
                sucess = True
                cv2.imshow('random picture', img)
                cv2.waitKey(20000)

            except Exception as e:
                LOGGER.error(str(e))
                #print(str(e))

        cv2.destroyWindow('random picture')

    def handle_search_picture_intent(self,message):
        #search = "anal porn lesbian"
        search = message.data.get("Search")
        self.speak("please wait while i search google pictures for "+ search)
        self.searchanddl(search)
        pics = []
        search = search.replace(' ', '+')
        path = "RandomPic/pictures/search/"+search
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                pics.append(os.path.join(path, f))
        pic = random.choice(pics)
        showpic = cv2.imread(pic)
        self.speak("heres your picture")
        cv2.imshow(search, showpic)
        cv2.waitKey(20000)
        cv2.destroyWindow(search)

    def get_soup(self, url, header):
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')

    def searchanddl(self, searchkey,dlnum=3):
        query = searchkey  # raw_input("query image")# you can change the query for the image  here
        image_type = "ActiOn"
        query = query.split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
        print url
        # add the directory for your image here
        DIR = "RandomPic/pictures/search"
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
        cv2.destroyAllWindows()
        pass


def create_skill():
    return PictureSkill()
