import cv2
import numpy as np
import time
import random
from PIL import Image
import imutils
import sys
import urllib
import os
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message

from imgurpython import ImgurClient

__author__ = 'jarbas'


class ImageRecognitionService(MycroftSkill):

    def __init__(self):
        super(ImageRecognitionService, self).__init__(name="ImageRecognitionSkill")
        self.reload_skill = False

        try:
            path = self.config["caffe_path"]
        except:
            path = "../caffe"

        sys.path.insert(0, path + '/python')
        import caffe

        self.model = "bvlc_googlenet"
        path += '/models/' + self.model

        self.net = caffe.Net(path + '/deploy.prototxt',
                        self.model + '.caffemodel', caffe.TEST)

    def initialize(self):
        self.emitter.on("image_classify_request", self.handle_classify)

        dream_status_intent = IntentBuilder("ImageClassfyStatusIntent") \
            .require("imgstatus").build()
        self.register_intent(dream_status_intent,
                             self.handle_img_recog_intent)

    def handle_img_recog_intent(self, message):
        self.speak_dialog("imgrecogstatus")

    def handle_classify(self, message):
        # TODO dreaming queue
        source = message.data.get("dream_source")
        guide = message.data.get("dream_guide")
        name = message.data.get("dream_name")
        user_id = message.data.get("source")

        if user_id is not None:
            if user_id == "unknown":
                user_id = "all"
            self.target = user_id
        else:
            self.log.warning("no user/target specified")
            user_id = "all"

        if name is None:
            name = time.asctime().replace(" ","_") + ".jpg"

        if guide is not None:
            result = self.guided_dream(source, guide, name)
        else:
            result = self.dream(source, name)

        print result
        if result is not None:
            data = self.client.upload_from_path(result)
            link = data["link"]
            self.speak("Here is what i dreamed", metadata={"dream_url": link})
            self.emitter.emit(Message("message_request", {"user_id":user_id, "data":{"dream_url":link}, "type":"deep_dream_result"}))

    def stop(self):
        pass


def create_skill():
    return ImageRecognitionService()
