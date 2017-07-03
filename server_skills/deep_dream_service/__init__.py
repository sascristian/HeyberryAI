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
from mycroft.configuration import ConfigurationManager
from imgurpython import ImgurClient


try:
    path = ConfigurationManager.get("caffe_path")
except:
    path = "../caffe"

sys.path.insert(0, path + '/python')

from batcountry import BatCountry


__author__ = 'jarbas'


class Dream():
    def __init__(self, emitter):
        self.emitter = emitter
        self.emitter.on("deep_dream_result", self.end_wait)
        self.waiting = False
        self.url = None
        self.file_path = None
        self.time = None

    def dream(self, dream_source, dream_name=None, iter_num=15, context=None):
        self.emitter.emit(
            Message("deep_dream_request", {"dream_source": dream_source, "dream_name": dream_name, "iter_num": iter_num}, context))
        self.wait()
        return self.file_path

    def get_url(self):
        return self.url

    def get_time(self):
        return self.time

    def wait(self):
        self.waiting = True
        while self.waiting:
            time.sleep(1)

    def end_wait(self, message):
        self.waiting = False
        self.url = message.data.get("dream_url")
        self.file_path = message.data.get("file")
        self.time = message.data.get("elapsed_time")


class DreamService(MycroftSkill):

    def __init__(self):
        super(DreamService, self).__init__(name="DreamSkill")
        self.reload_skill = False

        # TODO get from config
        try:
            client_id = self.config_core.get("APIS")["ImgurKey"]
            client_secret = self.config_core.get("APIS")["ImgurSecret"]
        except:
            if self.config is not None:
                client_id = self.config.get("ImgurKey")
                client_secret = self.config.get("ImgurSecret")
            else:
                # TODO throw error
                client_id = 'xx'
                client_secret = 'yyyyyyyyy'

        self.client = ImgurClient(client_id, client_secret)

        try:
            self.path = self.config_core["caffe_path"]
        except:
            self.path = "../caffe"

        self.iter = self.config.get("iter_num", 25) #dreaming iterations
        self.layers = [ "inception_5b/output", "inception_5b/pool_proj",
                        "inception_5b/pool", "inception_5b/5x5",
                        "inception_5b/5x5_reduce", "inception_5b/3x3",
                        "inception_5b/3x3_reduce", "inception_5b/1x1",
                        "inception_5a/output", "inception_5a/pool_proj",
                        "inception_5a/pool", "inception_5a/5x5",
                        "inception_5a/5x5_reduce", "inception_5a/3x3",
                        "inception_5a/3x3_reduce", "inception_5a/1x1",
                        "pool4/3x3_s2", "inception_4e/output", "inception_4e/pool_proj",
                        "inception_4e/pool", "inception_4e/5x5",
                        "inception_4e/5x5_reduce", "inception_4e/3x3",
                        "inception_4e/3x3_reduce", "inception_4e/1x1",
                        "inception_4d/output", "inception_4d/pool_proj",
                        "inception_4d/pool", "inception_4d/5x5",
                        "inception_4d/5x5_reduce", "inception_4d/3x3",
                        "inception_4d/3x3_reduce", "inception_4d/1x1",
                        "inception_4c/output", "inception_4c/pool_proj",
                        "inception_4c/pool", "inception_4c/5x5",
                        "inception_4c/5x5_reduce", "inception_4c/3x3",
                        "inception_4c/3x3_reduce", "inception_4c/1x1",
                        "inception_4b/output", "inception_4b/pool_proj",
                        "inception_4b/pool", "inception_4b/5x5",
                        "inception_4b/5x5_reduce", "inception_4b/3x3",
                        "inception_4b/3x3_reduce", "inception_4b/1x1",
                        "inception_4a/output", "inception_4a/pool_proj",
                        "inception_4a/pool", "inception_4a/5x5",
                        "inception_4a/5x5_reduce", "inception_4a/3x3",
                        "inception_4a/3x3_reduce", "inception_4a/1x1",
                        "inception_3b/output", "inception_3b/pool_proj",
                        "inception_3b/pool", "inception_3b/5x5",
                        "inception_3b/5x5_reduce", "inception_3b/3x3",
                        "inception_3b/3x3_reduce", "inception_3b/1x1",
                        "inception_3a/output", "inception_3a/pool_proj",
                        "inception_3a/pool", "inception_3a/5x5",
                        "inception_3a/5x5_reduce", "inception_3a/3x3",
                        "inception_3a/3x3_reduce", "inception_3a/1x1",
                        "pool2/3x3_s2","conv2/norm2","conv2/3x3",
                        "conv2/3x3_reduce", "pool1/norm1"] #"pool1/3x3_s2" , "conv17x7_s2"

        # image dimensions
        self.w = 640
        self.h = 480

        self.outputdir = self.config_core["database_path"] + "/dreams/"

        # check if folders exist
        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

    def initialize(self):
        self.emitter.on("deep_dream_request", self.handle_dream)

        dream_status_intent = IntentBuilder("DreamStatusIntent") \
            .require("dream").build()
        #self.register_intent(dream_status_intent,
        #                     self.handle_dream_status_intent)

    def handle_dream_status_intent(self, message):
        self.speak_dialog("dreamstatus")

    def handle_dream(self, message):
        # TODO dreaming queue
        self.log.info("Dream request received")
        self.context = message.context
        source = message.data.get("dream_source")
        guide = message.data.get("dream_guide")
        name = message.data.get("dream_name")
        iter = message.data.get("iter_num", self.iter)
        result = None
        link = None
        elapsed_time = 0
        if source is None:
            self.log.error("No dream source")
        elif guide is not None:
            result = self.guided_dream(source, guide, name, iter)
        else:
            start = time.time()
            try:
                result = self.dream(source, name, iter)
            except Exception as e:
                self.log.error(str(e))
            elapsed_time = time.time() - start
        layer = random.choice(self.layers)
        if result is not None:
            data = self.client.upload_from_path(result)
            link = data["link"]
            self.speak("Here is what i dreamed", metadata={"url": link, "file": result, "elapsed_time": elapsed_time})
        else:
            self.speak("I could not dream this time")
        if ":" in message.context["destinatary"]: #socket
            self.emitter.emit(Message("message_request",
                                      {"context": message.context,
                                       "data": {"dream_url": link, "file": result, "elapsed_time": elapsed_time, "layer": layer},
                                       "type": "deep_dream_result"},
                                      message.context))
        self.emitter.emit(Message("deep_dream_result",
                                  {"dream_url": link, "file": result, "elapsed_time": elapsed_time},
                                  message.context))

    #### dreaming functions
    def dream(self, imagepah, name=None, iter=25, layer=None):
        self.speak("please wait while the dream is processed")
        if layer is None:
            layer = random.choice(self.layers)
        # start batcountry instance (self, base_path, deploy_path=None, model_path=None,
        # TODO any model
        self.log.info(layer)
        self.model = "bvlc_googlenet"
        self.path += '/models/' + self.model
        self.log.info(self.path)
        try:
            bc = BatCountry(self.path)  # path,model_path=path)
        except Exception as e:
            self.log.error(e)
        req = urllib.urlopen(imagepah)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)  # 'load it as it is'
        dreampic = imutils.resize(img, self.w, self.h)  # cv2.resize(img, (640, 480))
        if dreampic is None:
            self.log.error("Could not load seed dream pic " + imagepah)
            self.speak("I can't dream without a seed.. retry later")
            return
        image = bc.dream(np.float32(dreampic), end=layer, iter_n=iter)
        # write the output image to file
        result = Image.fromarray(np.uint8(image))
        if name is None:
            name = time.asctime().replace(" ", "_") + ".jpg"
        outpath = self.outputdir + name
        result.save(outpath)
        bc.cleanup()
        return outpath

    def guided_dream(self, sourcepath, guidepath, name=None, iter=25):
        self.log.error("Guided dream not implemented")
        return None

    def stop(self):
        pass


def create_skill():
    return DreamService()
