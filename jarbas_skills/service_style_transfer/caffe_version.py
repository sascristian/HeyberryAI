"""
style.py - An implementation of "A Neural Algorithm of Artistic Style"
by L. Gatys, A. Ecker, and M. Bethge. http://arxiv.org/abs/1508.06576.
authors: Frank Liu - frank@frankzliu.com
         Dylan Paiton - dpaiton@gmail.com
last modified: 10/06/2015
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Frank Liu (fzliu) nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Frank Liu (fzliu) BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
# Service skill that performs style transfer, adapted from: https://github.com/fzliu/style-transfer
# May take up to 7 hours

__author__ = 'jarbas'

import os
import sys
import time
import timeit
from os.path import dirname

import numpy as np
from adapt.intent import IntentBuilder
from imgurpython import ImgurClient
from scipy.fftpack import ifftn
from scipy.linalg.blas import sgemm
from scipy.misc import imsave
from scipy.optimize import minimize
from skimage import img_as_ubyte
from skimage.transform import rescale
from mycroft.util.jarbas_services import StyleTransferService
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill

try:
    caffe_path = ConfigurationManager.get("caffe_path")
except:
    caffe_path = "../caffe"

sys.path.insert(0, caffe_path + '/python')

import caffe_version
# caffe.set_mode_gpu() # uncomment this if gpu processing is available

from time import sleep

# numeric constants
INF = np.float32(np.inf)
STYLE_SCALE = 1.2

# weights for the individual models
# assume that corresponding layers' top blob matches its name
VGG19_WEIGHTS = {"content": {"conv4_2": 1},
                 "style": {"conv1_1": 0.2,
                           "conv2_1": 0.2,
                           "conv3_1": 0.2,
                           "conv4_1": 0.2,
                           "conv5_1": 0.2}}
VGG16_WEIGHTS = {"content": {"conv4_2": 1},
                 "style": {"conv1_1": 0.2,
                           "conv2_1": 0.2,
                           "conv3_1": 0.2,
                           "conv4_1": 0.2,
                           "conv5_1": 0.2}}
GOOGLENET_WEIGHTS = {"content": {"conv2/3x3": 2e-4,
                                 "inception_3a/output": 1 - 2e-4},
                     "style": {"conv1/7x7_s2": 0.2,
                               "conv2/3x3": 0.2,
                               "inception_3a/output": 0.2,
                               "inception_4a/output": 0.2,
                               "inception_5a/output": 0.2}}
CAFFENET_WEIGHTS = {"content": {"conv4": 1},
                    "style": {"conv1": 0.2,
                              "conv2": 0.2,
                              "conv3": 0.2,
                              "conv4": 0.2,
                              "conv5": 0.2}}


class StyleTransferTool():
    def __init__(self, emitter):
        self.emitter = emitter
        self.emitter.on("style.transfer.result", self.end_wait)
        self.waiting = False
        self.url = None
        self.file_path = None
        self.time = None

    def style_transfer(self, style_path, target_path, iter_num=300, context=None):
        self.emitter.emit(
            Message("style.transfer.request", {"style_img": style_path, "target_img": target_path, "iter_num": iter_num}, context))
        self.wait()
        return self.file_path

    def get_url(self):
        return self.url

    def get_time(self):
        return self.time

    def wait(self):
        self.waiting = True
        while self.waiting:
            sleep(1)

    def end_wait(self, message):
        self.waiting = False
        self.url = message.data.get("url")
        self.file_path = message.data.get("file")
        self.time = message.data.get("elapsed_time")


class StyleTransferSkill(MycroftSkill):

    def __init__(self):
        super(StyleTransferSkill, self).__init__(name="StyleTransferSkill")
        self.reload_skill = False
        self.external_reload = False
        self.external_shutdown = False
        from caffe_version.io import load_image
        self.load_image = load_image

        try:
            client_id = self.config_core.get("APIS")["ImgurKey"]
            client_secret = self.config_core.get("APIS")["ImgurSecret"]
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
        self.save_path = dirname(__file__) + "/style_transfer"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def initialize(self):
        self.emitter.on("style.transfer.request", self.handle_style_transfer)
        self.emitter.on("style.transfer.result", self.handle_receive_transfer_result)

        style_transfer_intent = IntentBuilder("StyleTransferIntent") \
            .require("styletransfer").build()
        self.register_intent(style_transfer_intent,
                             self.handle_style_transfer_intent)

    def handle_receive_transfer_result(self, message):
        self.log.info("Style transfer result received " + message.data.get("url"))

    def handle_style_transfer_intent(self, message):
        if message.context is None:
            message.context = self.message_context
        style_img = dirname(__file__) + "/alien.jpg"
        target_img = dirname(__file__) + "/dariusz.jpg"
        iter_num = message.data.get("iter_num", 400)
        self.speak("testing style transfer")
        transfer = StyleTransferService(self.emitter)
        file = transfer.transfer_from_file(target_img, style_img, iter=iter_num, context=self.message_context, server=False)
        url = transfer.get_result().get("url")
        time = transfer.get_result().get("elapsed_time")
        self.speak("Style transfer test complete in " + str(time) + " seconds", metadata={"file": file, "url": url, "elapsed_time": time})

    def handle_style_transfer(self, message):
        if message.context is not None:
            self.message_context.update(message.context)
        name = message.data.get("name")
        style_img = message.data.get("style_img", dirname(__file__) + "/giger.jpg")
        target_img = message.data.get("target_img")
        iter_num = message.data.get("iter_num", 512)
        speak = message.data.get("speak", True)
        if name is None:
            name = time.asctime().replace(" ", "_")
        # load images
        try:
            img_style = self.load_image(style_img)
            img_content = self.load_image(target_img)
            self.log.info("images loaded")
        except:
            self.log.error("Could not load images: " + style_img + " | " + target_img)
            self.send_result()
            return
        # prepare style transfer
        # TODO make model configurable
        model_name = "vgg16"
        path = dirname(__file__) + '/models/' + model_name
        model_file = path + '/VGG_ILSVRC_16_layers_deploy.prototxt'
        pretrained_file = path + '/VGG_ILSVRC_16_layers.caffemodel'
        mean_file = caffe_path + '/python/caffe/imagenet/ilsvrc_2012_mean.npy'
        weights = VGG16_WEIGHTS
        self.log.info("preparing net for style transfer")
        if speak:
            self.speak("Starting style transfer, this may take up to 7 hours, i will let you know when ready")
        try:
            st = StyleTransfer(model_name, model_file, pretrained_file, mean_file, weights, logger=self.log)
        except Exception as e:
            self.log.error(e)
            self.speak(e)
            return
        # perform style transfer
        self.log.info("starting style transfer")
        start = timeit.default_timer()
        n_iters = st.transfer_style(img_style, img_content, length=512,
                                    init="content", ratio=np.float("1e4"),
                                    n_iter=iter_num, verbose=True)
        end = timeit.default_timer()
        e_time = end - start
        self.log.info("Ran {0} iterations in {1:.0f}s.".format(n_iters, e_time))
        img_out = st.get_generated()

        # save image
        out_path = self.save_path + "/" + name + '.jpg'
        self.log.info("saving image to " + out_path)
        imsave(out_path, img_as_ubyte(img_out))
        self.log.info("Output saved to {0}.".format(out_path))
        self.send_result(out_path, e_time)

    def send_result(self, out_path=None, e_time=None, error=None):
        if error is not None:
            self.speak(error)
        msg_type = "style.transfer.result"
        msg_data = {"file": None, "url": None, "elapsed_time": e_time}
        if out_path is not None:
            # upload pic
            data = self.client.upload_from_path(out_path)
            msg_data["url"] = data["link"]

        # to source socket
        if ":" in self.message_context["destinatary"]:
            if self.message_context["destinatary"].split(":")[1].isdigit():
                self.emitter.emit(Message("message_request",
                                          {"context": self.message_context, "data": msg_data,
                                           "type": msg_type}, self.message_context))
        # to bus
        msg_data["file"] = out_path
        self.emitter.emit(Message(msg_type,
                                  msg_data, self.message_context))
        self.speak("style transfer result: " + out_path + " " + str(e_time),
                   metadata=msg_data)

    def stop(self):
        pass


def create_skill():
    return StyleTransferSkill()


def _compute_style_grad(F, G, G_style, layer):
    """
        Computes style gradient and loss from activation features.
    """

    # compute loss and gradient
    (Fl, Gl) = (F[layer], G[layer])
    c = Fl.shape[0] ** -2 * Fl.shape[1] ** -2
    El = Gl - G_style[layer]
    loss = c / 4 * (El ** 2).sum()
    grad = c * sgemm(1.0, El, Fl) * (Fl > 0)

    return loss, grad


def _compute_content_grad(F, F_content, layer):
    """
        Computes content gradient and loss from activation features.
    """

    # compute loss and gradient
    Fl = F[layer]
    El = Fl - F_content[layer]
    loss = (El ** 2).sum() / 2
    grad = El * (Fl > 0)

    return loss, grad


def _compute_reprs(net_in, net, layers_style, layers_content, gram_scale=1):
    """
        Computes representation matrices for an image.
    """

    # input data and forward pass
    (repr_s, repr_c) = ({}, {})
    net.blobs["data"].data[0] = net_in
    net.forward()

    # loop through combined set of layers
    for layer in set(layers_style) | set(layers_content):
        F = net.blobs[layer].data[0].copy()
        F.shape = (F.shape[0], -1)
        repr_c[layer] = F
        if layer in layers_style:
            repr_s[layer] = sgemm(gram_scale, F, F.T)

    return repr_s, repr_c


def style_optfn(x, net, weights, layers, reprs, ratio):
    """
        Style transfer optimization callback for scipy.optimize.minimize().
        :param numpy.ndarray x:
            Flattened data array.
        :param caffe.Net net:
            Network to use to generate gradients.
        :param dict weights:
            Weights to use in the network.
        :param list layers:
            Layers to use in the network.
        :param tuple reprs:
            Representation matrices packed in a tuple.
        :param float ratio:
            Style-to-content ratio.
    """

    # update params
    layers_style = weights["style"].keys()
    layers_content = weights["content"].keys()
    net_in = x.reshape(net.blobs["data"].data.shape[1:])

    # compute representations
    (G_style, F_content) = reprs
    (G, F) = _compute_reprs(net_in, net, layers_style, layers_content)

    # backprop by layer
    loss = 0
    net.blobs[layers[-1]].diff[:] = 0
    for i, layer in enumerate(reversed(layers)):
        next_layer = None if i == len(layers) - 1 else layers[-i - 2]
        grad = net.blobs[layer].diff[0]

        # style contribution
        if layer in layers_style:
            wl = weights["style"][layer]
            (l, g) = _compute_style_grad(F, G, G_style, layer)
            loss += wl * l * ratio
            grad += wl * g.reshape(grad.shape) * ratio

        # content contribution
        if layer in layers_content:
            wl = weights["content"][layer]
            (l, g) = _compute_content_grad(F, F_content, layer)
            loss += wl * l
            grad += wl * g.reshape(grad.shape)

        # compute gradient
        net.backward(start=layer, end=next_layer)
        if next_layer is None:
            grad = net.blobs["data"].diff[0]
        else:
            grad = net.blobs[next_layer].diff[0]

    # format gradient for minimize() function
    grad = grad.flatten().astype(np.float64)

    return loss, grad


class StyleTransfer(object):
    """
        Style transfer class.
    """

    def __init__(self, model_name, model_file, pretrained_file, mean_file, weights, logger=None):
        """
            Initialize the model used for style transfer.
            :param str model_name:
                Model to use.
        """
        self.log = logger
        # add model and weights
        if self.log is not None:
            self.log.info("Loading model " + model_name)
        if not os.path.isfile(model_file):
            self.log.error(str(model_name) + " could not be found in path, check requirements.sh for download")
            self.abort = True
            return
        else:
            self.abort = False
            self.load_model(model_file, pretrained_file, mean_file)
        if self.log is not None:
            self.log.info("Loading weights")
        self.weights = weights.copy()
        self.layers = []
        for layer in self.net.blobs:
            if layer in self.weights["style"] or layer in self.weights["content"]:
                if self.log is not None:
                    self.log.info("Loading layer " + layer)
                self.layers.append(layer)

        # set the callback function
        def callback(xk):
            if self._callback is not None:
                net_in = xk.reshape(self.net.blobs["data"].data.shape[1:])
                self._callback(self.transformer.deprocess("data", net_in))

        self.callback = callback

    def load_model(self, model_file, pretrained_file, mean_file):
        """
            Loads specified model from caffe install (see caffe docs).
            :param str model_file:
                Path to model protobuf.
            :param str pretrained_file:
                Path to pretrained caffe model.
            :param str mean_file:
                Path to mean file.
        """

        # load net (supressing stderr output)
        null_fds = os.open(os.devnull, os.O_RDWR)
        out_orig = os.dup(2)
        os.dup2(null_fds, 2)
        net = caffe_version.Net(model_file, pretrained_file, caffe_version.TEST)
        os.dup2(out_orig, 2)
        os.close(null_fds)

        # all models used are trained on imagenet data
        transformer = caffe_version.io.Transformer({"data": net.blobs["data"].data.shape})
        transformer.set_mean("data", np.load(mean_file).mean(1).mean(1))
        transformer.set_channel_swap("data", (2, 1, 0))
        transformer.set_transpose("data", (2, 0, 1))
        transformer.set_raw_scale("data", 255)

        # add net parameters
        self.net = net
        self.transformer = transformer

    def get_generated(self):
        """
            Saves the generated image (net input, after optimization).
            :param str path:
                Output path.
        """

        data = self.net.blobs["data"].data
        img_out = self.transformer.deprocess("data", data)
        return img_out

    def _rescale_net(self, img):
        """
            Rescales the network to fit a particular image.
        """

        # get new dimensions and rescale net + transformer
        new_dims = (1, img.shape[2]) + img.shape[:2]
        self.net.blobs["data"].reshape(*new_dims)
        self.transformer.inputs["data"] = new_dims

    def _make_noise_input(self, init):
        """
            Creates an initial input (generated) image.
        """

        # specify dimensions and create grid in Fourier domain
        dims = tuple(self.net.blobs["data"].data.shape[2:]) + \
               (self.net.blobs["data"].data.shape[1],)
        grid = np.mgrid[0:dims[0], 0:dims[1]]

        # create frequency representation for pink noise
        Sf = (grid[0] - (dims[0] - 1) / 2.0) ** 2 + \
             (grid[1] - (dims[1] - 1) / 2.0) ** 2
        Sf[np.where(Sf == 0)] = 1
        Sf = np.sqrt(Sf)
        Sf = np.dstack((Sf ** int(init),) * dims[2])

        # apply ifft to create pink noise and normalize
        ifft_kernel = np.cos(2 * np.pi * np.random.randn(*dims)) + \
                      1j * np.sin(2 * np.pi * np.random.randn(*dims))
        img_noise = np.abs(ifftn(Sf * ifft_kernel))
        img_noise -= img_noise.min()
        img_noise /= img_noise.max()

        # preprocess the pink noise image
        x0 = self.transformer.preprocess("data", img_noise)

        return x0

    def transfer_style(self, img_style, img_content, length=512, ratio=1e5,
                       n_iter=512, init="-1", verbose=False, callback=None, context=None):
        """
            Transfers the style of the artwork to the input image.
            :param numpy.ndarray img_style:
                A style image with the desired target style.
            :param numpy.ndarray img_content:
                A content image in floating point, RGB format.
            :param function callback:
                A callback function, which takes images at iterations.
        """
        if self.abort:
            self.log.error("no model")
            return
        # assume that convnet input is square
        orig_dim = min(self.net.blobs["data"].shape[2:])

        # rescale the images
        if self.log is not None:
            self.log.info("Rescaling images")
        scale = max(length / float(max(img_style.shape[:2])),
                    orig_dim / float(min(img_style.shape[:2])))
        img_style = rescale(img_style, STYLE_SCALE * scale)
        scale = max(length / float(max(img_content.shape[:2])),
                    orig_dim / float(min(img_content.shape[:2])))
        img_content = rescale(img_content, scale)

        # compute style representations
        if self.log is not None:
            self.log.info("computing style representations")
        self._rescale_net(img_style)
        layers = self.weights["style"].keys()
        net_in = self.transformer.preprocess("data", img_style)
        gram_scale = float(img_content.size) / img_style.size
        G_style = _compute_reprs(net_in, self.net, layers, [],
                                 gram_scale=1)[0]

        # compute content representations
        if self.log is not None:
            self.log.info("computing content representations")
        self._rescale_net(img_content)
        layers = self.weights["content"].keys()
        net_in = self.transformer.preprocess("data", img_content)
        F_content = _compute_reprs(net_in, self.net, [], layers)[1]

        # generate initial net input
        # "content" = content image, see kaishengtai/neuralart
        if self.log is not None:
            self.log.info("Generating initial net input")
        if isinstance(init, np.ndarray):
            img0 = self.transformer.preprocess("data", init)
        elif init == "content":
            img0 = self.transformer.preprocess("data", img_content)
        elif init == "mixed":
            img0 = 0.95 * self.transformer.preprocess("data", img_content) + \
                   0.05 * self.transformer.preprocess("data", img_style)
        else:
            img0 = self._make_noise_input(init)

        # compute data bounds
        if self.log is not None:
            self.log.info("Computing data bounds")
        data_min = -self.transformer.mean["data"][:, 0, 0]
        data_max = data_min + self.transformer.raw_scale["data"]
        data_bounds = [(data_min[0], data_max[0])] * (img0.size / 3) + \
                      [(data_min[1], data_max[1])] * (img0.size / 3) + \
                      [(data_min[2], data_max[2])] * (img0.size / 3)

        # optimization params
        grad_method = "L-BFGS-B"
        reprs = (G_style, F_content)
        minfn_args = {
            "args": (self.net, self.weights, self.layers, reprs, ratio),
            "method": grad_method, "jac": True, "bounds": data_bounds,
            "options": {"maxcor": 8, "maxiter": n_iter, "disp": verbose}
        }

        # optimize
        if self.log is not None:
            self.log.info("Optimizing")
        self._callback = callback
        minfn_args["callback"] = self.callback
        res = minimize(style_optfn, img0.flatten(), **minfn_args).nit

        return res
