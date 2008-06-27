from abc import ABCMeta, abstractmethod

from mycroft.messagebus.message import Message


class DisplayService():
    def __init__(self, emitter):
        self.emitter = emitter

    def show(self, pics=[], utterance=''):
        self.emitter.emit(Message('MycroftDisplayServiceShow',
                                  data={'pictures': pics,
                                        'utterance': utterance}))


class DisplayBackend():
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self, config, emitter):
        pass

    @abstractmethod
    def clear_list(self):
        pass

    @abstractmethod
    def add_list(self, tracks):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def next(self):
        pass

    def previous(self):
        pass
