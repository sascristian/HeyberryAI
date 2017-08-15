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


try:
    from snowboydecoder import HotwordDetector
except:
    from mycroft.client.speech.recognizer.snowboy.snowboydecoder import HotwordDetector

from mycroft.client.speech.recognizer.local_recognizer import LocalRecognizer

__author__ = 'jarbas'


class SnowboyRecognizer(LocalRecognizer):
    def __init__(self, models_path_list, sensitivity=0.5, wake_word="snowboy"):
        self.key_phrase = wake_word
        self.snowboy = HotwordDetector(models_path_list,
                                       sensitivity=[sensitivity]*len(models_path_list))

    def found_wake_word(self, frame_data):
        wake_word = self.snowboy.detector.RunDetection(frame_data)
        return wake_word == 1
