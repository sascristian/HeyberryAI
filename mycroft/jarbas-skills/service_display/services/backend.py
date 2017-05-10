from abc import ABCMeta, abstractmethod

__author__ = 'jarbas'


class DisplayBackend():
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def show(self, pic):
        pass

    @abstractmethod
    def stop(self):
        pass