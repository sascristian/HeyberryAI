from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from jarbas_utils.skill_tools import url_to_pic
from mycroft import MYCROFT_ROOT_PATH as root_path

import tensorflow as tf
from skimage.io import imsave
from skimage.transform import resize
import cv2
import time
from os.path import dirname, exists

from jarbas_models.tf_colorize.net import Net
from jarbas_models.tf_colorize.utils import *
from mycroft.skills.displayservice import DisplayService
from jarbas_utils.skill_dev_tools import ResponderBackend
from jarbas_utils.skill_tools import ColorizationQuery

from imgurpython import ImgurClient

__author__ = 'jarbas'


class ColorizationService(MycroftSkill):

    def __init__(self):
        super(ColorizationService, self).__init__()
        self.reload_skill = False
        self.model_path = root_path + '/jarbas_models/tf_colorization/models/model.ckpt'
        if not exists(self.model_path):
            # TODO download model
            self.log.error("no model for colorize, download from https://drive.google.com/file/d/0B-yiAeTLLamRWVVDQ1VmZ3BxWG8/view")
        try:
            client_id = self.APIS["ImgurKey"]
            client_secret = self.APIS["ImgurSecret"]
        except:
            if self.config is not None:
                client_id = self.config.get("ImgurKey")
                client_secret = self.config.get("ImgurSecret")
            else:
                # TODO throw error
                client_id = 'xx'
                client_secret = 'yyyyyyyyy'
        self.client = ImgurClient(client_id, client_secret)

    def initialize(self):
        self.responder = ResponderBackend(self.name, self.emitter, self.log)
        self.responder.set_response_handler("colorization.request", self.handle_colorize_request)
        intent = IntentBuilder("ColorizeIntent") \
            .require("ColorizeKeyword").optionally(
            "PicturePath").optionally("picture_url").optionally(
            "BlackWhiteKeyword").build()
        self.register_intent(intent,
                             self.handle_colorize_intent)
        self.display_service = DisplayService(self.emitter)

    def handle_colorize_intent(self, message):
        pic = message.data.get("picture_url", message.data.get("PictureUrl"))
        if not pic:
            pic = message.data.get("PicturePath")
            if not pic:
                pic = url_to_pic("https://unsplash.it/600")
        else:
            pic = url_to_pic(pic)

        colorize_tool = ColorizationQuery(self.name, self.emitter)
        result = colorize_tool.colorize(picture_path=pic, context=message.context)
        path = result.get("file")
        self.speak("Here is your colorized picture ", metadata=result,
                   message_context=colorize_tool.get_result(context=True))
        self.display_service.display([path, path.replace(".jpg", "_bw.jpg")],
                                     utterance=message.data.get("utterance"))

    def handle_colorize_request(self, message):
        url = message.data.get("picture_url")
        if url:
            pic = url_to_pic(url)
        else:
            pic = message.data.get("PicturePath")
        file, url = self.colorize([pic])
        data = {"url": url, "file": file, "original": file.replace(".jpg", "_bw.jpg")}
        context = self.get_message_context(message.context)
        self.responder.update_response_data(data, context)

    def colorize(self, file_path, name=None):
        img = cv2.imread(file_path)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        path = dirname(__file__) + "/" + name + "_bw.jpg"
        imsave(path, img)

        img = img[None, :, :, None]
        data_l = (img.astype(dtype=np.float32)) / 255.0 * 100 - 50

        # data_l = tf.placeholder(tf.float32, shape=(None, None, None, 1))
        autocolor = Net(train=False)

        conv8_313 = autocolor.inference(data_l)

        saver = tf.train.Saver()
        with tf.Session() as sess:
            saver.restore(sess, self.model_path)
            conv8_313 = sess.run(conv8_313)

        img_rgb = decode(data_l, conv8_313, 2.63)
        if name is None:
            name = time.asctime().replace(" ", "_")
        path = dirname(__file__) + "/" + name + ".jpg"
        imsave(path, img_rgb)
        data = self.client.upload_from_path(path)
        url = data["link"]
        return path, url


def create_skill():
    return ColorizationService()