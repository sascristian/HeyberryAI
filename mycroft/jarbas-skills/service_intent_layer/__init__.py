from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from time import time, sleep
from multiprocessing import Process

__author__ = 'jarbas'

logger = getLogger(__name__)


class IntentParser():
    def __init__(self, emitter, time_out = 20):
        self.emitter = emitter
        self.waiting = False
        self.intent = ""
        self.id = 0
        self.emitter.on("intent_response", self.handle_receive_intent)
        self.emitter.on("intent_to_skill_response", self.handle_receive_skill_id)
        self.time_out = time_out

    def determine_intent(self, utterance, lang="en-us"):
        self.waiting = True
        self.emitter.emit(Message("intent_request", {"utterance": utterance, "lang": lang}))
        start_time = time()
        t = 0
        while self.waiting and t < self.time_out:
            t = time() - start_time
        return self.intent, self.id

    def get_skill_id(self, intent_name):
        self.waiting = True
        self.id = 0
        self.emitter.emit(Message("intent_to_skill_request", {"intent_name": intent_name}))
        start_time = time()
        t = 0
        while self.waiting and t < self.time_out:
            t = time() - start_time
        self.waiting = False
        return self.id

    def handle_receive_intent(self, message):
        self.id = message.data["skill_id"]
        self.intent = message.data["intent_name"]
        self.waiting = False

    def handle_receive_skill_id(self, message):
        self.id = message.data["skill_id"]
        self.waiting = False


class IntentLayers():
    def __init__(self, emitter, layers = [], timer = 500):
        self.emitter = emitter
        # make intent tree for N layers
        self.layers = []
        self.current_layer = 0
        self.timer = timer
        self.timer_thread = None
        for layer in layers:
            self.add_layer(layer)
        self.activate_layer(0)

    def disable_intent(self, intent_name):
        """Disable a registered intent"""
        self.emitter.emit(Message("disable_intent", {"intent_name": intent_name}))

    def enable_intent(self, intent_name):
        """Reenable a registered self intent"""
        self.emitter.emit(Message("enable_intent", {"intent_name": intent_name}))

    def start_timer(self):

        self.stop_timer()

        # set new timer
        def timer():
            logger.info("New Timer Started")
            start_time = time()
            while time() - start_time <= self.timer:
                sleep(1)
            # on end of timer reset tree
            logger.info("Timer Ended - resetting tree")
            self.reset()

        self.timer_thread = Process(target=timer)
        self.timer_thread.start()

    def stop_timer(self):
        logger.info("Stopping previous timer")
        try:
            # cancel previous timers
            self.timer_thread.terminate()
        except:
            pass

    def reset(self):
        logger.info("Reseting Tree")
        self.stop_timer()
        self.activate_layer(0)

    def next(self):
        logger.info("Going to next Tree Layer")
        self.current_layer += 1
        if self.current_layer > len(self.layers):
            logger.info("Already in last layer, going to layer 0")
            self.current_layer = 0
        if self.current_layer != 0:
            self.start_timer()
        self.activate_layer(self.current_layer)

    def previous(self):
        logger.info("Going to previous Tree Layer")
        self.current_layer -= 1
        if self.current_layer < 0:
            self.current_layer = len(self.layers)
            logger.info("Already in layer 0, going to last layer")
        if self.current_layer != 0:
            self.start_timer()
        self.activate_layer(self.current_layer)

    def add_layer(self, intent_list=[]):
        self.layers.append(intent_list)
        logger.info("Adding layer to tree " + str(intent_list))

    def replace_layer(self, layer_num, intent_list=[]):
        logger.info("Removing layer number " + str(layer_num) + " from tree ")
        self.layers.pop(layer_num)
        self.layers[layer_num] = intent_list
        logger.info("Adding layer" + str(intent_list) + " to tree in position " + str(layer_num) )

    def remove_layer(self, layer_num):
        self.layers.pop(layer_num)
        logger.info("Removing layer number " + str(layer_num) + " from tree ")

    def find_layer(self, intent_list=[]):
        layer_list = []
        for i in range(0, len(self.layers)):
            if self.layers[i] == intent_list:
                layer_list.append(i)
        return layer_list

    def disable(self):
        logger.info("Disabling tree")
        # disable all tree layers
        for i in range(0, len(self.layers)):
            self.deactivate_layer(i)

    def activate_layer(self, layer_num):
        # error check
        if layer_num < 0 or layer_num > len(self.layers):
            logger.error("invalid layer number")
            return

        self.current_layer = layer_num

        # disable other layers
        self.disable()

        # TODO in here we should wait for all intents to be detached
        # sometimes detach intent from this step comes after register from next
        sleep(0.3)

        # enable layer
        logger.info("Activating Layer " + str(layer_num))
        for intent_name in self.layers[layer_num]:
            self.enable_intent(intent_name)

    def deactivate_layer(self, layer_num):
        # error check
        if layer_num < 0 or layer_num > len(self.layers):
            logger.error("invalid layer number")
            return
        logger.info("Deactivating Layer " + str(layer_num))
        for intent_name in self.layers[layer_num]:
            self.disable_intent(intent_name)

# TODO intent layer usage / stats / help skill