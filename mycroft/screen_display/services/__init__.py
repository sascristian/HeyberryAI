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
    def display(self, pictures):
        """
           Display First Picture in Pictures List of paths
        """
        pass

    def reset(self):
        """
            Reset Display.
        """
        pass

    def clear(self):
        """
            Clear Display.
        """
        pass

    def next(self):
        """
            Skip to next pic in playlist.
        """
        pass

    def previous(self):
        """
            Skip to previous pic in playlist.
        """
        pass

    def lock(self):
        """
           Set Lock Flag so nothing else can display
        """
        pass

    def unlock(self):
        """
           Unset Lock Flag so nothing else can display
        """
        pass

    def stop(self):
        """
            Stop playback.
        """
        pass
