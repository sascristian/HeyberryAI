import numpy as np
import sys, time
from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger

__author__ = 'jarbas'


class ImageRecognitionService():
    def __init__(self, emitter, timeout=30, logger=None, server=False):
        self.emitter = emitter
        self.waiting = False
        self.server = server
        self.image_classification_result = None
        self.timeout = timeout
        if logger is not None:
            self.logger = logger
        else:
            self.logger = getLogger("ImageRecognitionService")
        self.emitter.on("image_classification_result", self.end_wait)

    def end_wait(self, message):
        if message.type == "image_classification_result":
            self.logger.info("image classification result received")
            self.image_classification_result = message.data["result"]
        self.waiting = False

    def wait(self):
        start = time.time()
        elapsed = 0
        self.waiting = True
        while self.waiting and elapsed < self.timeout:
            elapsed = time.time() - start
            time.sleep(0.1)

    def local_image_classification(self, picture_path, user_id="unknown"):
        requester = user_id
        message_type = "image_classification_request"
        message_data = {"file": picture_path, "source": requester, "user":"unknown"}
        self.emitter.emit(Message(message_type, message_data))
        self.wait()
        result = self.image_classification_result["classification"]
        return result

    def server_image_classification(self, picture_path, user_id="unknown"):
        requester = user_id
        message_type = "image_classification_request"
        message_data = {"file": picture_path, "source": requester, "user":"unknown"}
        self.emitter.emit(Message("server_request", {"server_msg_type":"file", "requester":requester, "message_type": message_type, "message_data": message_data}))
        self.wait()
        result = self.image_classification_result["classification"]
        return result


class ImageRecognitionSkill(MycroftSkill):

    def __init__(self):
        super(ImageRecognitionSkill, self).__init__(name="ImageRecognitionSkill")
        #self.reload_skill = False
        # load caffe
        try:
            self.path = self.config["caffe_path"]
        except:
            self.path = "../caffe"

        sys.path.insert(0, self.path + '/python')
        import caffe
        from caffe.io import load_image
        self.load_image = load_image
        # load net
        try:
           self.model = self.config["caffe_path"]
        except:
            self.model = "bvlc_googlenet"

        path = self.path + '/models/' + self.model

        self.net = caffe.Classifier(path + '/deploy.prototxt', path + '/' + self.model + '.caffemodel',
                                    mean=np.load(self.path + '/python/caffe/imagenet/ilsvrc_2012_mean.npy').mean(1).mean(1),
                                    channel_swap=(2, 1, 0),
                                    raw_scale=255,
                                    image_dims=(224, 224))

        # output to text
        self.label_mapping = np.loadtxt(dirname(__file__) + "/synset_words.txt", str, delimiter='\t')

    def initialize(self):
        self.emitter.on("image_classification_request", self.handle_classify)

        image_recog_status_intent = IntentBuilder("ImageClassfyStatusIntent") \
            .require("imgstatus").build()
        self.register_intent(image_recog_status_intent,
                             self.handle_img_recog_intent)

    def handle_img_recog_intent(self, message):
        self.speak_dialog("imgrecogstatus")
        classifier = ImageRecognitionService(self.emitter)
        result = classifier.local_image_classification(dirname(__file__)+"/obama.jpg", message.data.get("target"))
        self.speak("in test image i see " + result[0] + ", or maybe it is " + result[1])

    def handle_classify(self, message):
        pic = message.data.get("file")
        user_id = message.data.get("source")

        if user_id is not None:
            if user_id == "unknown":
                user_id = "all"
            self.target = user_id
        else:
            self.log.warning("no user/target specified")
            user_id = "all"

        self.log.info("loading image: " + pic)
        try:
            input_image = self.load_image(pic)
        except Exception as e:
            self.log.error(e)

        self.log.info("predicting")
        result = []
        try:
            prediction = self.net.predict([input_image])
            ind = prediction[0].argsort()[-5:][::-1]  # top-5 predictions
            for i in ind:
                result.append(self.label_mapping[i])
        except Exception as e:
            self.log.error(e)

        self.log.info(result)

        # send result
        msg_type = "image_classification_result"
        msg_data = {"classification":result}
        # to source socket
        try:
            if user_id.split(":")[1].isdigit():
                self.emitter.emit(Message("message_request",
                                          {"user_id": user_id, "data":msg_data,
                                           "type": msg_type}))
        except:
            pass
        # to bus
        self.emitter.emit(Message(msg_type,
                                  msg_data))

    def stop(self):
        pass


def create_skill():
    return ImageRecognitionSkill()
