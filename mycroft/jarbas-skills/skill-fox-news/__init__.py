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


import feedparser
import time
from os.path import dirname
import re

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util import play_mp3
from mycroft.util.log import getLogger

__author__ = 'chrison999'

LOGGER = getLogger(__name__)


class FoxNewsSkill(MycroftSkill):
    def __init__(self):
        super(FoxNewsSkill, self).__init__(name="FoxNewsSkill")
#        self.url_rss = self.config['url_rss']
        self.process = None

    def initialize(self):
        intent = IntentBuilder("FoxNewsIntent").require(
            "FoxNewsKeyword").build()
        self.register_intent(intent, self.handle_intent)

    def handle_intent(self, message):
        try:
#            data = feedparser.parse("curl -s http://feeds.foxnewsradio.com/FoxNewsRadio |"
#                                    "grep '<link>http://feeds' |"
#                                    "sed -e 's/<link>//g' -e 's/<\/link>//g' -e 's/\t//g'")

            data = feedparser.parse("http://feeds.foxnewsradio.com/FoxNewsRadio")
            self.speak_dialog('fox.news')
            time.sleep(5)

#            self.process = play_mp3(data)

            self.process = play_mp3(
                re.sub(
                    'https', 'http', data['entries'][0]['links'][0]['href']))

        except Exception as e:
            LOGGER.error("Error: {0}".format(e))

    def stop(self):
        if self.process and self.process.poll() is None:
            self.speak_dialog('fox.news.stop')
            self.process.terminate()
            self.process.wait()


def create_skill():
    return FoxNewsSkill()
