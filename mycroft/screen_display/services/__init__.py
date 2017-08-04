from abc import ABCMeta, abstractmethod

__author__ = 'jarbas'


class DisplayBackend():
    """
        Base class for all display backend implementations.

        Args:
            config: configuration dict for the instance
            emitter: eventemitter or websocket object
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, config, emitter):
        pass

    @abstractmethod
    def display(self):
        """
            Start playback.
        """
        pass

    @abstractmethod
    def reset(self):
        """
            Start playback.
        """
        pass

    @abstractmethod
    def clear(self):
        """
            Start playback.
        """
        pass

    def lock(self):
        pass

    def unlock(self):
        pass

    def stop(self):
        """
            Stop playback.
        """
        pass
