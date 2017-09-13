from os.path import dirname
import sys
sys.path.append(dirname(__file__))
import os
import time
import timeit
from stylize import stylize
import scipy.misc
import math
import numpy as np
from PIL import Image
from imgurpython import ImgurClient

from adapt.intent import IntentBuilder
from jarbas_utils.skill_tools import StyleTransferQuery as StyleTransferService
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft import MYCROFT_ROOT_PATH
from mycroft.skills.displayservice import DisplayService
from jarbas_utils.skill_dev_tools import ResponderBackend


__author__ = 'jarbas'

# default arguments
CHECKPOINT_OUTPUT = True
CONTENT_WEIGHT = 5e0
CONTENT_WEIGHT_BLEND = 1
STYLE_WEIGHT = 5e2
TV_WEIGHT = 1e2
STYLE_LAYER_WEIGHT_EXP = 1
LEARNING_RATE = 1e1
BETA1 = 0.9
BETA2 = 0.999
EPSILON = 1e-08
STYLE_SCALE = 1.0
ITERATIONS = 1000
VGG_PATH = MYCROFT_ROOT_PATH + \
           '/jarbas_models/tf_vgg19/imagenet-vgg-verydeep-19.mat'
POOLING = 'max'


class StyleTransferSkill(MycroftSkill):
    def __init__(self):
        super(StyleTransferSkill, self).__init__(name="StyleTransferSkill")
        self.reload_skill = False
        self.external_reload = False
        self.external_shutdown = False

        # imgur
        try:
            client_id = self.APIS["ImgurKey"]
            client_secret = self.APIS["ImgurSecret"]
        except:
            try:
                client_id = self.config.get("ImgurKey")
                client_secret = self.config.get("ImgurSecret")
            except:
                # TODO throw error
                client_id = 'xx'
                client_secret = 'yyyyyyyyy'

        self.client = ImgurClient(client_id, client_secret)
        self.waiting = False
        self.save_path = dirname(__file__) + "/style_transfer_results"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.maybe_download()

    def maybe_download(self):
        # TODO download
        if not os.path.isfile(VGG_PATH):
            self.log.error(
                "Network %s does not exist. (Did you forget to download it?)" % VGG_PATH)

    def initialize(self):
        self.responder = ResponderBackend(self.name, self.emitter, self.log)
        self.responder.set_response_handler("style.transfer.request", self.handle_style_transfer)

        style_transfer_intent = IntentBuilder("StyleTransferIntent") \
            .require("styletransfer").optionally("PicturePath").build()
        self.register_intent(style_transfer_intent,
                             self.handle_style_transfer_intent)
        self.display_service = DisplayService(self.emitter)


    def handle_style_transfer_intent(self, message):
        if message.context is None:
            message.context = self.message_context
        style_img = [dirname(__file__) + "/styles/HRGiger/alien.jpg", dirname(
            __file__) + "/styles/HRGiger/giger.jpg"]
        target_img = message.data.get("PicturePath", dirname(__file__) + "/test.jpg")
        iter_num = message.data.get("iter_num", 400)
        self.speak("testing style transfer")
        transfer = StyleTransferService(self.name, self.emitter)
        file = transfer.transfer_from_file(target_img, style_img, iter=iter_num,
                                           context=self.message_context, server=False)
        url = transfer.get_result().get("url")
        time = transfer.get_result().get("elapsed_time")
        self.speak("Style transfer test complete in " + str(time) + " seconds",
                   metadata={"file": file, "url": url, "elapsed_time": time})
        self.display_service.display([file],
                                     utterance=message.data.get("utterance"))

    def handle_style_transfer(self, message):
        self.log.info("Style Transfer request")
        if message.context is not None:
            self.message_context.update(message.context)
        name = message.data.get("name")
        # list of styles
        style_img = message.data.get("style_img", [
                                     dirname(__file__) + "/giger.jpg"])
        target_img = message.data.get("target_img")
        if target_img:
            self.set_context("PicturePath", target_img)
        iter_num = message.data.get("iter_num", ITERATIONS)
        speak = message.data.get("speak", True)
        if name is None:
            name = time.asctime().replace(" ", "_")
        # load images

        try:
            self.log.info("loading content image: " + target_img)
            content_image = imread(target_img)
            self.log.info("loading style images: " + str(style_img))
            style_images = [imread(style) for style in style_img]
            self.log.info("images loaded")
        except Exception as e:
            self.log.error(
                "Could not load images: " + str(e))
            self.send_result()
            return
        # prepare style transfer
        if speak:
            self.speak(
                "Starting style transfer, this may take up to 7 hours, i will let you know when ready")
        start = time.time()
        try:
            self.log.info("scaling images")
            width = message.data.get("width") # optionally resize pic
            if width is not None:
                new_shape = (int(math.floor(float(content_image.shape[0]) /
                                            content_image.shape[1] * width)),
                             width)
                content_image = scipy.misc.imresize(content_image, new_shape)

            target_shape = content_image.shape
            for i in range(len(style_images)):
                style_scale = STYLE_SCALE
                style_images[i] = scipy.misc.imresize(style_images[i],
                                                      style_scale *
                                                      target_shape[1] /
                                                      style_images[i].shape[1])

            style_blend_weights = None
            # how much each style matters
            self.log.info("Processing style weights")
            if style_blend_weights is None:
                # default is equal weights
                style_blend_weights = [1.0 / len(style_images) for _ in
                                       style_images]
            else:
                total_blend_weight = sum(style_blend_weights)
                style_blend_weights = [weight / total_blend_weight
                                       for weight in style_blend_weights]

            self.log.info("Processing initial guess and noiseblend")
            initial = None
            initial_noiseblend = None
            if initial is not None:
                initial = scipy.misc.imresize(imread(initial),
                                              content_image.shape[:2])
                # Initial guess is specified, but not noiseblend - no noise should be blended
                if initial_noiseblend is None:
                    initial_noiseblend = 0.0
            else:
                # Neither inital, nor noiseblend is provided, falling back to random generated initial guess
                if initial_noiseblend is None:
                    initial_noiseblend = 1.0
                if initial_noiseblend < 1.0:
                    initial = content_image

            # print progress every print_iterations
            print_iterations = 20
            # save every checkpoint_iterations
            checkpoint_iterations = 20
            self.log.info("Performing Style Transfer")
            for iteration, image in stylize(
                    network=VGG_PATH,
                    initial=initial,
                    initial_noiseblend=initial_noiseblend,
                    content=content_image,
                    styles=style_images,
                    preserve_colors=message.data.get("preserver_colors",
                                                     False),
                    iterations=iter_num,
                    content_weight=CONTENT_WEIGHT,
                    content_weight_blend=CONTENT_WEIGHT_BLEND,
                    style_weight=STYLE_WEIGHT,
                    style_layer_weight_exp=STYLE_LAYER_WEIGHT_EXP,
                    style_blend_weights=style_blend_weights,
                    tv_weight=TV_WEIGHT,
                    learning_rate=LEARNING_RATE,
                    beta1=BETA1,
                    beta2=BETA2,
                    epsilon=EPSILON,
                    pooling=POOLING,
                    print_iterations=print_iterations,
                    checkpoint_iterations=checkpoint_iterations
            ):
                output_file = None
                combined_rgb = image

                if iteration is not None:
                    if CHECKPOINT_OUTPUT:
                        if not os.path.exists(self.save_path + "/" + name):
                            os.mkdir(self.save_path + "/" + name)
                        output_file = self.save_path + "/" + name + "/" + str(
                            iteration) + '.jpg'
                else:
                    output_file = self.save_path + "/" + name + '.jpg'
                if output_file:
                    if iteration is None:
                        iteration = "final"
                    self.log.info("Saving iteration " + str(iteration))
                    imsave(output_file, combined_rgb)

        except Exception as e:
            self.log.error(e)
            self.speak(e)
            return
        e_time = time.time() - start
        minutes = e_time / 60
        self.log.info("Style Transfer finished, elapsed time: " + str(
            minutes) + " minutes")
        # send result
        out_path = self.save_path + "/" + name + '.jpg'
        msg_data = {"file": None, "url": None, "elapsed_time": e_time}
        if out_path is not None:
            # upload pic
            data = self.client.upload_from_path(out_path)
            msg_data["url"] = data["link"]
            msg_data["file"] = out_path
        self.responder.update_response_data(msg_data, self.message_context)

    def stop(self):
        pass


def create_skill():
    return StyleTransferSkill()


def imread(path):
    img = scipy.misc.imread(path).astype(np.float)
    if len(img.shape) == 2:
        # grayscale
        img = np.dstack((img,img,img))
    elif img.shape[2] == 4:
        # PNG with alpha channel
        img = img[:,:,:3]
    return img


def imsave(path, img):
    img = np.clip(img, 0, 255).astype(np.uint8)
    Image.fromarray(img).save(path, quality=95)