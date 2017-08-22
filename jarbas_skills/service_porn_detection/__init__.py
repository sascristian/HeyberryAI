from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft import MYCROFT_ROOT_PATH as root_path
from jarbas_models.tf_Porn_Recognition.nnpcr import NNPCR
from jarbas_utils.jarbas_services import url_to_pic

__author__ = 'jarbas'


class PornDetectionService(MycroftSkill):

    def __init__(self):
        super(PornDetectionService, self).__init__()
        self.reload_skill = False

        self.model_path = root_path + \
                          '/jarbas_models/TensorFlow/PornRecognition' \
                          '/porn_detect_model.bin'

    def initialize(self):
        self.emitter.on("porn.recognition.request", self.handle_is_this_porn_request)

        # TODO train neural net to say which pornstar looks more like you
        # TODO classify porn neural net
        # TODO download porn
        # TODO random porn!

        # only triggered in cli/fb or by context
        intent = IntentBuilder("PornRecogIntent") \
            .require("IsThisPornKeyword").require("PicturePath").build()
        self.register_intent(intent,
                             self.handle_is_this_porn_intent)

        intent = IntentBuilder("PornRecogIntent") \
            .require("IsThisPornKeyword").require("picture_url").build()
        self.register_intent(intent,
                             self.handle_is_this_porn_intent)

    def handle_is_this_porn_intent(self, message):
        pic = message.data.get("picture_url")
        if not pic:
            pic = message.data.get("PicturePath")
            if pic:
                self.set_context("PicturePath", pic)
        else:
            pic = url_to_pic(pic)
        predictions = self.is_this_porn([pic])
        self.speak(predictions)

    def handle_is_this_porn_request(self, message):
        pic = message.data.get("picture_path")
        predictions = self.is_this_porn([pic])
        self.emitter.emit(Message("porn.recognition.result",
                                  {"predictions": predictions},
                                  self.get_message_context(message.context)))

    def is_this_porn(self, picture_list):
        model = NNPCR()
        model.loadModel(self.model_path)
        predictions = model.predict(picture_list)
        print predictions
        return predictions

def create_skill():
    return PornDetectionService()