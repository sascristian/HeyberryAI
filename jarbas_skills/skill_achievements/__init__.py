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

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message
import time, json

__author__ = 'jarbas'

logger = getLogger(__name__)


class AchievementsSkill(MycroftSkill):
    def __init__(self):
        super(AchievementsSkill, self).__init__(name="AchievementSkill")
        if "achievements" not in self.settings.keys():
            self.settings["achievements"] = {}
        self.last_achievement = None
        self.achievements = {}
        self.handlers = {}
        self.tweet = False

    def add_standard_achievements(self):
        self.register_achievement("inspirobot", {"timestamp": None, "text":
            "Asked Inspirobot for a quote",
                                                 "url": "http://http://inspirobot.me/"},
                                  "inspirobot.result")
        self.register_achievement("tweet",
                                  {"timestamp": None,
                                   "text": "Twitter bot unlocked",
                                   "url": "https://github.com/btotharye/mycroft-twitter-skill/"},
                                  "twitter.result")
        self.register_achievement("tts", {"timestamp": None,
                                          "text": "i speak therefore i am",
                                          "url": "https://mimic.mycroft.ai/"},
                                  "speak")
        self.register_achievement("tensor flow object recognition",
                                  {"timestamp": None,
                                   "text": "Recognized objects using tensorflow",
                                   "url":
                                       "https://medium.com/towards-data-science/building-a-real-time-object-recognition-app-with-tensorflow-and-opencv-b7a2b4ebdc32"},
                                  "object.recognition.result")

        # TODO these
        self.register_achievement("face detection", {"timestamp": None, "text":
            "Detected faces using haar cascades!",
                                                     "url": "https://pythonprogramming.net/haar-cascade-object-detection-python-opencv-tutorial/"})
        self.register_achievement("joke", {"timestamp": None, "text": "Said a "
                                                                      "joke",
                                           "url": "https://github.com/pyjokes/pyjokes"})
        self.register_achievement("facebook photo like", {"timestamp": None,
                                                          "text": "Liked a photo on Facebook",
                                                          "url": "https://www.facebook.com/profile.php?id=100017774057242"})
        self.register_achievement("facebook friend", {"timestamp": None,
                                                      "text": "Added a friend on Facebook",
                                                      "url": "https://www.facebook.com/profile.php?id=100017774057242"})
        self.register_achievement("facebook post", {"timestamp": None,
                                                    "text": "Facebook bot unlocked",
                                                    "url": "https://www.facebook.com/profile.php?id=100017774057242"})

        self.register_achievement("deep dream", {"timestamp": None,
                                                 "text": "deep dreaming performed",
                                                 "url": "http://www.pyimagesearch.com/2015/07/06/bat-country-an-extendible-lightweight-python-package-for-deep-dreaming-with-caffe-and-convolutional-neural-networks/"})
        self.register_achievement("deep draw", {"timestamp": None,
                                                "text": "deep draw performed",
                                                "url": "https://www.auduno.com/2015/08/04/drawing-with-googlenet/"})
        self.register_achievement("style transfer", {"timestamp": None,
                                                     "text": "style transfer performed",
                                                     "url": "https://frankzliu.com/artistic-style-transfer/"})
        self.register_achievement("googlenet classification",
                                  {"timestamp": None,
                                   "text": "Classified an image using BVLC_GoogleNet",
                                   "url": "http://adilmoujahid.com/posts/2016/06/introduction-deep-learning-python-caffe/"})

    def add_achievement(self, name, data=None):
        if data is None:
            data = {}
        if name not in self.settings["achievements"].keys():
            self.settings["achievements"][name] = data
            self.settings["achievements"][name]["count"] = 0
            self.settings["achievements"][name]["tweeted"] = False
        else:
            # update data
            count = self.settings["achievements"][name]["count"]
            self.settings["achievements"][name].update(data)
            self.settings["achievements"][name]["timestamp"] = time.time()
            # increase counter
            self.settings["achievements"][name]["count"] = count + 1
        self.settings.store()
        self.last_achievement = name

    def initialize(self):
        self.add_standard_achievements()
        self.last_achievement = None
        self.emitter.on("message", self.handle_new_achievement)

    def register_achievement(self, name, data, message_type=None, handler=None):
        self.add_achievement(name, data)
        if message_type is None:
            return
        self.achievements[message_type] = [name, data]
        self.handlers[name] = handler
        self.emitter.on(message_type, self.handle_new_achievement)

    def handle_new_achievement(self, message):
        _message = json.loads(message)
        type = _message.get("type")
        data = _message.get("data")
        if type in self.achievements.keys():
            name = self.achievements[type]
            self.last_achievement = name
        else:
            return

        # allow achievements to specify a handler to determine if it was meet
        condition = True
        if self.handlers[name]:
            condition = self.handlers[name]()
        if not condition:
            return
        self.add_achievement(name)
        if not self.settings["achievements"][name].get("tweeted", False):
            text = self.settings["achievements"][name]["text"] + " " + \
                   self.settings["achievements"][name].get("url", "")
            self.tweet_request(text + " #AchievementUnlocked")
            self.settings["achievements"][name]["tweeted"] = True
        if self.settings["achievements"][name]["count"] % 100 == 0:
            self.emitter.emit(Message("achievement", {"name": name,
                                                      "achievement":
                                                          self.settings[
                                                              "achievements"][
                                                              name]},
                                      self.context))
            text = str(self.settings["achievements"][name]["count"]) + " X " + \
                   self.settings["achievements"][name]["text"]
            self.tweet_request(text + " #AchievementUnlocked")
            self.speak("Achievement Unlocked " + text, metadata={"name": name,
                                                                 "achievement":
                                                                     self.settings[
                                                                         "achievements"][
                                                                         name]})

    def tweet_request(self, text):
        if self.tweet:
            tweet_type = "text"
            tweet_pic = None
            tweet_text = text
            self.emitter.emit(Message("tweet_request",
                                      {"tweet_type": tweet_type,
                                       "tweet_pic": tweet_pic,
                                       "tweet_text": tweet_text}, self.context))

    def stop(self):
        pass


def create_skill():
    return AchievementsSkill()