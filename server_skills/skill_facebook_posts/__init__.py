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

from time import asctime

import pyjokes
import requests
from adapt.intent import IntentBuilder

from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


def get_soup(url):
    try:
        return BeautifulSoup(requests.get(url).text, "html.parser")
    except Exception as SockException:
        print SockException
        sys.exit(1)


class FbPost():
    def __init__(self, emitter):
        self.emitter = emitter

    def post_text(self, text, id="me", speech="Making a post on face book", link=None):
        self.emitter.emit(
            Message("fb_post_request", {"type": "text", "id": id, "link": link, "text": text, "speech": speech}))

    def post_link(self, link, text="", id="me", speech="Sharing a link on face book"):
        self.emitter.emit(
            Message("fb_post_request", {"type": "link", "id": id, "link": link, "text": text, "speech": speech}))


class FacebookPostsSkill(MycroftSkill):
    def __init__(self):
        super(FacebookPostsSkill, self).__init__(name="FacebookPostsSkill")

    def initialize(self):
        self.poster = FbPost(self.emitter)

        joke_intent = IntentBuilder("FbJokeIntent").require("fbJokeKeyword").build()
        self.register_intent(joke_intent, self.handle_joke_intent)

        btc_intent = IntentBuilder("FbBitcoinPricePostIntent") \
            .require("fbbtcKeyword").build()
        self.register_intent(btc_intent,
                             self.handle_btc_intent)

    def handle_joke_intent(self, message):
        joke = pyjokes.get_joke(language=self.lang[:-3], category='all')
        self.poster.post_text(joke, speech="Posting a joke on face book")

    def handle_btc_intent(self, message):
        time = asctime()
        bitcoinprice = requests.get("https://api.bitcoinaverage.com/all").json()['EUR']['averages']['24h_avg']
        text = "This is Jarbas BTC price service\nBitcoin price is: " + str(
            bitcoinprice) + " eur \nCurrent time is: " + time

        self.poster.post_text(text, speech="Posting bitcoin price on Face book")

    def stop(self):
        pass


def create_skill():
    return FacebookPostsSkill()
