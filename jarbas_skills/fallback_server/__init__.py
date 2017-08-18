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


from jarbas_utils.jarbas_services import ServiceBackend
from mycroft.skills.core import FallbackSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class ServerFallbackService(ServiceBackend):
    def __init__(self, emitter=None, timeout=30, waiting_messages=[
        "server.message.received"],logger=None):
        super(ServerFallbackService, self).__init__(name="ServerFallbackService",
                                                    emitter=emitter, timeout=timeout,
                                                    waiting_messages=waiting_messages, logger=logger)

    def wait_server_response(self, data = None):
        if data is None:
            data = {}
        self.send_request(message_type="server.intent_failure",
                          message_data=data)
        return self.wait("server.message.received")


class ServerFallback(FallbackSkill):
    def __init__(self):
        super(ServerFallback, self).__init__(name="ServerFallbackSkill")
        self.server = None

    def initialize(self):
        self.register_fallback(self.handle_fallback, 50)
        self.server = ServerFallbackService(self.emitter)

    def handle_fallback(self, message):
        return self.server.wait_server_response(message.data)

    def stop(self):
        pass


def create_skill():
    return ServerFallback()
