# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import time, urllib
from mycroft.messagebus.message import Message
from os.path import dirname

__author__ = 'jarbas'

logger = getLogger(__name__)


class UserIdService():
    def __init__(self, emitter, timeout=20, logger=None, server=False):
        self.emitter = emitter
        self.waiting = False
        self.server = server
        self.face_recog_result = None
        self.vision_result = None
        self.timeout = timeout
        if logger is not None:
            self.logger = logger
        else:
            self.logger = getLogger("User_ID")
        self.emitter.on("vision_result", self.end_wait)
        self.emitter.on("face_recognition_result", self.end_wait)

    def end_wait(self, message):
        # TODO implemnt all wait cases
        if message.type == "face_recognition_result":
            self.logger.info("face recognition result received")
            self.face_recog_result = message.data["result"]
        if message.type == "vision_result":
            self.logger.info("vision result received")
            self.vision_result = message.data
        self.waiting = False

    def wait(self):
        start = time.time()
        elapsed = 0
        self.waiting = True
        while self.waiting and elapsed < self.timeout:
            elapsed = time.time() - start
            time.sleep(0.1)

    def local_face_recog(self, picture_path, user_id):
        requester = user_id
        message_type = "face_recognition_request"
        context = {"destinatary": user_id}
        message_data = {"file": picture_path, "source": requester, "user":"unknown"}
        self.emitter.emit(Message(message_type, message_data, context))
        self.wait()
        result = self.face_recog_result
        return result

    def server_face_recog(self, picture_path, user_id):
        requester = user_id
        message_type = "face_recognition_request"
        message_data = {"file": picture_path, "source": requester}
        context = {"destinatary": user_id}
        self.emitter.emit(Message("server_request", {"server_msg_type":"file", "requester":requester, "message_type": message_type, "message_data": message_data}, context))
        self.wait()
        result = self.face_recog_result
        return result

    def request_vision_id(self, user_id):
        self.logger.info("Vision Recognition requested")
        self.vision_result = None
        self.face_recog_result = None
        if self.server:
            # TODO request vision result from client
            # request vision service for feed
            self.logger.info("Requesting client vision service")
            self.emitter.emit(Message("message_request", {"user_id": user_id, "type": "vision_request", "data": {}}))
            self.wait()
            if self.vision_result is None:
                self.logger.info("No vision result received for " + str(self.timeout) + " seconds, aborting")
                return None
            if self.vision_result["num_persons"] == 0:
                self.logger.info("No persons detected")
                return None
            self.logger.info("Requesting local face recognition service")
            return self.local_face_recog(self.vision_result["feed_path"], user_id)

        else:
            # request vision service for feed
            self.logger.info("Requesting local vision service")
            self.emitter.emit(Message("vision_request", {}))
            self.wait()
            if self.vision_result["num_persons"] == 0:
                self.logger.info("No persons detected")
                return None
            self.logger.info("Requesting face recognition from server")
            return self.server_face_recog(self.vision_result["feed_path"], user_id)

    def face_recog_from_url(self, url, user_id):
        self.logger.info("URL Face Recognition requested")
        self.vision_result = None
        self.face_recog_result = None
        if self.server:
            self.logger.info("Requesting local face recognition service")
            saved_url = dirname(__file__)+"/temp.jpg"
            f = open(saved_url, 'wb')
            f.write(urllib.urlopen(url).read())
            f.close()
            return self.local_face_recog(saved_url, user_id)

        else:
            self.logger.info("Requesting face recognition from server")
            saved_url = dirname(__file__) + "/temp.jpg"
            f = open(saved_url, 'wb')
            f.write(urllib.urlopen(url).read())
            f.close()
            return self.server_face_recog(saved_url, user_id)

    def request_bluetooth_id(self, user_id):
        self.logger.error("Bluetooth recognition requested but not implemented")
        return None

    def request_voice_print_id(self, user_id):
        self.logger.error("Voice recognition requested but not implemented")
        return None


class UserIdSkill(MycroftSkill):

    def __init__(self):
        super(UserIdSkill, self).__init__(name="User Identification Skill")
        self.server = True
        self.photo = None

    def initialize(self):
        self.emitter.on("recognizer_loop:utterance", self.handle_set_fb_photo)

        who_am_i_intent = IntentBuilder("WhoAmIIntent")\
            .require("WhoAmIKeyword").build()
        self.register_intent(who_am_i_intent,
                             self.handle_who_am_i_intent)

        what_am_i_intent = IntentBuilder("WhatAmIIntent") \
            .require("WhatAmIKeyword").build()
        self.register_intent(what_am_i_intent,
                             self.handle_what_am_i_intent)

        self.userid = UserIdService(self.emitter, server=self.server)

    def handle_set_fb_photo(self, message):
        if "fbchat" in message.context.get("source"):
            self.photo = message.context.get("photo")

    def handle_who_am_i_intent(self, message):
        user_id = message.context.get("destinatary")
        user = ""
        if "fbchat" in user_id:
            url = self.photo
            vision_user = self.userid.face_recog_from_url(url, user_id)
        else:
            vision_user = self.userid.request_vision_id(user_id)
        if vision_user is None:
            vision_user = "unknown"
        if vision_user != "unknown":
            user += vision_user + ", according to vision service\n"

        voice_user = self.userid.request_voice_print_id(user_id)
        if voice_user is None:
            voice_user = "unknown"
        if voice_user != "unknown":
            user += voice_user + ", according to voice print service\n"

        bluetooth_user = self.userid.request_bluetooth_id(user_id)
        if bluetooth_user is None:
            bluetooth_user = "unknown"
        if bluetooth_user != "unknown":
            user += bluetooth_user + ", according to bluetooth service\n"

        usr = message.data.get("user", "unknown")
        if usr == "unknown":
            usr = "unknown " + message.context.get("destinatary") + " user"
        user += usr + ", according to source of message\n"
        self.speak_dialog("who.user.is", {"username": user})

    def handle_what_am_i_intent(self, message):
        try:
            # server
            target, sock_num = message.context.get("destinatary").split(":")
        except:
            # non server
            target = message.context.get("destinatary")
            self.log.debug("could not get socket from " + str(target))
        self.speak_dialog("what.user.is", {"usertype": target})

    def stop(self):
        pass


def create_skill():
    return UserIdSkill()
