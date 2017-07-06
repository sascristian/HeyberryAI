from time import sleep, time
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

__author__ = 'jarbas'


class ServiceBackend(object):
    """
        Base class for all service implementations.

        Args:
            name: name of service (str)
            emitter: eventemitter or websocket object
            timeout: time in seconds to wait for response (int)
            waiting_messages: end wait on any of these messages (list)

    """

    def __init__(self, name, emitter=None, timeout=5, waiting_messages=None, logger=None):
        self.initialize(name, emitter, timeout, waiting_messages, logger)

    def initialize(self, name, emitter, timeout, waiting_messages, logger):
        """
           initialize emitter, register events, initialize internal variables
        """
        self.name = name
        self.emitter = emitter
        self.timeout = timeout
        self.result = None
        self.waiting = False
        self.waiting_for = "any"
        if logger is None:
            self.logger = getLogger(self.name)
        else:
            self.logger = logger
        if waiting_messages is None:
            waiting_messages = []
        self.waiting_messages = waiting_messages
        for msg in waiting_messages:
            self.emitter.on(msg, self.end_wait)

    def send_request(self, message_type, message_data=None, message_context=None):
        """
          send message
        """
        if message_data is None:
            message_data = {}
        if message_context is None:
            message_context = {"source": self.name, "waiting_for": self.waiting_messages}
        self.emitter.emit(Message(message_type, message_data, message_context))

    def wait(self, waiting_for="any"):
        """
            wait until result response or time_out
            waiting_for: message that ends wait, by default use any of waiting_messages list
            returns True if result received, False on timeout
        """
        self.waiting_for = waiting_for
        if self.waiting_for != "any" and self.waiting_for not in self.waiting_messages:
            self.emitter.on(waiting_for, self.end_wait)
            self.waiting_messages.append(waiting_for)
        self.waiting = True
        start = time()
        elapsed = 0
        while self.waiting and elapsed < self.timeout:
            elapsed = time() - start
            sleep(0.3)

        return not self.waiting

    def end_wait(self, message):
        """
            Check if this is the message we were waiting for and save result
        """
        if self.waiting_for == "any" or message.type == self.waiting_for:
            self.result = message.data
            self.waiting = False

    def get_result(self):
        """
            return last processed result
        """
        return self.process_result()

    def process_result(self):
        """
         process and return only desired data
         """
        if self.result is None:
            self.result = {}
        return self.result