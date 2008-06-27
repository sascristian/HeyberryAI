from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft import MYCROFT_ROOT_PATH as root_path
from jarbas_models.tf_Porn_Recognition.nnpcr import NNPCR
from jarbas_utils.skill_tools import url_to_pic
from jarbas_utils.skill_dev_tools import ResponderBackend


__author__ = 'jarbas'


class PornDetectionService(MycroftSkill):

    def __init__(self):
        super(PornDetectionService, self).__init__()
        self.reload_skill = False

        self.model_path = root_path + \
                          '/jarbas_models/TensorFlow/PornRecognition' \
                          '/porn_detect_model.bin'

    def initialize(self):
        self.responder = ResponderBackend(self.name, self.emitter, self.log)
        self.responder.set_response_handler("porn.recognition.request", self.handle_is_this_porn_request)

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
        pic = message.data.get("picture_url", message.data.get("PictureUrl"))
        if not pic:
            pic = message.data.get("picture_path", message.data.get("PicturePath"))
        else:
            pic = url_to_pic(pic)
        if pic:
            self.set_context("PicturePath", pic)
            predictions = self.is_this_porn([pic])
            self.speak(predictions)
        else:
            self.speak("show me a picture first")

    def handle_is_this_porn_request(self, message):
        pic = message.data.get("picture_path", message.data.get("PicturePath"))
        self.handle_update_message_context(message)
        predictions = self.is_this_porn([pic])
        data = {"predictions": predictions}
        self.responder.update_response_data(data, self.message_context)

    def is_this_porn(self, picture_list):
        model = NNPCR()
        model.loadModel(self.model_path)
        predictions = model.predict(picture_list)
        print predictions
        return predictions

def create_skill():
    return PornDetectionService()