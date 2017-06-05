import cv2
import numpy as np
import time
import random
from PIL import Image
import imutils
import sys

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill

#import flickrapi

__author__ = 'jarbas'


class DreamService(MycroftSkill):

    def __init__(self):
        super(DreamService, self).__init__(name="DreamSkill")
        self.reload_skill = False

        try:
            path = self.config["caffe_path"]
        except:
            path = "../caffe"

        sys.path.insert(0, path + '/python')
        from batcountry import BatCountry

        self.model = "bvlc_googlenet"
        path += '/models/' + self.model

        # start batcountry instance (self, base_path, deploy_path=None, model_path=None,
        self.bc = BatCountry(path)#path,model_path=path)
        self.iter = 20#self.config["iter"] #dreaming iterations
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

        ###imagine dimensions
        self.w = 640
        self.h = 480

        ### flag to avoid dreaming multiple times at once
        self.dreaming = False

        self.outputdir = self.config_core["database_path"] + "/dreams/"

    def initialize(self):
        self.emitter.on("deep_dream_request", self.handle_dream)

        dream_status_intent = IntentBuilder("DreamStatusIntent") \
            .require("dream").build()
        self.register_intent(dream_status_intent,
                             self.handle_dream_status_intent)

    def handle_dream_status_intent(self, message):
        self.speak_dialog("dreamstatus")

    def handle_dream(self, message):
        source = message.data.get("dream_source")
        guide = message.data.get("dream_guide")
        name = message.data.get("dream_name")
        print source, guide, name

        if name is None:
            name = time.asctime()

        if guide is not None:
            result = self.guided_dream(source, guide, name)
        else:
            result = self.dream(source, name)

        if result is not None:
            # TODO upload on flickr, send remote link
            self.speak("Here is what i dreamed", metadata={"dream_url": result})

    #### dreaming functions
    def dream(self, imagepah, name):
        fails = 0
        if self.dreaming:
            self.speak("i am dreaming")
            return None
        else:
            self.speak("please wait while the dream is processed", more=True)

        while fails <= 5:
            layer = random.choice(self.layers)
            try:
                dreampic = imutils.resize(cv2.imread(imagepah), self.w, self.h)  # cv2.resize(img, (640, 480))
                self.dreaming = True
                image = self.bc.dream(np.float32(dreampic), end=layer, iter_n=int(self.iter))
                # write the output image to file
                result = Image.fromarray(np.uint8(image))
                outpath = self.outputdir + "/" + name
                result.save(outpath)
                self.dreaming = False
                return outpath
            except:
                fails += 1

        self.dreaming = False
        self.speak("Could not dream this time")
        return None

    def guided_dream(self, sourcepath, guidepath, name):
        # dreampic = np.zeros((480, 640, 3), np.uint8)
        if self.dreaming:
            self.speak("i am dreaming")
            return None
        else:
            self.speak_dialog("dream")
            self.speak("please wait while the dream is processed")
        fails = 0
        while fails <= 5:
            self.dreaming = True
            layer = random.choice(self.layers)
            try:
                features = self.bc.prepare_guide(Image.open(guidepath), end=layer)
                dreampic = imutils.resize(cv2.imread(sourcepath), self.w, self.h)  # cv2.resize(img, (640, 480))
                image = self.bc.dream(np.float32(dreampic), end=layer,
                                      iter_n=int(self.iter), objective_fn=self.bc.guided_objective,
                                      objective_features=features)

                # write the output image to file
                result = Image.fromarray(np.uint8(image))
                outpath = self.outputdir + name
                result.save(outpath)
                self.dreaming = False
                return outpath
            except:
                fails += 1
        self.dreaming = False
        self.speak("Could not dream this time")
        return None

    def stop(self):
        try:
            self.bc.cleanup()
            cv2.destroyAllWindows()
        except:
            pass


def create_skill():
    return DreamService()
