from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from threading import Timer
from os.path import dirname, exists
from os import makedirs

import numpy as np
import cv2
from imutils.video import FPS
from imutils.video import WebcamVideoStream as eye
import imutils
from time import asctime, sleep
__author__ = "jarbas"

# Mapping based on Jeffers phoneme to viseme map, seen in table 1 from:
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.221.6377&rep=rep1&type=pdf
#
# Mycroft unit visemes based on images found at:
# http://www.web3.lu/wp-content/uploads/2014/09/visemes.jpg
#
# Mapping was created partially based on the "12 mouth shapes visuals seen at:
# https://wolfpaulus.com/journal/software/lipsynchronization/

VISIMES = {
    'uh': '2',
    'uw': '2',
    'er': '2',
    'ow': '2',
    'aw': '1',
    'th': '3',
    'dh': '3',
    'zh': '3',
    'ch': '3',
    'sh': '3',
    'jh': '3',
    'oy': '6',
    'ao': '6',
    'ae': '0',
    'eh': '0',
    'ey': '0',
    'ah': '0',
    'ih': '0',
    'iy': '0',
    'aa': '0',
    'ay': '0',
    'ax': '0',
    'hh': '0',
    'ng': '3',
    'n': '3',
    't': '3',
    'd': '3',
    'l': '3',
    'g': '3',
    'y': '0',
    'z': '3',
    's': '3',
    'w': '2',
    'b': '4',
    'p': '4',
    'm': '4',
    'r': '2',
    'v': '5',
    'f': '5',
    'k': '3',
    'pau': '4'
}


class FaceSkill(MycroftSkill):

    def __init__(self):
        super(FaceSkill, self).__init__(name="FaceSkill")
        self.reload_skill = False
        self.visemes = []
        self.speaking = False
        self.speed = 100
        sprites = cv2.imread(dirname(__file__) + "/visemes.jpg")
        sprites = cv2.resize(sprites, (500, 200))
        cv2.imshow("mouth", sprites)
        height, width = sprites.shape[:2]
        sprite_h = height/2
        sprite_w = width/5
        for i in range(0, 5):
            sprite = sprites[0:sprite_h, sprite_w * i:sprite_w * (i+1)]
            self.visemes.append(sprite)
            sprite = sprites[sprite_h:height, sprite_w * i:sprite_w * (i+1)]
            self.visemes.append(sprite)

    def initialize(self):
        self.emitter.on("speak", self.handle_viseme)
        self.face_thread = Timer(0, self.face_thread)
        self.face_thread.daemon = True
        self.face_thread.start()
        self.build_intents()

    def face_thread(self):
        while True:
            if not self.speaking:
                cv2.imshow("mouth", self.visemes[5])
                cv2.waitKey(50)
            else:
                sleep(1)

    def handle_viseme(self, message):
        utterance = message.data["utterance"]
        for sound in VISIMES:
            utterance = utterance.replace(sound, VISIMES[sound])
        i = 0
        for char in utterance:
            if not char.isdigit():
                utterance = utterance.replace(char, "1")
        self.draw(utterance)
        #self.code = int(message.data["code"])
        #self.draw()
        #print self.code

    def draw(self, utterance):
        self.speaking = True
        for char in utterance:
            cv2.imshow("mouth", self.visemes[int(char)])
            cv2.waitKey(self.speed)
        self.speaking = False

    def build_intents(self):
        pass

    def stop(self):
        cv2.destroyAllWindows()


def create_skill():
    return FaceSkill()
