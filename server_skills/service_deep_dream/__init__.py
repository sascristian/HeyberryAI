# Adapted by github.com/jnordberg from https://github.com/tensorflow/tensorflow/tree/master/tensorflow/examples/tutorials/deepdream
# Adapted by github.com/ProGamerGov from https://github.com/jnordberg/dreamcanvas

import cv2
import time
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from imgurpython import ImgurClient
import urllib2
import random
import json
from bs4 import BeautifulSoup
import urllib

import scipy.ndimage as spi
from skimage.io import imread, imsave
import numpy as np
import os
from os.path import dirname
import tensorflow as tf
from PIL import Image

from mycroft.util.jarbas_services import DreamService as DD

__author__ = 'jarbas'


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

        self.channel_value = 139
        # TODO all layers
        self.layers = ['mixed4d_3x3_bottleneck_pre_relu']
        self.iter_value = 10
        self.octave_value = 4
        self.octave_scale_value = 1.4
        self.step_size = 1.5
        self.tile_size = 512

        self.model_path = dirname(__file__) + '/model/tensorflow_inception_graph.pb'
        self.model_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.model_path)
        self.print_model = True
        self.verbose = True
        self.last_layer = None
        self.last_grad = None
        self.last_channel = None
        self.graph = None
        self.sess = None
        self.t_input = None
        self.iter = self.config.get("iter_num", 25) #dreaming iterations

        self.outputdir = self.config_core["database_path"] + "/dreams/"

        # check if folders exist
        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        # TODO check if model exists, if not download!
        # wget https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip
        # unzip -d model inception5h.zip
        # helper resize function using TF
        self.resize = tffunc(self.sess, np.float32, np.int32)(resize)

    def initialize(self):
        self.emitter.on("deep.dream.request", self.handle_dream)

        dream_intent = IntentBuilder("DreamIntent") \
            .require("dream").optionally("Subject").build()
        self.register_intent(dream_intent,
                             self.handle_dream_intent)

    def handle_dream_intent(self, message):
        search = message.data.get("Subject")
        if search:
            # collect dream entropy
            self.speak("dreaming about " + search)
            pics = self.search_pic(search)
            url = random.choice(pics)
        else:
            url = "https://unsplash.it/640/480/?random"
        req = urllib.urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)  # 'load it as it is'
        cv2.imwrite(dirname(__file__)+"/dream_seed.jpg", img)
        dreamer = DD(self.emitter)
        dreamer.dream_from_file(dirname(__file__)+"/dream_seed.jpg", context=message.context, server=False)

    def handle_dream(self, message):
        # TODO dreaming queue, all params from message
        self.log.info("Dream request received")
        self.context = message.context
        source = message.data.get("dream_source")
        guide = message.data.get("dream_guide")
        name = message.data.get("dream_name")
        iter = message.data.get("iter_num", self.iter)

        result = None
        link = None
        start = time.time()
        if source is None:
            self.log.error("No dream source")
        elif guide is not None:
            result = self.guided_dream(source, guide, name, iter)
        else:
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
                                       "type": "deep.dream.result"},
                                      message.context))
        self.emitter.emit(Message("deep.dream.result",
                                  {"dream_url": link, "file": result, "elapsed_time": elapsed_time},
                                  message.context))

    #### dreaming functions
    def dream(self, imagepah, name=None, iter=25, layer=None):
        self.speak("please wait while the dream is processed, this can take up to 15 minutes")
        if layer is None:
            layer = random.choice(self.layers)

        dreampic = spi.imread(imagepah, mode="RGB")
        if dreampic is None:
            self.log.error("Could not load seed dream pic " + imagepah)
            self.speak("I can't dream without a seed.. retry later")
            return

        # creating TensorFlow session and loading the model
        self.graph = tf.Graph()
        self.sess = tf.InteractiveSession(graph=self.graph)
        # update resize function using TF session
        self.resize = tffunc(self.sess, np.float32, np.int32)(resize)
        with tf.gfile.FastGFile(self.model_fn, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
        self.t_input = tf.placeholder(np.float32, name='input')  # define the input tensor
        imagenet_mean = 117.0
        t_preprocessed = tf.expand_dims(self.t_input - imagenet_mean, 0)
        tf.import_graph_def(graph_def, {'input': t_preprocessed})

        # Optionally print the inputs and layers of the specified graph.
        if not self.print_model:
            self.log.debug(self.graph.get_operations())
        # TODO get everything from message
        image = self.render(dreampic, layer=layer, channel=self.channel_value, iter_n=iter, step=self.step_size,
                    octave_n=self.octave_value, octave_scale=self.octave_scale_value)
        # write the output image to file
        if name is None:
            name = time.asctime().replace(" ", "_") + ".jpg"
        if ".jpg" not in name:
            name += ".jpg"
        outpath = self.outputdir + name
        self.log.info("Saving dream: " + outpath)
        imsave(outpath, image)
        return outpath

    def guided_dream(self, sourcepath, guidepath, name=None, iter=25):
        self.log.error("Guided dream not implemented")
        return None

    ## dream internals
    def T(self, layer):
        '''Helper for getting layer output tensor'''
        return self.graph.get_tensor_by_name("import/%s:0" % layer)

    def calc_grad_tiled(self, img, t_grad, tile_size=512):
        '''Compute the value of tensor t_grad over the image in a tiled way.
        Random shifts are applied to the image to blur tile boundaries over
        multiple iterations.'''
        sz = tile_size
        h, w = img.shape[:2]
        sx, sy = np.random.randint(sz, size=2)
        img_shift = np.roll(np.roll(img, sx, 1), sy, 0)
        grad = np.zeros_like(img)
        for y in range(0, max(h - sz // 2, sz), sz):
            for x in range(0, max(w - sz // 2, sz), sz):
                sub = img_shift[y:y + sz, x:x + sz]
                g = self.sess.run(t_grad, {self.t_input: sub})
                grad[y:y + sz, x:x + sz] = g
        return np.roll(np.roll(grad, -sx, 1), -sy, 0)

    def render_deepdream(self, t_grad, img0, iter_n=10, step=1.5, octave_n=4, octave_scale=1.4):
        # split the image into a number of octaves
        img = img0
        octaves = []
        for i in range(octave_n - 1):
            hw = img.shape[:2]
            lo = self.resize(img, np.int32(np.float32(hw) / octave_scale))
            hi = img - self.resize(lo, hw)
            img = lo
            octaves.append(hi)

        # generate details octave by octave
        for octave in range(octave_n):
            if octave > 0:
                hi = octaves[-octave]
                img = self.resize(img, hi.shape[:2]) + hi
            for i in range(iter_n):
                # g = calc_grad_tiled(img, t_grad)
                g = self.calc_grad_tiled(img, t_grad, self.tile_size)
                img += g * (step / (np.abs(g).mean() + 1e-7))
                if self.verbose:
                    self.log.info("Iteration Number: %d" % i)
            if self.verbose:
                self.log.info("Octave Number: %d" % octave)

        return Image.fromarray(np.uint8(np.clip(img / 255.0, 0, 1) * 255))

    def render(self, img, layer='mixed4d_3x3_bottleneck_pre_relu', channel=139, iter_n=10, step=1.5, octave_n=4,
               octave_scale=1.4):
        if self.last_layer == layer and self.last_channel == channel:
            t_grad = self.last_grad
        else:
            if channel == 4242:
                t_obj = tf.square(self.T(layer))
            else:
                t_obj = self.T(layer)[:, :, :, channel]
            t_score = tf.reduce_mean(t_obj)  # defining the optimization objective
            t_grad = tf.gradients(t_score, self.t_input)[0]  # behold the power of automatic differentiation!
            self.last_layer = layer
            self.last_grad = t_grad
            self.last_channel = channel
        img0 = np.float32(img)
        return self.render_deepdream(t_grad, img0, iter_n, step, octave_n, octave_scale)

    ## pic search
    def get_soup(self, url, header):
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')

    def search_pic(self, searchkey, dlnum=5):
        query = searchkey  # raw_input("query image")# you can change the query for the image  here
        query = query.split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        }
        soup = self.get_soup(url, header)
        i = 0
        ActualImages = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link = json.loads(a.text)["ou"]
            ActualImages.append(link)
            i += 1
            if i >= dlnum:
                break
        return ActualImages

    def stop(self):
        pass


def create_skill():
    return DreamService()


def tffunc(session, *argtypes):
    '''Helper that transforms TF-graph generating function into a regular one.
    See "resize" function below.
    '''
    placeholders = list(map(tf.placeholder, argtypes))

    def wrap(f):
        out = f(*placeholders)

        def wrapper(*args, **kw):
            return out.eval(dict(zip(placeholders, args)), session=session)

        return wrapper

    return wrap


# Helper function that uses TF to resize an image
def resize(img, size):
    img = tf.expand_dims(img, 0)
    return tf.image.resize_bilinear(img, size)[0, :, :, :]
