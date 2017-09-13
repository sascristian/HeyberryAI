# Copyright 2017 Mycroft AI, Inc.
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
from subprocess import call
from time import time as get_time, sleep

from threading import Event
from os.path import expanduser, isfile, exists, dirname
from os import mkdir
from pkg_resources import get_distribution

from mycroft.configuration import ConfigurationManager
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from mycroft.util.parse import normalize

__author__ = 'matthewscholefield'

logger = getLogger(__name__)

PADATIOUS_VERSION = '0.2.2'  # Also update in requirements.txt


class PadatiousService(object):
    def __init__(self, emitter):
        self.config = ConfigurationManager.get()['padatious']
        # intent_cache = expanduser(self.config['intent_cache'])
        # TODO really fix this
        intent_cache = dirname(__file__) + "/intent_cache"
        if not exists(intent_cache):
            mkdir(intent_cache)
        try:
            from padatious import IntentContainer
        except ImportError:
            logger.error('Padatious not installed. Please re-run dev_setup.sh')
            try:
                call(['notify-send', 'Padatious not installed',
                      'Please run build_host_setup and dev_setup again'])
            except OSError:
                pass
            return
        ver = get_distribution('padatious').version
        logger.warning('VERSION: ' + ver)
        if ver != PADATIOUS_VERSION:
            logger.warning('Using Padatious v' + ver + '. Please re-run ' +
                           'dev_setup.sh to install ' + PADATIOUS_VERSION)

        self.container = IntentContainer(intent_cache)

        self.emitter = emitter
        self.emitter.on('padatious:register_intent', self.register_intent)
        self.emitter.on('padatious:fallback.request', self.handle_fallback)
        self.finished_training_event = Event()

        self.train_delay = self.config['train_delay']
        self.train_time = get_time() + self.train_delay
        self.wait_and_train()

    def wait_and_train(self):
        sleep(self.train_delay)
        if self.train_time < 0.0:
            return

        if self.train_time <= get_time() + 0.01:
            self.train_time = -1.0

            self.finished_training_event.clear()
            logger.info('Training...')
            self.container.train(print_updates=True)
            logger.info('Training complete.')
            self.finished_training_event.set()

    def register_intent(self, message):
        logger.debug('Registering Padatious intent: ' +
                     message.data['intent_name'])

        file_name = message.data['file_name']
        intent_name = message.data['intent_name']
        if not isfile(file_name):
            return

        self.container.load_file(intent_name, file_name)
        self.train_time = get_time() + self.train_delay
        self.wait_and_train()

    def handle_fallback(self, message):
        utt = message.data.get('utterance')
        logger.debug("Padatious fallback attempt: " + utt)

        utt = normalize(utt, message.data.get('lang', 'en-us'))

        if not self.finished_training_event.is_set():
            logger.debug('Waiting for training to finish...')
            self.finished_training_event.wait()

        data = self.container.calc_intent(utt)

        if data.conf < 0.5:
            success = False
        else:
            success = True
            self.emitter.emit(Message(data.name, data=data.matches))

        self.emitter.emit(Message('padatious:fallback.response',
                                  data={"success": success}))
