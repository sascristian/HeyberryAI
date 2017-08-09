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

from jarbas_utils.jarbas_services import FaceRecognitionService, VisionService
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)


class UserIdSkill(MycroftSkill):

    def __init__(self):
        super(UserIdSkill, self).__init__(name="User Identification Skill")
        self.photo = None

    def initialize(self):

        who_am_i_intent = IntentBuilder("WhoAmIIntent")\
            .require("WhoAmIKeyword").build()
        self.register_intent(who_am_i_intent,
                             self.handle_who_am_i_intent)

        what_am_i_intent = IntentBuilder("WhatAmIIntent") \
            .require("WhatAmIKeyword").build()
        self.register_intent(what_am_i_intent,
                             self.handle_what_am_i_intent)

    def handle_who_am_i_intent(self, message):
        user_id = message.context.get("destinatary")
        user = ""
        face_recog = FaceRecognitionService(self.emitter)
        if "fbchat" in user_id:
            url = message.context.get("photo")
            vision_user = face_recog.face_recognition_from_url(url, self.message_context, server=True)
        else:
            vision = VisionService(self.emitter)
            feed = vision.get_feed(self.message_context)
            vision_user = face_recog.face_recognition_from_file(feed, self.message_context, server=True)

        if vision_user is None:
            vision_user = "unknown"
        if vision_user != "unknown":
            user += vision_user + ", according to vision service\n"

        #voice_user = self.userid.request_voice_print_id(user_id)
        #if voice_user is None:
        #    voice_user = "unknown"
        #if voice_user != "unknown":
        #    user += voice_user + ", according to voice print service\n"

        #bluetooth_user = self.userid.request_bluetooth_id(user_id)
        #if bluetooth_user is None:
        #    bluetooth_user = "unknown"
        #if bluetooth_user != "unknown":
        #    user += bluetooth_user + ", according to bluetooth service\n"

        usr = message.context.get("user", "unknown")
        if usr == "unknown":
            source = message.context.get("destinatary")
            if source == "all":
                source = "local"
            usr = "unknown " + source + " user"
        user += usr + ", according to source of message\n"

        self.speak_dialog("who.user.is", {"username": user})

    def handle_what_am_i_intent(self, message):
        if ":" in message.context.get("destinatary", ""):
            # server
            target, sock_num = message.context.get("destinatary").split(":")
        else:
            # non server
            target = message.context.get("destinatary", "unknown source")
            self.log.debug("could not get socket from " + str(target))
        self.speak_dialog("what.user.is", {"usertype": target})

    def stop(self):
        pass


def create_skill():
    return UserIdSkill()
