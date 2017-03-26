from abc import ABCMeta, abstractmethod

from mycroft.messagebus.message import Message


class DisplayService():
    def __init__(self, emitter):
        self.emitter = emitter

    def show(self, pic="", utterance=''):
        self.emitter.emit(Message('MycroftDisplayServiceShow',
                                  data={'picture': pic,
                                        'utterance': utterance}))


class DisplayBackend():
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self, config, emitter):
        pass

    @abstractmethod
    def show(self, pic):
        pass

    @abstractmethod
    def stop(self):
        pass
