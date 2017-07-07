from time import sleep, time, asctime
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message
import urllib
from os.path import dirname

__author__ = 'jarbas'


def url_to_pic(url):
    saved_url = dirname(__file__) + "/temp.jpg"
    f = open(saved_url, 'wb')
    f.write(urllib.urlopen(url).read())
    f.close()
    return saved_url


class ServiceBackend(object):
    """
        Base class for all service implementations.

        Args:
            name: name of service (str)
            emitter: eventemitter or websocket object
            timeout: time in seconds to wait for response (int)
            waiting_messages: end wait on any of these messages (list)

    """

    def __init__(self, name, emitter=None, timeout=5, waiting_messages=None, logger=None):
        self.initialize(name, emitter, timeout, waiting_messages, logger)

    def initialize(self, name, emitter, timeout, waiting_messages, logger):
        """
           initialize emitter, register events, initialize internal variables
        """
        self.name = name
        self.emitter = emitter
        self.timeout = timeout
        self.result = None
        self.waiting = False
        self.waiting_for = "any"
        if logger is None:
            self.logger = getLogger(self.name)
        else:
            self.logger = logger
        if waiting_messages is None:
            waiting_messages = []
        self.waiting_messages = waiting_messages
        for msg in waiting_messages:
            self.emitter.on(msg, self.end_wait)
        self.context = {"source": self.name, "waiting_for": self.waiting_messages}

    def send_request(self, message_type, message_data=None, message_context=None, server=False):
        """
          send message
        """
        if message_data is None:
            message_data = {}
        if message_context is None:
            message_context = {"source": self.name, "waiting_for": self.waiting_messages}
        if not server:
            self.emitter.emit(Message(message_type, message_data, message_context))
        else:
            type = "bus"
            if "file" in message_data.keys():
                type = "file"
            self.emitter.emit(Message("server_request",
                                      {"server_msg_type": type, "requester": self.name,
                                       "message_type": message_type,
                                       "message_data": message_data}, message_context))

    def wait(self, waiting_for="any"):
        """
            wait until result response or time_out
            waiting_for: message that ends wait, by default use any of waiting_messages list
            returns True if result received, False on timeout
        """
        self.waiting_for = waiting_for
        if self.waiting_for != "any" and self.waiting_for not in self.waiting_messages:
            self.emitter.on(waiting_for, self.end_wait)
            self.waiting_messages.append(waiting_for)
        self.waiting = True
        start = time()
        elapsed = 0
        while self.waiting and elapsed < self.timeout:
            elapsed = time() - start
            sleep(0.3)
        self.process_result()
        return not self.waiting

    def end_wait(self, message):
        """
            Check if this is the message we were waiting for and save result
        """
        if self.waiting_for == "any" or message.type == self.waiting_for:
            self.result = message.data
            if message.context is None:
                message.context = {}
            self.context.update(message.context)
            self.waiting = False

    def get_result(self):
        """
            return last processed result
        """
        return self.result

    def process_result(self):
        """
         process and return only desired data
         """
        if self.result is None:
            self.result = {}
        return self.result


class FaceRecognitionService(ServiceBackend):
    def __init__(self, emitter=None, timeout=125, waiting_messages=None, logger=None):
        super(FaceRecognitionService, self).__init__(name="FaceRecognitionService", emitter=emitter, timeout=timeout,
                                                   waiting_messages=waiting_messages, logger=logger)

    def face_recognition_from_file(self, picture_path, context=None, server=False):
        self.send_request(message_type="face.recognition.request",
                          message_data={"file": picture_path},
                          message_context=context,
                          server=server)
        self.wait("face.recognition.result")
        return self.result.get("result", "unknown person")

    def face_recognition_from_url(self, url, context=None, server=False):
        self.send_request(message_type="face.recognition.request",
                          message_data={"file": url_to_pic(url)},
                          message_context=context,
                          server=server)
        self.wait("face.recognition.result")
        return self.result.get("result", "unknown person")


class ImageRecogService(ServiceBackend):
    def __init__(self, emitter=None, timeout=125, waiting_messages=None, logger=None):
        super(ImageRecogService, self).__init__(name="ImageRecognitionService", emitter=emitter, timeout=timeout, waiting_messages=waiting_messages, logger=logger)

    def get_classification(self, file_path, server=True, context=None):
        self.send_request(message_type="image.classification.request",
                          message_data={"file": file_path},
                          message_context=context,
                          server=server)
        self.wait("image.classification.result")
        return self.result.get("classification", [])

    def get_deep_draw(self, class_num=None, server=True, context=None):
        if class_num is None:
            class_num = random.randint(0, 1000)
        self.send_request(message_type="class.visualization.request",
                          message_data={"class": class_num},
                          message_context=context,
                          server=server)
        self.wait("class.visualization.result")
        return self.result.get("file", [])


class VisionService(ServiceBackend):
    def __init__(self, emitter=None, timeout=25, waiting_messages=None, logger=None):
        super(VisionService, self).__init__(name="VisionService", emitter=emitter, timeout=timeout, waiting_messages=waiting_messages, logger=logger)

    def get_feed(self, context=None, server=False):
        self.send_request("vision.feed.request", {}, context, server)
        self.wait("vision.feed.result")
        return self.result.get("file")

    def get_data(self, context=None, server=False):
        self.send_request("vision_request", {}, context, server)
        self.wait("vision_result")
        return self.result

    def get_faces(self, file=None, context=None, server=False):
        self.send_request("vision.faces.request", {"file": file}, context, server)
        self.wait("vision.faces.result")
        return self.result.get("faces", [])


class ObjectRecogService(ServiceBackend):
    def __init__(self, emitter=None, timeout=25, waiting_messages=None, logger=None):
        super(ObjectRecogService, self).__init__(name="ObjectRecogService", emitter=emitter, timeout=timeout, waiting_messages=waiting_messages, logger=logger)

    def recognize_objects(self, picture_path, context=None, server=False):
        self.send_request("object.recognition.request", {"file": picture_path}, context, server=server)
        self.wait("object.recognition.result")
        return self.result

    def recognize_objects_from_url(self, picture_url, context=None, server=False):
        self.send_request("object.recognition.request", {"url": picture_url}, context, server=server)
        self.wait("object.recognition.result")
        return self.result


class DreamService(ServiceBackend):
    def __init__(self, emitter=None, timeout=900, waiting_messages=None, logger=None):
        super(DreamService, self).__init__(name="DreamService", emitter=emitter, timeout=timeout,
                                                   waiting_messages=waiting_messages, logger=logger)

    def dream_from_file(self, picture_path, name=None, iter=20, context=None, server=False):
        if name is None:
            name = asctime().replace(" ","_")
        self.send_request(message_type="deep.dream.request",
                          message_data={"dream_source": picture_path, "dream_name": name, "num_iter": iter},
                          message_context=context,
                          server=server)
        self.wait("deep.dream.result")
        return self.result.get("file")

    def dream_from_url(self, picture_url, name=None, iter=20, context=None, server=False):
        if name is None:
            name = asctime().replace(" ","_")
        self.send_request(message_type="deep.dream.request",
                          message_data={"dream_source": url_to_pic(picture_url), "dream_name": name, "num_iter": iter},
                          message_context=context,
                          server=server)
        self.wait("deep.dream.result")
        return self.result.get("file")


class StyleTransferService(ServiceBackend):
    def __init__(self, emitter=None, timeout=900, waiting_messages=None, logger=None):
        super(StyleTransferService, self).__init__(name="StyleTransferService", emitter=emitter, timeout=timeout,
                                                   waiting_messages=waiting_messages, logger=logger)

    def transfer_from_file(self, picture_path, style_path, name=None, iter=350, context=None, server=False):
        if name is None:
            name = asctime().replace(" ", "_")
        self.send_request(message_type="style.transfer.request",
                          message_data={"style_img": style_path, "target_img": picture_path, "name": name, "num_iter": iter},
                          message_context=context,
                          server=server)
        self.wait("style.transfer.result")
        return self.result.get("file")

    def transfer_from_url(self, picture_url, style_url, name=None, iter=350, context=None, server=False):
        if name is None:
            name = asctime().replace(" ", "_")
        self.send_request(message_type="style.transfer.request",
                          message_data={"style_img": url_to_pic(style_url), "target_img": url_to_pic(picture_url), "name": name, "num_iter": iter},
                          message_context=context,
                          server=server)
        self.wait("style.transfer.result")
        return self.result.get("file")


