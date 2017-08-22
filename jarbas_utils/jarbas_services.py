from time import sleep, time, asctime
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message
import urllib, random
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

    def send_request(self, message_type, message_data=None, message_context=None, cipher="aes", server=False, client=False):
        """
          send message
        """
        file_fields = ["file", "path", "dream_source", "file_path", "pic_path"]
        if message_data is None:
            message_data = {}
        if message_context is None:
            message_context = {"source": self.name, "waiting_for": self.waiting_messages}
        data = {"requester": self.name,
                "message_type": message_type,
                "message_data": message_data, "cipher": cipher}

        type = "bus"
        for field in file_fields:
            if field in message_data.keys():
                type = "file"
                message_data["file"] = message_data[field]
                break
        data["request_type"] = type

        if not server:
            if not client:
                self.emitter.emit(Message(message_type, message_data, message_context))
            else:

                self.emitter.emit(Message("message_request",
                                         data, message_context))
        else:
            self.emitter.emit(Message("server_request",
                                      data, message_context))

    def wait(self, waiting_for="any"):
        """
            wait until result response or time_out
            waiting_for: message that ends wait, by default use any of waiting_messages list
            returns True if result received, False on timeout
        """
        self.waiting_for = waiting_for
        self.result = None
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


class Colorization(ServiceBackend):
    def __init__(self, emitter=None, timeout=10,
                 waiting_messages=["colorization.result"],
                 logger=None):
        super(Colorization, self).__init__(name="Colorization",
                                         emitter=emitter,
                                         timeout=timeout,
                                         waiting_messages=waiting_messages,
                                         logger=logger)

    def colorize(self, picture_path, context=None):
        self.send_request("colorization.request", {"picture_path":
                                                           picture_path},
                          message_context=context)
        self.wait("colorization.result")
        return file

    def colorize_from_url(self, picture_url, context=None):
        picture_path = url_to_pic(picture_url)
        self.send_request("colorization.request", {"picture_path":
                                                           picture_path},
                          message_context=context)
        self.wait("colorization.result")
        return file


class PornDetect(ServiceBackend):
    def __init__(self, emitter=None, timeout=10,
                 waiting_messages=["porn.recognition.result"],
                 logger=None):
        super(PornDetect, self).__init__(name="PornDetect",
                                         emitter=emitter,
                                         timeout=timeout,
                                         waiting_messages=waiting_messages,
                                         logger=logger)

    def is_porn(self, picture_path, context=None):
        self.send_request("porn.recognition.request", {"picture_path":
                                                           picture_path},
                          message_context=context)
        self.wait("porn.recognition.result")
        return self.result.get("predictions")

    def is_porn_from_url(self, picture_url, context=None):
        picture_path = url_to_pic(picture_url)
        self.send_request("porn.recognition.request", {"picture_path":
                                                           picture_path},
                          message_context=context)
        self.wait("porn.recognition.result")
        return self.result.get("predictions")


class LILACSstorageService(ServiceBackend):
    def __init__(self, emitter=None, timeout=10, waiting_messages=None,
                 logger=None):
        super(LILACSstorageService, self).__init__(name="LILACSstorageService",
                                       emitter=emitter, timeout=timeout,
                                                   waiting_messages=waiting_messages, logger=logger)

    def save(self, node_dict):
        self.send_request("LILACS.node.json.save.request", {"node": node_dict})
        self.wait("LILACS.node.json.save.result")
        self.logger.info("saved node: " + node_dict["name"])
        return self.result

    def load(self, node_name):
        self.send_request("LILACS.node.json.load.request", {"node": node_name})
        self.wait("LILACS.node.json.load.result")
        return self.result

    def process_result(self):
        """
         process and return only desired data
         """
        if self.result is None:
            self.result = {}
        # dont load empty connections
        for key in dict(self.result):
            data = self.result[key]
            if data == {}:
                self.result.pop(key)
        return self.result


class KnowledgeService(ServiceBackend):
    def __init__(self, emitter=None, timeout=15, waiting_messages=None,
                 logger=None):
        super(KnowledgeService, self).__init__(name="KnowledgeService",
                                       emitter=emitter, timeout=timeout,
                                                   waiting_messages=waiting_messages, logger=logger)

    def adquire(self, subject, where="wolfram"):
        if "wikipedia" in where:
            return self.ask_wikipedia(subject)
        if "wikidata" in where:
            return self.ask_wikidata(subject)
        if "dbpedia" in where:
            return self.ask_dbpedia(subject)
        if "wordnik" in where:
            return self.ask_wordnik(subject)
        if "wikihow" in where:
            return self.ask_wikihow(subject)
        if "wolfram" in where:
            return self.ask_wolfram(subject)
        if "concept" in where:
            return self.ask_conceptnet(subject)

    def ask_wikipedia(self, subject):
        self.send_request("wikipedia.request", {"TargetKeyword": subject})
        self.wait("wikipedia.result")
        return self.result

    def ask_wikidata(self, subject):
        self.send_request("wikidata.request", {"TargetKeyword": subject})
        self.wait("wikidata.result")
        return self.result

    def ask_dbpedia(self, subject):
        self.send_request("dbpedia.request", {"TargetKeywordt": subject})
        self.wait("dbpedia.result")
        return self.result

    def ask_wolfram(self, subject):
        self.send_request("wolframalpha.request", {"TargetKeyword": subject})
        self.wait("wolframalpha.result")
        return self.result

    def ask_wikihow(self, subject):
        self.send_request("wikihow.request", {"TargetKeyword": subject})
        self.wait("wikihow.result")
        return self.result

    def ask_conceptnet(self, subject):
        self.send_request("conceptnet.request", {"TargetKeyword": subject})
        self.wait("conceptnet.result")
        return self.result

    def ask_wordnik(self, subject):
        self.send_request("wordnik.request", {"TargetKeyword": subject})
        self.wait("wordnik.result")
        return self.result


class UserManagerService(ServiceBackend):
    def __init__(self, emitter=None, timeout=125, waiting_messages=None, logger=None):
        super(UserManagerService, self).__init__(name="UserManagerService", emitter=emitter, timeout=timeout,
                                                   waiting_messages=waiting_messages, logger=logger)

    def user_from_sock(self, sock_num):
        self.send_request(message_type="user.from_sock.request",
                          message_data={"sock": sock_num})
        self.wait("user.from_sock.result")
        return self.result

    def user_from_facebook_id(self, fb_id):
        self.send_request(message_type="user.from_facebook.request",
                          message_data={"id": fb_id})
        self.wait("user.from_facebook.result")
        return self.result

    def user_from_id(self, user_id):
        self.send_request(message_type="user.from_id.request",
                          message_data={"id": user_id})
        self.wait("user.from_id.result")
        if "error" in self.result.keys():
            self.logger.error(self.result["error"])
            return None
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
        timeout = self.timeout
        self.timeout = 60 * 40 # 40 mins?
        self.send_request(message_type="class.visualization.request",
                          message_data={"class": class_num},
                          message_context=context,
                          server=server)
        self.wait("class.visualization.result")
        self.timeout = timeout
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
    def __init__(self, emitter=None, timeout=100, waiting_messages=None, logger=None):
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

    def dream_from_file(self, picture_path, name=None, iter=20, categorie=None, context=None, server=False):
        if name is None:
            name = asctime().replace(" ","_")
        self.send_request(message_type="deep.dream.request",
                          message_data={"dream_source": picture_path, "dream_name": name, "num_iter": iter, "categorie":categorie},
                          message_context=context,
                          server=server)
        self.wait("deep.dream.result")
        return self.result.get("file")

    def dream_from_url(self, picture_url, name=None, iter=20, categorie=None, context=None, server=False):
        if name is None:
            name = asctime().replace(" ","_")
        self.send_request(message_type="deep.dream.request",
                          message_data={"dream_source": url_to_pic(picture_url), "dream_name": name, "num_iter": iter, "categorie":categorie},
                          message_context=context,
                          server=server)
        self.wait("deep.dream.result")
        return self.result.get("file")


class StyleTransferService(ServiceBackend):
    def __init__(self, emitter=None, timeout=900, waiting_messages=None, logger=None):
        super(StyleTransferService, self).__init__(name="StyleTransferService", emitter=emitter, timeout=timeout,
                                                   waiting_messages=waiting_messages, logger=logger)

    def transfer_from_file(self, picture_path, styles_path, name=None,
                           iter=350, context=None, server=False):
        if name is None:
            name = asctime().replace(" ", "_")
        self.send_request(message_type="style.transfer.request",
                          message_data={"style_img": styles_path,
                                        "target_img": picture_path, "name": name, "num_iter": iter},
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


