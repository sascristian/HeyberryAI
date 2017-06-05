import urllib2
import urllib
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
        self.outputdir = "../pictures/dreams"
        # check if folders exist
        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)
        ###imagine dimensions
        self.w = 640
        self.h = 480

        ### flag to avoid dreaming multiple times at once
        self.dreaming = False
        self.save = True

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
        self.emitter.emit(Message("deep_dream_request", {"dream_source":dream_pic, "dream_guide":dream_guide, "dream_name":dream_name}))
        start = time.time()
        elapsed = 0
        while self.dreaming and elapsed < 60 * 5:
            elapsed = time.time() - start
            time.sleep(0.2)
        self.dreaming = False

    def receive_dream(self, message):
        self.dreaming = False
        dream = message.data.get("dream_url")
        if self.save:
            self.speak("Dream received from server with sucess " + dream)

    def handle_dream_intent(self, message):
        if not self.dreaming:
            try:
                with open(self.sourcespath) as f:
                    urls = f.readlines()
                    image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
                    imagepath = random.choice(image_urls.split('\n'))
            except:
                imagepath = "https://mycroft.ai/wp-content/uploads/2017/02/mark1_white.png"
            result = self.dream(imagepath)

    def handle_dream_about_intent(self, message):
        search = message.data.get("DreamSearch")
        if not self.dreaming:
            # collect dream entropy
            self.speak("dreaming about " + search)
            pics = self.search_pic(search)
            imagepath = random.choice(pics)
            result = self.dream(imagepath)

    def stop(self):
        pass

    def get_soup(self, url, header):
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')

    def search_pic(self, searchkey, dlnum=5):
        query = searchkey  # raw_input("query image")# you can change the query for the image  here
        query = query.split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        }
        soup = self.get_soup(url, header)
        i = 0
        ActualImages = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link = json.loads(a.text)["ou"]
            ActualImages.append(link)
            i += 1
            if i >= dlnum:
                break
        return ActualImages


def create_skill():
    return DreamSkill()
