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

from jarbas_utils.skill_tools import ServerFallbackQuery
from mycroft.skills.core import FallbackSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class ServerFallback(FallbackSkill):
    def __init__(self):
        super(ServerFallback, self).__init__(name="ServerFallbackSkill")
        self.server = None

    def initialize(self):
        self.register_fallback(self.handle_fallback, 50)
        self.server = ServerFallbackQuery(self.name, self.emitter)

    def handle_fallback(self, message):
        return self.server.wait_server_response(message.data, message.context)

    def stop(self):
        pass


def create_skill():
    return ServerFallback()
