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


class PadatiusFallbackService(ServiceBackend):
    def __init__(self, emitter=None, timeout=5, waiting_messages=["padatius:fallback.response"],logger=None):
        super(PadatiusFallbackService, self).__init__(
            name="PadatiusFallbackService", emitter=emitter, timeout=timeout,
            waiting_messages=waiting_messages, logger=logger)

    def wait_server_response(self, data = None):
        if data is None:
            data = {}
        self.send_request(message_type="padatius:fallback.request",
                          message_data=data)
        self.wait("padatius:fallback.response")
        return self.result.get("success", False)


class PadatiusFallback(FallbackSkill):
    def __init__(self):
        super(PadatiusFallback, self).__init__()
        self.padatius = None

    def initialize(self):
        self.register_fallback(self.handle_fallback, 99)
        self.padatius = PadatiusFallbackService(self.emitter)

    def handle_fallback(self, message):
        return self.padatius.wait_server_response(message.data)

    def stop(self):
        pass


def create_skill():
    return PadatiusFallback()
