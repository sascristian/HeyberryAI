import numpy as np
import sys
from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message

__author__ = 'jarbas'


class ImageRecognitionService(MycroftSkill):

    def __init__(self):
        super(ImageRecognitionService, self).__init__(name="ImageRecognitionSkill")
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

        dream_status_intent = IntentBuilder("ImageClassfyStatusIntent") \
            .require("imgstatus").build()
        self.register_intent(dream_status_intent,
                             self.handle_img_recog_intent)

    def handle_img_recog_intent(self, message):
        self.speak_dialog("imgrecogstatus")
        self.emitter.emit(Message("image_classification_request", {"file":dirname(__file__)+"/obama.jpg", "source":message.data.get("target")}))

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
        self.speak("in test image i see " + result[0] + ", or maybe it is " + result[1])
        # send result
        msg_type = "image_classification_result"
        msg_data = {"classfication":result}
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
    return ImageRecognitionService()
