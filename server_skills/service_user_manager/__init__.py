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

__author__ = 'eward'

LOGGER = getLogger(__name__)

from mycroft.messagebus.message import Message
from mycroft.skills.settings import SkillSettings
from os.path import dirname
import time


class User():
    def __init__(self, id, name="user", emitter=None):
        self.user_id = id
        self.name = name
        self.emitter = emitter
        self.load_user()
        self.save_user()
        # session data
        self.session_key = None #encrypt everything with this shared key
        self.current_sock = None
        self.current_ip = None
        self.status = "offline"
        self.user_type = "client"

    def load_user(self, path=None):
        if path is None:
            path = dirname(__file__) + "/users/"+str(self.user_id)+".json"
        self.settings = SkillSettings(path)
        if self.user_id not in self.settings.keys():
            self.settings[self.user_id] = {}
        self.name = self.settings[self.user_id].get("name")
        self.nicknames = self.settings[self.user_id].get("nicknames", [])
        self.public_key = self.settings[self.user_id].get("public_key")
        self.security_level = self.settings[self.user_id].get("security_level", 0)
        self.authorized_skills = self.settings[self.user_id].get("authorized_skills", [])
        self.last_seen = self.settings[self.user_id].get("last_seen", "never")
        self.last_timestamp = self.settings[self.user_id].get("last_ts", 0)
        self.known_ips = self.settings[self.user_id].get("known_ips", [])
        self.timestamp_history = self.settings[self.user_id].get("timestamp_history", [])
        self.photo = self.settings[self.user_id].get("photo")
        self.user_type = self.settings[self.user_id].get("user_type", "client")

    def save_user(self):
        self.settings[self.user_id]["name"] = self.name
        self.settings[self.user_id]["nicknames"] = self.nicknames
        self.settings[self.user_id]["public_key"] = self.public_key
        self.settings[self.user_id]["security_level"] = self.security_level
        self.settings[self.user_id]["authorized_skills"] = self.authorized_skills
        self.settings[self.user_id]["last_seen"] = self.last_seen
        self.settings[self.user_id]["last_ts"] = self.last_timestamp
        self.settings[self.user_id]["known_ips"] = self.known_ips
        self.settings[self.user_id]["timestamp_history"] = self.timestamp_history
        self.settings[self.user_id]["photo"] = self.photo
        self.settings[self.user_id]["user_type"] = self.user_type
        self.settings.store()

    def add_new_ip(self, ip, emit=True):
        if ip not in self.known_ips:
            self.known_ips.append(ip)
            if emit:
                self.emitter.emit(Message("user.new_ip", {"ts": time.time(), "name": self.name, "last_seen": self.last_seen}))

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
        for name in names:
            if name not in self.nicknames:
                self.nicknames.append(name)


class UserSkill(MycroftSkill):
    def __init__(self):
        super(UserSkill, self).__init__(name="UserSkill")
        self.default_key = ""
        self.user_list = self.settings.get("users", {}) # id, sock
        self.users = {"0": User("0")}    # id, user object
        for user_id in self.user_list.keys():
            user = User(id=user_id, emitter=self.emitter)
            self.users[user_id] = user
        self.facebook_users = {} #fb_id, user object

    def initialize(self):
        self.emitter.on("user.connect", self.handle_user_connect)
        self.emitter.on("user.names", self.handle_user_names)
        self.emitter.on("user.request", self.handle_user_request)
        self.emitter.on("user.disconnect", self.handle_user_disconnect)
        self.emitter.on("user.facebook", self.handle_facebook_user)

    def handle_facebook_user(self, message):
        name = message.data.get("name")
        id = message.data.get("id")
        photo = message.data.get("photo")
        ts = message.data.get("ts")
        last_seen = message.data.get("last_seen")
        if id in self.facebook_users.keys():
            current_user = self.facebook_users[id]
        else:
            current_user = User(id=id, name=name, emitter=self.emitter)
            self.facebook_users[id] = current_user

        current_user.add_nicknames([name])
        current_user.user_type = "facebook chat"
        current_user.status = "online"
        if last_seen is not None:
            current_user.last_seen = last_seen
        if photo is not None:
            current_user.photo = photo
        if ts is not None:
            current_user.last_timestamp = ts
            current_user.timestamp_history.append(ts)
        current_user.save()

    def handle_user_connect(self, message):
        ip = message.data.get("ip")
        sock = message.data.get("sock")
        pub_key = message.data.get("pub_key")
        type = message.context.get("source", "unknown")
        user = message.context.get("user", "user")

        if ":" in type:
            type = type.split(":")[0] + "client"
        elif "fbchat" in type:
            type = "facebook chat"

        current_user = None
        if pub_key == self.default_key:
            # default shared user
            current_user = self.users["0"]
        else:
            # id user by pub_key
            for user in self.users:
                user = self.users[user]
                if user.public_key == pub_key:
                    current_user = user.user_id
        if current_user is None:
            # new user
            # get new_id
            new_id = len(self.users.keys())+1
            while new_id in self.users.keys():
                new_id += 1
            # save new user
            new_user = User(id=str(new_id), emitter=self.emitter, name=user)
            self.users[str(new_id)] = new_user
            current_user = str(new_id)

        self.user_list[current_user] = sock # set active sock
        # update user info
        current_user = self.user_list[current_user]
        current_user.current_sock = sock
        current_user.current_ip = ip
        current_user.add_new_ip(ip)
        current_user.last_timestamp = time.time()
        current_user.last_seen = "0 seconds ago"
        current_user.timestamp_history.append(time.time())
        current_user.user_type = type
        current_user.status = "online"
        current_user.save_user()
        self.log.info("User updated: " + user + " " + ip + " " + str(current_user.last_timestamp))

    def handle_user_names(self, message):
        names = message.data.get("names")
        sock = message.data.get("sock")
        user_id = None
        for user in self.user_list:
            if self.user_list[user] == sock:
                user_id = user
                break
        if user_id is None:
            self.log.error("Could not understand what user this is")
            return

        current_user = self.users[user_id]
        current_user.add_nicknames(names)
        current_user.last_timestamp = time.time()
        current_user.last_seen = "0 seconds ago"
        current_user.timestamp_history.append(time.time())
        current_user.save_user()

    def handle_user_request(self, message):
        sock = message.data.get("sock")
        user_id = None
        for user in self.user_list:
            if self.user_list[user] == sock:
                user_id = user
                break
        if user_id is None:
            self.log.error("Could not understand what user this is")
            return

        current_user = self.users[user_id]
        current_user.last_timestamp = time.time()
        current_user.last_seen = "0 seconds ago"
        current_user.timestamp_history.append(time.time())
        current_user.save_user()

    def handle_user_disconnect(self, message):
        sock = message.data.get("sock")
        user_id = None
        for user in self.user_list:
            if self.user_list[user] == sock:
                user_id = user
                break
        if user_id is None:
            self.log.error("Could not understand what user this is")
            return

        current_user = self.users[user_id]
        current_user.last_timestamp = time.time()
        current_user.last_seen = "0 seconds ago"
        current_user.timestamp_history.append(time.time())
        current_user.status = "offline"
        current_user.save_user()

    def stop(self):
        pass


def create_skill():
    return UserSkill()
