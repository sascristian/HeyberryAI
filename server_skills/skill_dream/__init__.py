import urllib2
import cv2
import numpy as np
import os
import random
import json
from bs4 import BeautifulSoup
from mycroft.messagebus.message import Message
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import time

__author__ = 'jarbas'

logger = getLogger(__name__)


class DreamSkill(MycroftSkill):

    def __init__(self):
        super(DreamSkill, self).__init__(name="DreamSkill")
        # make working directories, TODO refactor into config file
        self.sourcespath = os.path.dirname(__file__) + '/sources.txt'
        self.searchpath = "../pictures/search"
        self.sourcedir = "../pictures/random"
        self.outputdir = "../pictures/dreams"
        # check if folders exist
        if not os.path.exists(self.sourcedir):
            os.makedirs(self.sourcedir)
        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)
        if not os.path.exists(self.searchpath):
            os.makedirs(self.searchpath)
        ###imagine dimensions
        self.w = 640
        self.h = 480

        ### flag to avoid dreaming multiple times at once
        self.dreaming = False
        self.dream = None

    def initialize(self):
        self.emitter.on("deep_dream_result", self.receive_dream)

        prefixes = [
            'dream about', 'dream with', 'dream of', 'dream off', 'da']
        self.__register_prefixed_regex(prefixes, "(?P<DreamSearch>.*)")

        dream_about_intent = IntentBuilder("DreamAboutIntent") \
            .require("DreamSearch").build()
        self.register_intent(dream_about_intent,
                             self.handle_dream_about_intent)

        dream_intent = IntentBuilder("DreamIntent")\
            .require("dream").build()
        self.register_intent(dream_intent,
                             self.handle_dream_intent)

        # TODO guided dream

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    def dream(self, dream_pic, dream_guide=None, dream_name=None):
        self.dreaming = True
        self.dream = None
        self.emitter.emit(Message("deep_dream_request", {"dream_source":dream_pic, "dream_guide":dream_guide, "dream_name":dream_name}))
        start = time.time()
        elapsed = 0
        while self.dreaming and elapsed < 60 * 5:
            elapsed = time.time() - start
            time.sleep(0.2)
        self.dreaming = False
        return self.dream

    def receive_dream(self, message):
        self.dream = message.data.get("dream_url")
        self.dreaming = False
        self.speak("Dream received from server with sucess")

    def handle_dream_intent(self, message):
        if not self.dreaming:
            self.collectentropy()
            chosenpic = random.choice(os.listdir(self.sourcedir))
            imagepah = self.sourcedir+"/" + str(chosenpic)
            result = self.dream(imagepah)
            #if result is not None:
                #self.speak("Here is what i dreamed", metadata={"dream": result})

    def handle_dream_about_intent(self, message):
        imagepath = ""
        search = message.data.get("DreamSearch")
        if not self.dreaming:
            # collect dream entropy
            pics = self.search_image(search)
            imagepah = random.choice(pics)
            result = self.dream(imagepah)
            #if result is not None:
            #    self.speak("Here is what i dreamed", metadata={"dream": result})

    def stop(self):
        pass

    def collectentropy(self):
        # collect dream entropy
        self.store_raw_images(3)

    def store_raw_images(self, number=1):

        with open(self.sourcespath) as f:
            urls = f.readlines()
        i = 0
        pic_num = 0
        while i < number:
            try:
                image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
                chosenurl = random.choice(image_urls.split('\n'))
                print(chosenurl)
                url_response = urllib2.urlopen(chosenurl)
                img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
                img = cv2.imdecode(img_array, -1)
                print('Saving pic! ')
                # img = cv2.resize(img, (200, 200))
                cv2.imwrite(self.sourcedir+"/" + str(pic_num) + ".jpg", img)
                pic_num += 1
                i += 1

            except Exception as e:
                print(str(e))

    def search_image(self, search):
        self.speak("dreaming about " + search)
        self.searchanddl(search)
        pics = []
        search = search.replace(' ', '+')
        path = self.searchpath + "/" + search
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                pics.append(os.path.join(path, f))
        return pics

    def get_soup(self, url, header):
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')

    def searchanddl(self, searchkey, dlnum=5):
        query = searchkey  # raw_input("query image")# you can change the query for the image  here
        image_type = "ActiOn"
        query = query.split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
        print url
        # add the directory for your image here
        DIR = self.searchpath
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        }
        soup = self.get_soup(url, header)
        i = 0
        ActualImages = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            ActualImages.append((link, Type))
            i += 1
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
                #print cntr
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


def create_skill():
    return DreamSkill()
