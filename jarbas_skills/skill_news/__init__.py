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


import re
import time
import random
import feedparser
from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.skills.audioservice import AudioService

__author__ = 'jdorleans' , "jarbas", "chrison999"

LOGGER = getLogger(__name__)


class NewsSkill(MycroftSkill):
    def __init__(self):
        super(NewsSkill, self).__init__(name="NewsSkill")
        self.npr = "http://www.npr.org/rss/podcast.php?id=500005"
        self.fox = "http://feeds.foxnewsradio.com/FoxNewsRadio"
        self.cbc = "http://www.cbc.ca/podcasting/includes/hourlynews.xml"
        self.audio = None
        self.playing = False
        # TODO get from config
        self.default = "random"

    def initialize(self):
        intent = IntentBuilder("NewsIntent").require(
            "NewsKeyword").optionally("NewsSource").build()
        self.register_intent(intent, self.handle_intent)
        self.audio = AudioService(self.emitter)

    def handle_intent(self, message):
        self.playing = True
        sauce = message.data.get("NewsSource")
        if sauce:
            self.default = sauce

        if self.default == "fox":
            url_rss = self.fox
        elif self.default == "npr":
            url_rss = self.npr
        elif self.default == "cbc":
            url_rss = self.cbc
        else:
            url_rss = random.choice([self.fox, self.cbc, self.npr])
        try:
            data = feedparser.parse(url_rss)
            self.speak_dialog('news', {"source": self.default})
            time.sleep(3)
            self.audio.play(
                re.sub(
                    'https', 'http', data['entries'][0]['links'][0]['href']))

        except Exception as e:
            LOGGER.error("Error: {0}".format(e))
        self.playing = False

    def stop(self):
        if self.playing:
            self.speak_dialog("news.stop")
            self.playing = False


def create_skill():
    return NewsSkill()
