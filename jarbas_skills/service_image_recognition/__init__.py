import numpy as np
import scipy.ndimage as nd
import PIL.Image
import sys, time, random, os
from os.path import dirname
from imgurpython import ImgurClient
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from fuzzywuzzy import fuzz
from mycroft.skills.jarbas_service import ServiceBackend

try:
    path = ConfigurationManager.get("caffe_path")
except:
    path = "../caffe"

sys.path.insert(0, path + '/python')

# caffe.set_mode_gpu() # uncomment this if gpu processing is available

__author__ = 'jarbas'


class ImageRecogService(ServiceBackend):
    def __init__(self, emitter=None, timeout=125, waiting_messages=None, logger=None):
        super(ImageRecogService, self).__init__(name="ImageRecognitionService", emitter=emitter, timeout=timeout, waiting_messages=waiting_messages, logger=logger)

    def get_classification(self, file_path, server=True, context=None):
        if context is None:
            context = {"source": self.name}

        if not server:
            self.emitter.emit(Message("image.classification.request", {"file": file_path}, context))
        else:
            self.emitter.emit(Message("server_request",
                                      {"server_msg_type": "file", "requester": self.name, "message_type": "image.classification.request",
                                       "message_data": {"file": file_path}}, context))

        self.wait("image.classification.result")
        if self.result is None:
            self.result = {}
        return self.result.get("classification", [])

    def get_deep_draw(self, class_num=None, server=True, context=None):
        if context is None:
            context = {"source": self.name}
        msg_type = "class.visualization.request"
        if class_num is None:
            class_num = random.randint(0, 1000)
        msg_data = {"class": class_num}
        if not server:
            self.emitter.emit(Message(msg_type, msg_data, context))
        else:
            self.emitter.emit(Message("server_request",
                                      {"server_msg_type": "file", "requester": self.name,
                                       "message_type": msg_type,
                                       "message_data": msg_data}, context))

        self.wait("class.visualization.result")
        if self.result is None:
            self.result = {"file":None, "url": None, "class_label": class_num, "class_name": None}
        return self.result.get("file", [])


class ImageRecognitionService():
    def __init__(self, emitter, timeout=120, logger=None, server=False):
        self.emitter = emitter
        self.waiting = False
        self.server = server
        self.image_classification_result = {"classification":"unknown"}
        self.image_visualization_result = {"url": None}
        self.timeout = timeout
        if logger is not None:
            self.logger = logger
        else:
            self.logger = getLogger("ImageRecognitionService")
        self.emitter.on("image_classification_result", self.end_wait)
        self.emitter.on("class_visualization_result", self.end_wait)

    def end_wait(self, message):
        if message.type == "image_classification_result":
            self.logger.info("image classification result received")
            self.image_classification_result = message.data
        elif message.type == "image_visualization_result":
            self.logger.info("image visualization result received")
            self.image_visualization_result = message.data
        self.waiting = False

    def wait(self):
        start = time.time()
        elapsed = 0
        self.waiting = True
        while self.waiting and elapsed < self.timeout:
            elapsed = time.time() - start
            time.sleep(0.1)

    def local_deepdraw(self, label_num, context=None):
        message_type = "class_visualization_request"
        message_data = {"class": label_num}
        self.emitter.emit(Message(message_type, message_data, context))
        t = self.timeout
        self.timeout = 250 #shit takes long
        self.wait()
        self.timeout = t
        result = self.image_visualization_result["url"]
        return result

    def server_deepdraw(self, label_num, context=None):
        if context is None:
            context = {}
        requester = context.get("destinatary", "all")
        message_type = "class_visualization_request"
        message_data = {"class": label_num}
        self.emitter.emit(Message("server_request",
                                  {"server_msg_type": "result", "requester": requester, "message_type": message_type,
                                   "message_data": message_data}, context))

        t = self.timeout
        self.timeout = 250  # shit takes long
        self.wait()
        self.timeout = t
        result = self.image_visualization_result["url"]
        return result

    def local_image_classification(self, picture_path, context=None):
        message_type = "image_classification_request"
        message_data = {"file": picture_path}
        self.emitter.emit(Message(message_type, message_data, context))
        self.wait()
        result = self.image_classification_result["classification"]
        return result

    def server_image_classification(self, picture_path, context=None):
        if context is None:
            context = {}
        requester = context.get("destinatary", "all")
        message_type = "image_classification_request"
        message_data = {"file": picture_path}
        self.emitter.emit(Message("server_request", {"server_msg_type":"file", "requester":requester, "message_type": message_type, "message_data": message_data},context))
        self.wait()
        result = self.image_classification_result["classification"]
        return result


class ImageRecognitionSkill(MycroftSkill):

    def __init__(self):
        super(ImageRecognitionSkill, self).__init__(name="ImageRecognitionSkill")
        self.reload_skill = False
        # load caffe
        try:
            self.path = self.config["caffe_path"]
        except:
            self.path = "../caffe"

        sys.path.insert(0, self.path + '/python')

        from caffe.io import load_image
        self.load_image = load_image
        # load model
        try:
            self.model = self.config["caffe_model"]
        except:
            self.model = "bvlc_googlenet"

        # output to text
        self.label_mapping = np.loadtxt(dirname(__file__) + "/synset_words.txt", str, delimiter='\t')

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

        self.save_path = dirname(__file__) + "/deepdraw/"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def initialize(self):
        self.emitter.on("image.classification.request", self.handle_classify)
        self.emitter.on("class.visualization.request", self.handle_deep_draw)
        self.emitter.on("class.visualization.result", self.handle_deep_draw_result)

        image_recog_status_intent = IntentBuilder("ImageClassfyStatusIntent") \
            .require("imgstatus").build()
        self.register_intent(image_recog_status_intent,
                             self.handle_img_recog_intent)

        deep_draw_about_intent = IntentBuilder("DeepDrawIntent") \
            .require("deepdraw").optionally("NetClass").build()
        self.register_intent(deep_draw_about_intent,
                             self.handle_deep_draw_about_intent)

    def make_pretty(self, imagenet_class_name):
        imagenet_class_name = imagenet_class_name.split(" ")[1:]
        r = ""
        for word in imagenet_class_name:
            r += word + " "
        return r[:-1].split(",")[0]

    def handle_img_recog_intent(self, message):
        self.speak_dialog("imgrecogstatus")
        dest = message.context.get("destinatary", "all")
        classifier = ImageRecognitionService(self.emitter)
        results = classifier.local_image_classification(dirname(__file__)+"/obama.jpg", self.context)
        i = 0
        for result in list(results):
            results[i] = self.make_pretty(result)
            i += 1
        self.context["destinatary"] = dest
        self.speak("in test image i see " + results[0] + ", or maybe it is " + results[1])

    def handle_deep_draw_intent(self, message):
        imagenet_class = random.randint(0, len(self.label_mapping))
        classifier = ImageRecognitionService(self.emitter)
        classifier.local_deepdraw(imagenet_class, self.context)

    def handle_deep_draw_about_intent(self, message):
        about = message.data.get("NetClass")
        imagenet_class = -1
        if about is None:
            imagenet_class = random.randint(0, len(self.label_mapping))
        elif about.isdigit():
            if int(about) > 0 and int(about) < len(self.label_mapping):
                imagenet_class = about
            else:
                imagenet_class = random.randint(0, len(self.label_mapping))
        else:
            best = 0
            i = 0
            for image_class in self.label_mapping:
                rating = fuzz.ratio(about,
                                    self.make_pretty(image_class))
                if rating > best:
                    best = rating
                    imagenet_class = i
                if about in image_class:
                    best = best + 15
                    imagenet_class = i
                i += 1
        classifier = ImageRecognitionService(self.emitter)
        classifier.local_deepdraw(imagenet_class, self.context)

    def handle_classify(self, message):
        pic = message.data.get("file")
        user_id = message.context.get("source", "unknown")
        if ":" not in user_id and ":" in message.context.get("destinatary", "unknown"):
            user_id =message.context.get("destinatary")
        elif user_id == "unknown":
            self.log.warning("no user/destinatary specified")

        self.log.info("loading image: " + pic)
        try:
            input_image = self.load_image(pic)
        except Exception as e:
            self.log.error(e)
            self.speak("an error occured loading image to classify")
            return

        self.log.info("predicting")
        result = []
        # make net
        import caffe
        path = self.path + '/models/' + self.model
        net = caffe.Classifier(path + '/deploy.prototxt', path + '/' + self.model + '.caffemodel',
                                    mean=np.load(self.path + '/python/caffe/imagenet/ilsvrc_2012_mean.npy').mean(
                                        1).mean(1),
                                    channel_swap=(2, 1, 0),
                                    raw_scale=255,
                                    image_dims=(224, 224))

        try:
            prediction = net.predict([input_image])
            ind = prediction[0].argsort()[-5:][::-1]  # top-5 predictions
            for i in ind:
                result.append(self.label_mapping[i])
        except Exception as e:
            self.log.error(e)

        self.log.info(result)

        # send result
        msg_type = "image.classification.result"
        msg_data = {"classification": result}
        self.context["destinatary"] = user_id
        # to source socket
        if ":" in user_id:
            if user_id.split(":")[1].isdigit():
                self.emitter.emit(Message("message_request",
                                          {"data":msg_data,
                                           "type": msg_type, "context": self.context}, self.context))
        # to bus
        self.emitter.emit(Message(msg_type,
                                  msg_data, self.context))

    def handle_deep_draw(self, message):
        # deep draw, these octaves determine gradient ascent steps
        octaves = [
            {
                'layer': 'loss3/classifier',
                'iter_n': 190,
                'start_sigma': 2.5,
                'end_sigma': 0.78,
                'start_step_size': 11.,
                'end_step_size': 11.
            },
            {
                'layer': 'loss3/classifier',
                'scale': 1.2,
                'iter_n': 150,
                'start_sigma': 0.78 * 1.2,
                'end_sigma': 0.78,
                'start_step_size': 6.,
                'end_step_size': 6.
            },
            {
                'layer': 'loss2/classifier',
                'scale': 1.2,
                'iter_n': 150,
                'start_sigma': 0.78 * 1.2,
                'end_sigma': 0.44,
                'start_step_size': 6.,
                'end_step_size': 3.
            },
            {
                'layer': 'loss1/classifier',
                'iter_n': 10,
                'start_sigma': 0.44,
                'end_sigma': 0.304,
                'start_step_size': 3.,
                'end_step_size': 3.
            }
        ]

        user_id = message.context.get("destinatary")
        imagenet_class = message.data.get("class", 13)
        # set target of result
        if user_id is not None:
            if user_id == "unknown":
                user_id = "all"

        else:
            self.log.warning("no user/target specified")
            user_id = "all"

        if imagenet_class < 0 or imagenet_class > 1000:
            imagenet_class = random.randint(0, 1000)

        result = self.label_mapping[imagenet_class]
        name = self.make_pretty(result)
        self.speak_dialog("waitdeepdraw", data={"class_name": name})
        # make net
        net_fn = dirname(__file__) + '/deploy_googlenet_updated.prototxt'
        param_fn = self.path + '/models/' + self.model + '/' + self.model + '.caffemodel'
        mean = np.float32([104.0, 117.0, 123.0])
        net = caffe.Classifier(net_fn, param_fn,
                               mean=mean,  # ImageNet mean, training set dependent
                               channel_swap=(2, 1, 0))  # the reference model has channels in BGR order instead of RGB
        # get original input size of network
        original_w = net.blobs['data'].width
        original_h = net.blobs['data'].height

        # the background color of the initial image
        # TODO make configurable
        background_color = np.float32([200.0, 200.0, 200.0])
        # generate initial random image
        gen_image = np.random.normal(background_color, 8, (original_w, original_h, 3))

        # generate class visualization via octavewise gradient ascent
        gen_image = deepdraw(net, gen_image, octaves, focus=imagenet_class,
                             random_crop=True, visualize=False, logger=self.log)

        # save image
        path = self.save_path + str(imagenet_class)+'.png'
        self.log.info("saving image to " + path)
        PIL.Image.fromarray(np.uint8(gen_image)).save(path)

        # upload pic
        data = self.client.upload_from_path(path)
        link = data["link"]
        # send result
        msg_type = "class.visualization.result"
        msg_data = {"file":path, "url": link, "class_label": imagenet_class, "class_name": name}
        # to source socket
        self.context["destinatary"] = user_id
        try:
            if user_id.split(":")[1].isdigit():
                self.emitter.emit(Message("message_request",
                                          {"data": msg_data,
                                           "type": msg_type, "context": self.context}, self.context))
        except:
            # if try fails it wasnt from a socket
            pass
        # to bus
        self.emitter.emit(Message(msg_type,
                                  msg_data, self.context))

    def handle_deep_draw_result(self, message):
        link = message.data.get("url")
        class_label = message.data.get("class_label")
        class_name = message.data.get("class_name")
        self.speak("Here is how i visualize " + class_name,
                          metadata={"url": link, "class_label": class_label,
                                    "class_name": class_name}, context=message.context)

    def stop(self):
        pass


def create_skill():
    return ImageRecognitionSkill()


# deep draw https://github.com/auduno/deepdraw
def preprocess(net, img):
    return np.float32(np.rollaxis(img, 2)[::-1]) - net.transformer.mean['data']


def deprocess(net, img):
    return np.dstack((img + net.transformer.mean['data'])[::-1])


def blur(img, sigma):
    if sigma > 0:
        img[0] = nd.filters.gaussian_filter(img[0], sigma, order=0)
        img[1] = nd.filters.gaussian_filter(img[1], sigma, order=0)
        img[2] = nd.filters.gaussian_filter(img[2], sigma, order=0)
    return img


def make_step(net, step_size=1.5, end='inception_4c/output', clip=True, focus=None, sigma=None):
    '''Basic gradient ascent step.'''

    src = net.blobs['data']  # input image is stored in Net's 'data' blob

    try:
        dst = net.blobs[end]
    except Exception as e:
        print "invalid layer: " + str(e)
        return
    net.forward(end=end)

    one_hot = np.zeros_like(dst.data)
    one_hot.flat[focus] = 1.
    dst.diff[:] = one_hot

    net.backward(start=end)
    g = src.diff[0]

    src.data[:] += step_size / np.abs(g).mean() * g

    if clip:
        bias = net.transformer.mean['data']
        src.data[:] = np.clip(src.data, -bias, 255 - bias)

    src.data[0] = blur(src.data[0], sigma)

    # reset objective for next step
    dst.diff.fill(0.)


def deepdraw(net, base_img, octaves, random_crop=True, visualize=False, focus=None,
             clip=True, logger=None, verbose=False, **step_params):
    # prepare base image
    if logger is not None:
        logger.info("pre-processing")
    image = preprocess(net, base_img)  # (3,224,224)

    # get input dimensions from net
    w = net.blobs['data'].width
    h = net.blobs['data'].height

    if logger is not None:
        logger.info("starting deep drawing")
    src = net.blobs['data']
    src.reshape(1, 3, h, w)  # resize the network's input image size
    for e, o in enumerate(octaves):
        if 'scale' in o:
            # resize by o['scale'] if it exists
            image = nd.zoom(image, (1, o['scale'], o['scale']))
        _, imw, imh = image.shape

        # select layer
        layer = o['layer']

        for i in xrange(o['iter_n']):
            if imw > w:
                if random_crop:
                    # randomly select a crop
                    # ox = random.randint(0,imw-224)
                    # oy = random.randint(0,imh-224)
                    mid_x = (imw - w) / 2.
                    width_x = imw - w
                    ox = np.random.normal(mid_x, width_x * 0.3, 1)
                    ox = int(np.clip(ox, 0, imw - w))
                    mid_y = (imh - h) / 2.
                    width_y = imh - h
                    oy = np.random.normal(mid_y, width_y * 0.3, 1)
                    oy = int(np.clip(oy, 0, imh - h))
                    # insert the crop into src.data[0]
                    src.data[0] = image[:, ox:ox + w, oy:oy + h]
                else:
                    ox = (imw - w) / 2.
                    oy = (imh - h) / 2.
                    src.data[0] = image[:, ox:ox + w, oy:oy + h]
            else:
                ox = 0
                oy = 0
                src.data[0] = image.copy()

            sigma = o['start_sigma'] + ((o['end_sigma'] - o['start_sigma']) * i) / o['iter_n']
            step_size = o['start_step_size'] + ((o['end_step_size'] - o['start_step_size']) * i) / o['iter_n']

            try:
                if verbose:
                    if logger is not None:
                        logger.info("making step " + str(i) + " for octave " + str(e) + " layer " + layer)
                make_step(net, end=layer, clip=clip, focus=focus,
                      sigma=sigma, step_size=step_size)
            except Exception as e:
                if logger is not None:
                    logger.error('error making step: ' + str(i) + " error: " + str(e))

            if i % 10 == 0:
                if logger is not None:
                    logger.info('finished step %d in octave %d' % (i, e))

            # insert modified image back into original image (if necessary)
            image[:, ox:ox + w, oy:oy + h] = src.data[0]

    if logger is not None:
        logger.info("deprocessing image")

    # returning the resulting image
    return deprocess(net, image)
