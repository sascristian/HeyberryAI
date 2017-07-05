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
from mycroft.messagebus.message import  Message
import time, json

__author__ = 'jarbas'

logger = getLogger(__name__)


class AchievementsSkill(MycroftSkill):

    def __init__(self):
        super(AchievementsSkill, self).__init__(name="AchievementSkill")
        if "achievements" not in self.settings.keys():
            self.settings["achievements"] = {}
        self.last_achievement = None

    def add_standard_achievements(self):
        self.add_achievement("face detection", {"timestamp": None, "text": "Detected faces using haar cascades!", "url":"https://pythonprogramming.net/haar-cascade-object-detection-python-opencv-tutorial/"})
        self.add_achievement("joke", {"timestamp": None, "text": "Said a joke"})
        self.add_achievement("facebook photo like", {"timestamp": None, "text": "Liked a photo on Facebook",
                                                       "url": "https://www.facebook.com/profile.php?id=100017774057242"})
        self.add_achievement("facebook friend", {"timestamp": None, "text": "Added a friend on Facebook",
                                                     "url": "https://www.facebook.com/profile.php?id=100017774057242"})
        self.add_achievement("facebook post", {"timestamp": None, "text": "Facebook bot unlocked",
                                             "url": "https://www.facebook.com/profile.php?id=100017774057242"})
        self.add_achievement("tweet", {"timestamp": None, "text": "Twitter bot unlocked",
                                          "url": "https://github.com/btotharye/mycroft-twitter-skill/"})
        self.add_achievement("tts", {"timestamp": None, "text": "i speak therefore i am", "url": "https://en.wikipedia.org/wiki/Speech_synthesis#Text-to-speech_systems"})
        self.add_achievement("deep dream", {"timestamp": None, "text": "deep dreaming performed", "url": "http://www.pyimagesearch.com/2015/07/06/bat-country-an-extendible-lightweight-python-package-for-deep-dreaming-with-caffe-and-convolutional-neural-networks/"})
        self.add_achievement("deep draw", {"timestamp": None, "text": "deep draw performed", "url": "https://www.auduno.com/2015/08/04/drawing-with-googlenet/"})
        self.add_achievement("style transfer", {"timestamp": None, "text": "style transfer performed",
                                           "url": "https://frankzliu.com/artistic-style-transfer/"})
        self.add_achievement("googlenet classification",
                             {"timestamp": None, "text": "Classified an image using BVLC_GoogleNet",
                              "url": "http://adilmoujahid.com/posts/2016/06/introduction-deep-learning-python-caffe/"})
        self.add_achievement("tensor flow object recognition",
                             {"timestamp": None, "text": "Recognized objects using tensorflow",
                              "url": "https://medium.com/towards-data-science/building-a-real-time-object-recognition-app-with-tensorflow-and-opencv-b7a2b4ebdc32"})

    def add_achievement(self, name, data=None):
        if data is None:
            data = {}
        if name not in self.settings["achievements"].keys():
            self.settings["achievements"][name] = data
            self.settings["achievements"][name]["count"] = 0
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

    def handle_new_achievement(self, message):
        _message = json.loads(message)
        type = _message.get("type")
        # TODO all achievements
        if "JokingIntent" in type:
            self.add_achievement("joke")
        elif "speak" in type:
            self.add_achievement("tts")
        elif "image_classification_result" in type:
            self.add_achievement("googlenet classification")
        elif "vision_result" in type and len(message.data.get("num_persons", 0)) > 0:
            self.add_achievement("first face detection")
        elif "class_visualization_result" in type:
            self.add_achievement("deep draw")
        elif "deep_dream_result" in type:
            self.add_achievement("deep dream")
        else:
            return
        self.log.info("Achievement unlocked " + str(self.last_achievement))
        self.emitter.emit(Message("achievement", {"name":self.last_achievement, "achievement":self.settings["achievements"][self.last_achievement]}, self.context))

    def stop(self):
        pass


def create_skill():
    return AchievementsSkill()
