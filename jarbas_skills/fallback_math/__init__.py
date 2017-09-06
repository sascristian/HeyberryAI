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


from mycroft.skills.core import FallbackSkill
from mycroft.util.log import getLogger

from mycroft.util.format import solve_expression

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class MathematicsFallback(FallbackSkill):
    def __init__(self):
        super(MathematicsFallback, self).__init__()

    def initialize(self):
        self.register_fallback(self.handle_fallback, 0)

    def handle_fallback(self, message):
        utterance = message.data.get("utterance")
        answer = solve_expression(utterance, nice=True)
        if answer != "":
            self.speak(answer)
            return True
        return False


def create_skill():
    return MathematicsFallback()
