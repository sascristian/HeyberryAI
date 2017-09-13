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

__author__ = 'jarbas'

LOGGER = getLogger(__name__)

from mycroft.messagebus.message import Message
from mycroft.skills.settings import SkillSettings
from mycroft.configuration import ConfigurationManager
from os.path import dirname, exists
import time, os
from os import mkdir
from jarbas_utils.skill_dev_tools import ResponderBackend

server_config = ConfigurationManager.get().get("jarbas_server", {})


class ClientUser():
    def __init__(self, id, name, emitter, reset=False):
        self.client_id = id
        self.name = name
        self.emitter = emitter
        default_forbidden_messages = server_config.get("forbidden_messages",
                                                       [])
        default_forbidden_skills = server_config.get("forbidden_skills", [])
        default_forbidden_intents = server_config.get("forbidden_intents", [])
        self.default_forbidden_messages = default_forbidden_messages
        self.default_forbidden_skills = default_forbidden_skills
        # TODO get parser skills names, not ids
        self.default_forbidden_intents = default_forbidden_intents
        self.init_user_settings()
        if reset:
            self.reset()
        self.load_user()
        self.save_user()
        # session data
        self.session_key = None  # encrypt everything with this shared key
        self.current_sock = None
        self.current_ip = None
        self.status = "offline"
        self.user_type = "client"

    def init_user_settings(self, path=None):
        if path is None:
            path = dirname(__file__) + "/users"
        # check if folders exist
        if not os.path.exists(path):
            os.makedirs(path)
        path += "/" + str(self.client_id) + ".json"
        self.settings = SkillSettings(path, autopath=False)
        if self.client_id not in self.settings.keys():
            self.settings[self.client_id] = {}

    def load_user(self):
        self.name = self.settings[self.client_id].get("name", "user")
        self.nicknames = self.settings[self.client_id].get("nicknames", [])
        self.public_key = self.settings[self.client_id].get("public_key")
        self.security_level = self.settings[self.client_id].get(
            "security_level", 0)
        self.forbidden_skills = self.settings[self.client_id].get(
            "forbidden_skills", self.default_forbidden_skills)
        self.forbidden_messages = self.settings[self.client_id].get(
            "forbidden_messages", self.default_forbidden_messages)
        self.forbidden_intents = self.settings[self.client_id].get(
            "forbidden_intents", self.default_forbidden_intents)
        self.last_seen = self.settings[self.client_id].get("last_seen",
                                                           "never")
        self.last_timestamp = self.settings[self.client_id].get("last_ts", 0)
        self.known_ips = self.settings[self.client_id].get("known_ips", [])
        self.timestamp_history = self.settings[self.client_id].get(
            "timestamp_history", [])
        self.photo = self.settings[self.client_id].get("photo")
        self.user_type = self.settings[self.client_id].get("user_type",
                                                           "client")

    def save_user(self):
        self.settings[self.client_id]["name"] = self.name
        self.settings[self.client_id]["nicknames"] = self.nicknames
        self.settings[self.client_id]["public_key"] = self.public_key
        self.settings[self.client_id]["security_level"] = self.security_level
        self.settings[self.client_id][
            "forbidden_skills"] = self.forbidden_skills
        self.settings[self.client_id][
            "forbidden_intents"] = self.forbidden_intents
        self.settings[self.client_id]["last_seen"] = self.last_seen
        self.settings[self.client_id]["last_ts"] = self.last_timestamp
        self.settings[self.client_id]["known_ips"] = self.known_ips
        self.settings[self.client_id][
            "timestamp_history"] = self.timestamp_history
        self.settings[self.client_id]["photo"] = self.photo
        self.settings[self.client_id]["user_type"] = self.user_type
        self.settings[self.client_id][
            "forbidden_messages"] = self.forbidden_messages
        self.settings.store()

    def add_new_ip(self, ip, emit=True):
        if ip not in self.known_ips:
            self.known_ips.append(ip)
            if emit:
                self.emitter.emit(Message("user.new_ip", {"ts": time.time(),
                                                          "name": self.name,
                                                          "last_seen": self.last_seen}))

    def update_timestamp(self):
        self.last_timestamp = time.time()
        self.timestamp_history.append(self.last_timestamp)

    def update_last_seen(self, last_seen):
        self.last_seen = last_seen

    def set_key(self, key):
        self.public_key = key

    def authenticate(self):
        pass

    def add_nicknames(self, names):
        if self.name == "user":
            self.name = names[0]
        for name in names:
            if name not in self.nicknames:
                self.nicknames.append(name)

    def reset(self):
        self.name = "user"
        self.nicknames = []
        self.public_key = "todo"
        self.security_level = 0
        self.forbidden_messages = self.default_forbidden_messages
        self.forbidden_skills = self.default_forbidden_skills
        self.forbidden_intents = self.default_forbidden_intents
        self.last_seen = "never"
        self.last_timestamp = 0
        self.known_ips = []
        self.timestamp_history = []
        self.photo = None
        self.user_type = "client"
        self.save_user()


class ClientManagerSkill(MycroftSkill):
    def __init__(self):
        super(ClientManagerSkill, self).__init__()
        self.reload_skill = False
        self.user_list = {}  # id, sock
        self.users = {}  # id, user object
        self.facebook_users = {}  # fb_id, user object

    def initialize(self):
        # listen for status updates
        self.emitter.on("user.connect", self.handle_user_connect)
        self.emitter.on("user.names", self.handle_user_names)
        self.emitter.on("user.request", self.handle_user_request)
        self.emitter.on("user.disconnect", self.handle_user_disconnect)
        self.emitter.on("fb.chat.message", self.handle_fb_message_received)
        self.emitter.on("fb.chat.message.seen", self.handle_fb_message_seen)
        self.emitter.on("fb.last.seen.timestamps", self.handle_fb_timestamp)

        # build users id list db from disk
        if not exists(dirname(__file__) + "/users"):
            mkdir(dirname(__file__) + "/users")
        user_files = os.listdir(dirname(__file__) + "/users")
        for file in user_files:
            if ".json" in file:
                user_id = file.replace(".json", "")
                self.user_list[user_id] = None
        # build user objects
        for user_id in self.user_list.keys():
            user = ClientUser(id=user_id, emitter=self.emitter, name="user")
            user.status = "offline"
            self.users[user_id] = user

        # sort facebook users
        for user_id in self.users:
            user = self.users[user_id]
            if user.user_type == "facebook chat":
                self.facebook_users[user_id] = user

        # set responders
        self.sock_responder = ResponderBackend(self.name + "_socks",
                                               self.emitter,
                                               self.log, server=False,
                                               client=False)
        self.id_responder = ResponderBackend(self.name + "_id",
                                             self.emitter,
                                             self.log, server=False,
                                             client=False)
        self.facebook_responder = ResponderBackend(self.name + "_facebook",
                                                   self.emitter,
                                                   self.log, server=False,
                                                   client=False)
        # set responder answers
        self.sock_responder.set_response_handler("user.from_sock.request",
                                                 self.handle_user_from_sock_request)
        self.id_responder.set_response_handler("user.from_id.request",
                                               self.handle_user_from_id_request)
        self.facebook_responder.set_response_handler(
            "user.from_facebook.request",
            self.handle_user_from_facebook_request)

    # internal messages
    def handle_user_from_id_request(self, message):
        user_id = message.data.get("id")
        found = False
        for id in self.user_list.keys():
            # search socks
            if id == user_id:
                user_id = str(id)
                self.log.info("sock user found: " + user_id)
                found = True

        if not found:
            # search fb
            for id in self.facebook_users.keys():
                # search socks
                if id == user_id:
                    user_id = str(id)
                    self.log.info("facebook user found: " + user_id)
                    found = True
        else:
            data = {"id": user_id,
                    "forbidden_skills": self.users[user_id].forbidden_skills,
                    "forbidden_messages": self.users[
                        user_id].forbidden_messages,
                    "forbidden_intents": self.users[
                        user_id].forbidden_intents,
                    "security_level": self.users[user_id].security_level,
                    "pub_key": self.users[user_id].public_key,
                    "nicknames": self.users[user_id].nicknames}
            self.id_responder.update_response_data(data, message.context)
            return

        if found:
            data = {"id": user_id,
                    "forbidden_skills": self.facebook_users[
                        user_id].forbidden_skills,
                    "forbidden_messages": self.facebook_users[
                        user_id].forbidden_messages,
                    "forbidden_intents": self.facebook_users[
                        user_id].forbidden_intents,
                    "security_level": self.facebook_users[
                        user_id].security_level,
                    "pub_key": self.facebook_users[user_id].public_key,
                    "nicknames": self.facebook_users[user_id].nicknames}
            self.id_responder.update_response_data(data, message.context)
        else:
            data = {"id": user_id, "error": "no such user"}
            self.id_responder.update_response_data(data, message.context)

    def handle_user_from_facebook_request(self, message):
        user_id = message.data.get("id")
        if user_id not in self.facebook_users.keys():
            self.log.warning(
                "Unknown facebook id provided, creating new user profile")
            # new user
            new_user = ClientUser(id=user_id, emitter=self.emitter)
            self.facebook_users[user_id] = new_user

        data = {"id": user_id,
                "forbidden_skills": self.facebook_users[
                    user_id].forbidden_skills,
                "forbidden_messages": self.facebook_users[
                    user_id].forbidden_messages,
                "forbidden_intents": self.facebook_users[
                    user_id].forbidden_intents,
                "security_level": self.facebook_users[user_id].security_level,
                "pub_key": self.facebook_users[user_id].public_key,
                "nicknames": self.facebook_users[user_id].nicknames}
        self.facebook_responder.update_response_data(data, message.context)

    def handle_user_from_sock_request(self, message):
        sock = message.data.get("sock")
        ip = message.data.get("ip")
        user_id = None
        if ip is None:
            for user_id in self.users:
                user = self.users[user_id]
                if "facebook" in user.user_type:
                    continue
                if user.current_sock == sock:
                    self.user_list[user_id] = sock
                    break
        else:
            user_id = self.user_from_ip_sock(sock, ip)

        if user_id is None:
            self.log.error("Something went wrong")
            # TODO send close request?
            self.sock_responder.update_response_data(
                {"id": None, "error": "user does not seem to exist"},
                message.context)
            return

        data = {"id": user_id,
                "forbidden_skills": self.users[user_id].forbidden_skills,
                "forbidden_messages": self.users[user_id].forbidden_messages,
                "forbidden_intents": self.users[user_id].forbidden_intents,
                "security_level": self.users[user_id].security_level,
                "pub_key": self.users[user_id].public_key,
                "nicknames": self.users[user_id].nicknames}
        self.sock_responder.update_response_data(data, message.context)

    # facebook messages
    def handle_fb_timestamp(self, message):
        timestamps = message.data.get("timestamps", {})
        for id in timestamps:
            name = timestamps[id]["name"]
            ts = timestamps[id]["timestamp"]
            if id in self.facebook_users.keys():
                current_user = self.facebook_users[id]
            else:
                current_user = ClientUser(id=id, name=name,
                                          emitter=self.emitter)
                self.facebook_users[id] = current_user
            current_user.name = name
            current_user.add_nicknames([name])
            current_user.user_type = "facebook chat"
            current_user.status = "online"
            current_user.last_timestamp = ts
            current_user.last_seen = time.asctime()
            if ts not in current_user.timestamp_history:
                current_user.timestamp_history.append(ts)
            current_user.save_user()

    def handle_fb_message_seen(self, message):
        name = message.data.get("friend_name")
        id = message.data.get("friend_id")
        ts = message.data.get("timestamp")
        if id in self.facebook_users.keys():
            current_user = self.facebook_users[id]
        else:
            current_user = ClientUser(id=id, name=name, emitter=self.emitter)
            self.facebook_users[id] = current_user

        current_user.name = name
        current_user.add_nicknames([name])
        current_user.user_type = "facebook chat"
        current_user.status = "online"
        current_user.last_timestamp = ts
        current_user.last_seen = time.asctime()
        if ts not in current_user.timestamp_history:
            current_user.timestamp_history.append(ts)
        current_user.save_user()

    def handle_fb_message_received(self, message):
        name = message.data.get("author_name")
        id = message.data.get("author_id")
        photo = message.data.get("photo")
        if id in self.facebook_users.keys():
            current_user = self.facebook_users[id]
        else:
            current_user = ClientUser(id=id, name=name, emitter=self.emitter)
            self.facebook_users[id] = current_user
        current_user.name = name
        current_user.add_nicknames([name])
        current_user.user_type = "facebook chat"
        current_user.status = "online"
        current_user.last_seen = time.asctime()
        current_user.photo = photo
        current_user.save_user()

    # server messages
    def handle_user_connect(self, message):
        ip = message.data.get("ip")
        sock = message.data.get("sock")
        pub_key = message.data.get("pub_key")
        nicknames = message.data.get("nicknames", [])
        user_name = message.context.get("user", "user")

        type = "sock_client"
        current_user = None
        if pub_key is None:
            pub_key = "yy"

        self.log.info("Comparing user key to keys in db")
        # id user by pub_key
        for user in self.users:
            user = self.users[user]
            if user.public_key == pub_key:
                self.log.info("User found")
                current_user = user.user_id

        if current_user is None:
            self.log.info("Registering new user")
            # new user
            # get new_id
            new_id = len(self.users.keys()) + 1
            self.log.info("Assigning new id: " + str(new_id))
            while str(new_id) in self.users.keys():
                self.log.info("assigned id already exists, increasing count")
                new_id += 1
            # save new user
            new_id = str(new_id)
            self.log.info("Creating user")
            try:
                new_user = ClientUser(new_id, user_name, self.emitter,
                                      reset=False)
            except Exception as e:
                self.log.error("Error creating user: " + str(e))
                return
            new_user.public_key = pub_key
            self.users[new_id] = new_user
            current_user = new_id

        self.log.info("Setting user sock")
        self.user_list[current_user] = sock  # set active sock
        # update user info
        self.log.info("Updating user info")
        current_user = self.users[current_user]
        current_user.current_sock = sock
        current_user.current_ip = ip
        current_user.add_new_ip(ip)
        current_user.last_timestamp = time.time()
        current_user.last_seen = time.asctime()
        current_user.timestamp_history.append(time.time())
        current_user.user_type = type
        current_user.status = "online"
        current_user.add_nicknames(nicknames)
        current_user.save_user()
        self.log.info(
            "User updated: " + current_user.name + " " + current_user.current_ip + " " + str(
                current_user.last_timestamp))
        self.emitter.emit(Message("user.connected",
                                  {"internal_id": current_user.id,
                                   "name": current_user.name,
                                   "ip": current_user.current_ip,
                                   "sock": current_user.current_sock},
                                  message.context))

    def user_from_ip_sock(self, sock, ip):
        user_id = None
        for uid in self.user_list.keys():
            if self.user_list[uid] == sock:
                user_id = uid
                break
        if user_id is None:
            for user_id in self.users:
                if self.users[user_id].current_ip == ip:
                    self.user_list[user_id] = sock
                    break
        return user_id

    def handle_user_names(self, message):
        names = message.data.get("names")
        sock = message.data.get("sock")
        ip = message.data.get("ip")
        user_id = self.user_from_ip_sock(sock, ip)
        current_user = self.users[user_id]
        current_user.add_nicknames(names)
        current_user.current_sock = sock
        current_user.last_timestamp = time.time()
        current_user.last_seen = time.asctime()
        current_user.timestamp_history.append(time.time())
        current_user.save_user()

    def handle_user_request(self, message):
        sock = message.data.get("sock")
        ip = message.data.get("ip")
        if not ip or not sock:
            return
        user_id = self.user_from_ip_sock(sock, ip)
        current_user = self.users[user_id]
        current_user.last_timestamp = time.time()
        current_user.last_seen = time.asctime()
        current_user.timestamp_history.append(time.time())
        current_user.save_user()

    def handle_user_disconnect(self, message):
        sock = message.data.get("sock")
        ip = message.data.get("ip")
        user_id = self.user_from_ip_sock(sock, ip)
        current_user = self.users[user_id]
        current_user.last_timestamp = time.time()
        current_user.current_sock = None
        current_user.last_seen = time.asctime()
        current_user.timestamp_history.append(time.time())
        current_user.status = "offline"
        current_user.save_user()
        self.emitter.emit(Message("user.disconnected", {}, message.context))

    def stop(self):
        # save all users
        for user in self.facebook_users:
            self.facebook_users[user].save_user()
        for user in self.users:
            self.users[user].save_user()


def create_skill():
    return ClientManagerSkill()
