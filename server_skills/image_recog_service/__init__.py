import numpy as np
import sys, cv2
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

        # pre-process input image stuff
        #self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
        # set mean_image
        #self.transformer.set_mean('data', np.load().mean(1).mean(1))
        # subtract mean image from input image
        #self.transformer.set_transpose('data', (2, 0, 1))
        #self.transformer.set_channel_swap('data', (2, 1, 0))  # if using RGB instead of BGR
        #self.transformer.set_raw_scale('data', 255.0)
        # reshape the blobs so that they match the image shape file
        #self.net.blobs['data'].reshape(1, 3, 227, 227)

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
        self.emitter.emit(Message("image_classification_request", {"file":dirname(__file__)+"/obama.jpg", "source":"testing"}))

    def handle_classify(self, message):
        import caffe
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
            input_image = caffe.io.load_image(pic)
        except Exception as e:
            self.log.error(e)

        self.log.info("predicting")
        result = []
        try:
            prediction = self.net.predict([input_image])
            ind = prediction[0].argsort()#[-5:][::-1]  # top-5 predictions
            for i in ind:
                result.append(self.label_mapping[i])
        except Exception as e:
            self.log.error(e)

        self.log.info(result)
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
