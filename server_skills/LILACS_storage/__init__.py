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


from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message
from os.path import dirname
import json
import os

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACSJsonStorageSkill(MycroftSkill):
    def __init__(self):
        super(LILACSJsonStorageSkill, self).__init__(
            name="LILACS_Json_Storage_Skill")
        self.reload_skill = False
        self.storage = dirname(__file__) + "/json"
        if not os.path.exists(self.storage):
            os.mkdir(self.storage)

    def initialize(self):
        self.emitter.on("LILACS.node.json.load.request", self.handle_load_node)
        self.emitter.on("LILACS.node.json.save.request", self.handle_save_node)

    def handle_load_node(self, message):
        node = message.data.get("node")
        data = self.load(node)
        if data:
            sucess = True
        else:
            sucess = False
        self.emitter.emit(Message("LILACS.node.json.load.result", {"node":
                                                                       data,
                                                              "sucess":
                                                                  sucess}))

    def handle_save_node(self, message):
        node = message.data.get("node")
        sucess = self.save(node)
        self.emitter.emit(Message("LILACS.node.json.save.result", {"node":
                                                                       node,
                                                              "sucess":
                                                                  sucess}))

    def save(self, node_dict, data_source=None):
        # TODO check hash before writing to file?
        if data_source is None:
            data_source = self.storage
        try:
            with open(data_source + "/" + node_dict.get("node",
                                                        node_dict.get(
                                                            "name",
                                                            "default")) +
                                                                ".json", \
                    'w') as \
                    myfile:
                node_json = json.dumps(node_dict)
                #print node_json
                myfile.write(node_json)
            return True
        except:
            return False

    def load(self, node_name, data_source=None):
        if data_source is None:
            data_source = self.storage
        if os.path.exists(data_source + "/" + node_name + ".json"):
            with open(data_source + "/" + node_name + ".json", 'r') as myfile:
                file_content = myfile.read()
                #print file_content
                node_json = json.loads(file_content)
                #print node_json
            return dict(node_json)
        return None


def create_skill():
    return LILACSJsonStorageSkill()