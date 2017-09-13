from time import asctime
import urllib
from os.path import dirname
from jarbas_utils.skill_dev_tools import QueryBackend

__author__ = 'jarbas'


def url_to_pic(url):
    saved_url = dirname(__file__) + "/temp.jpg"
    f = open(saved_url, 'wb')
    f.write(urllib.urlopen(url).read())
    f.close()
    return saved_url


class ServerFallbackQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=35, logger=None,
                 server=False, client=False, override=True):
        super(ServerFallbackQuery, self).__init__(name=name, emitter=emitter,
                                                  timeout=timeout,
                                                  logger=logger,
                                                  server=server,
                                                  client=client,
                                                  override=override)

    def wait_server_response(self, data=None, context=None):
        if data is None:
            data = {}
        if context is None:
            context = {}
        self.query = None
        result = self.send_request(message_type="server.intent_failure",
                                 message_data=data,
                                 message_context=context,
                                 response_messages=[
                                     "server.message.received"])
        if self.query.get_response_type() == "server.message.received":
            return True
        return False


class PadatiousFallbackQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=35, logger=None,
                 server=False, client=False, override=True):
        super(PadatiousFallbackQuery, self).__init__(name=name,
                                                     emitter=emitter,
                                                     timeout=timeout,
                                                     logger=logger,
                                                     server=server,
                                                     client=client,
                                                     override=override)

    def get_padatious_response(self, data=None, context=None):
        if data is None:
            data = {}
        result = self.send_request(message_type="padatious:fallback.request",
                                   message_data=data, message_context=context)
        return result.get("success", False)


class RBMQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=100, logger=None,
                 server=False, client=False, override=True):
        super(RBMQuery, self).__init__(name=name, emitter=emitter,
                                       timeout=timeout,
                                       logger=logger,
                                       server=server, client=client,
                                       override=override)

    def sample(self, model="random", sample_num=3, context=None):
        result = self.send_request("RBM.request",
                                   {"model": model, "sample_num": sample_num},
                                   message_context=context)
        result = result.get("samples")
        return result


class ColorizationQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=60 * 15, logger=None,
                 server=False, client=False, override=True):
        super(ColorizationQuery, self).__init__(name=name, emitter=emitter,
                                                timeout=timeout,
                                                logger=logger,
                                                server=server, client=client,
                                                override=override)

    def colorize(self, picture_path, context=None):
        result = self.send_request("colorization.request",
                                   {"picture_path": picture_path},
                                   message_context=context)
        return result

    def colorize_from_url(self, picture_url, context=None):
        picture_path = url_to_pic(picture_url)
        result = self.send_request("colorization.request",
                                   {"picture_path": picture_path},
                                   message_context=context)
        return result


class PornDetectQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=300, logger=None,
                 server=False, client=False, override=True):
        super(PornDetectQuery, self).__init__(name=name, emitter=emitter,
                                              timeout=timeout,
                                              logger=logger,
                                              server=server, client=client,
                                              override=override)

    def is_porn(self, picture_path, context=None):
        return self.send_request("porn.recognition.request",
                                 {"picture_path": picture_path},
                                 message_context=context)

    def is_porn_from_url(self, picture_url, context=None):
        picture_path = url_to_pic(picture_url)
        return self.send_request("porn.recognition.request",
                                 {"picture_path": picture_path},
                                 message_context=context)


class LILACSstorageQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=35, logger=None,
                 server=False, client=False, override=True):
        super(LILACSstorageQuery, self).__init__(name=name, emitter=emitter,
                                                 timeout=timeout,
                                                 logger=logger,
                                                 server=server, client=client,
                                                 override=override)

    def save(self, node_dict):
        result = self.send_request("LILACS.node.json.save.request",
                                   {"node": node_dict})
        self.logger.info("saved node: " + node_dict["name"])
        return self.process_result(result)

    def load(self, node_name):
        result = self.send_request("LILACS.node.json.load.request", {"node":
                                                                         node_name})
        return self.process_result(result)

    def process_result(self, result):
        """
         process and return only desired data
         """
        if result is None:
            result = {}
        # dont load empty connections
        for key in dict(result):
            data = result[key]
            if data == {}:
                result.pop(key)
        return result


class KnowledgeQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=120, logger=None,
                 server=False, client=False, override=True):
        super(KnowledgeQuery, self).__init__(name=name, emitter=emitter,
                                             timeout=timeout,
                                             logger=logger,
                                             server=server, client=client,
                                             override=override)

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
        return self.send_request("wikipedia.request", {"TargetKeyword":
                                                           subject})

    def ask_wikidata(self, subject):
        return self.send_request("wikidata.request",
                                 {"TargetKeyword": subject})

    def ask_dbpedia(self, subject):
        return self.send_request("dbpedia.request",
                                 {"TargetKeywordt": subject})

    def ask_wolfram(self, subject):
        return self.send_request("wolframalpha.request", {"TargetKeyword":
                                                              subject})

    def ask_wikihow(self, subject):
        return self.send_request("wikihow.request",
                                 {"TargetKeyword": subject})

    def ask_conceptnet(self, subject):
        return self.send_request("conceptnet.request", {"TargetKeyword":
                                                            subject})

    def ask_wordnik(self, subject):
        return self.send_request("wordnik.request",
                                 {"TargetKeyword": subject})


class UserManagerQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=35, logger=None,
                 server=False, client=False, override=True):
        super(UserManagerQuery, self).__init__(name=name, emitter=emitter,
                                               timeout=timeout,
                                               logger=logger,
                                               server=server, client=client,
                                               override=override)

    def user_from_sock(self, sock_num):
        return self.send_request(message_type="user.from_sock.request",
                                 message_data={"sock": sock_num})

    def user_from_facebook_id(self, fb_id):
        return self.send_request(message_type="user.from_facebook.request",
                                 message_data={"id": fb_id})

    def user_from_id(self, user_id):
        result = self.send_request(message_type="user.from_id.request",
                                   message_data={"id": user_id})
        if "error" in result.keys():
            self.logger.error(result["error"])
            return None
        return result


class FaceRecognitionQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=60 * 15, logger=None,
                 server=False, client=False, override=True):
        super(FaceRecognitionQuery, self).__init__(name=name, emitter=emitter,
                                                   timeout=timeout,
                                                   logger=logger,
                                                   server=server,
                                                   client=client,
                                                   override=override)

    def face_recognition_from_file(self, picture_path, context=None):
        result = self.send_request(message_type="face.recognition.request",
                                   message_data={"file": picture_path},
                                   message_context=context)
        return result.get("result", "unknown person")

    def face_recognition_from_url(self, url, context=None):
        result = self.send_request(message_type="face.recognition.request",
                                   message_data={"file": url_to_pic(url)},
                                   message_context=context)
        return result.get("result", "unknown person")


class ImageRecognitionQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=60 * 15, logger=None,
                 server=False, client=False, override=True):
        super(ImageRecognitionQuery, self).__init__(name=name,
                                                    emitter=emitter,
                                                    timeout=timeout,
                                                    logger=logger,
                                                    server=server,
                                                    client=client,
                                                    override=override)

    def get_classification(self, file_path, context=None):
        result = self.send_request(
            message_type="image.classification.request",
            message_data={"file": file_path},
            message_context=context)
        return result.get("classification", [])


class WebcamQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=35, logger=None,
                 server=False, client=False, override=True):
        super(WebcamQuery, self).__init__(name=name, emitter=emitter,
                                          timeout=timeout,
                                          logger=logger,
                                          server=server, client=client,
                                          override=override)

    def get_feed(self, context=None, server=False):
        result = self.send_request("vision.feed.request", {}, context)
        return result.get("file")

    def get_data(self, context=None, server=False):
        result = self.send_request("vision_request", {}, context)
        return result

    def get_faces(self, file=None, context=None, server=False):
        result = self.send_request("vision.faces.request", {"file": file},
                                   context)
        return result.get("faces", [])


class ObjectRecognitionQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=60 * 15, logger=None,
                 server=False, client=False, override=True):
        super(ObjectRecognitionQuery, self).__init__(name=name,
                                                     emitter=emitter,
                                                     timeout=timeout,
                                                     logger=logger,
                                                     server=server,
                                                     client=client,
                                                     override=override)

    def recognize_objects(self, picture_path, context=None):
        return self.send_request("object.recognition.request", {"file":
                                                                    picture_path},
                                 context)

    def recognize_objects_from_url(self, picture_url, context=None):
        return self.send_request("object.recognition.request", {"url":
                                                                    picture_url},
                                 context)


class DeepDreamQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=60 * 15, logger=None,
                 server=False, client=False, override=True):
        super(DeepDreamQuery, self).__init__(name=name, emitter=emitter,
                                             timeout=timeout,
                                             logger=logger,
                                             server=server, client=client,
                                             override=override)

    def dream_from_file(self, picture_path, name=None, iter=20,
                        categorie=None,
                        context=None):
        if name is None:
            name = asctime().replace(" ", "_")
        result = self.send_request(message_type="deep.dream.request",
                                   message_data={"dream_source": picture_path,
                                                 "dream_name": name,
                                                 "num_iter": iter,
                                                 "categorie": categorie},
                                   message_context=context)
        return result.get("file")

    def dream_from_url(self, picture_url, name=None, iter=20, categorie=None,
                       context=None):
        if name is None:
            name = asctime().replace(" ", "_")
        result = self.send_request(message_type="deep.dream.request",
                                   message_data={
                                       "dream_source": url_to_pic(
                                           picture_url),
                                       "dream_name": name, "num_iter": iter,
                                       "categorie": categorie},
                                   message_context=context)
        return result.get("file")


class StyleTransferQuery(QueryBackend):
    def __init__(self, name=None, emitter=None, timeout=60 * 60 * 3,
                 logger=None,
                 server=False, client=False, override=True):
        super(StyleTransferQuery, self).__init__(name=name, emitter=emitter,
                                                 timeout=timeout,
                                                 logger=logger,
                                                 server=server, client=client,
                                                 override=override)

    def transfer_from_file(self, picture_path, styles_path, name=None,
                           iter=350, context=None):
        if name is None:
            name = asctime().replace(" ", "_")
        result = self.send_request(message_type="style.transfer.request",
                                   message_data={"style_img": styles_path,
                                                 "target_img": picture_path,
                                                 "name": name,
                                                 "num_iter": iter},
                                   message_context=context)
        return result.get("file")

    def transfer_from_url(self, picture_url, style_url, name=None, iter=350,
                          context=None):
        if name is None:
            name = asctime().replace(" ", "_")
        result = self.send_request(message_type="style.transfer.request",
                                   message_data={
                                       "style_img": url_to_pic(style_url),
                                       "target_img": url_to_pic(picture_url),
                                       "name": name, "num_iter": iter},
                                   message_context=context)
        return result.get("file")
