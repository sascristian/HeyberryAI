#
#
#
# values to be consumed by services / skills and saved to file
#
#
#
import shelve
import time
from mycroft.util.log import getLogger


class Context():
    def __init__(self, name="current.context"):
        self.log = getLogger("context log")
        self.log.setLevel('WARNING')#uncomment to disable logs
        self.counter = 0

        self.setdefaultcontext()

        self.shelve = shelve.open(name, writeback=True)
        try:
            self.read()
        except:
            pass

    def setdefaultcontext(self):
        self.lastorder = ""  # order received
        self.lastaction = ""  # skill executed
        self.lastutterance = ""  # thing said
        self.lastresults = {}  # last skill results
        self.failures = 0
        # time
        self.time = time.time()
        self.timezone = "Europe/Central"
        # location
        self.location = "kansas"
        self.update()

    def resetcounter(self):
        self.counter = 0
        return

    def read(self):
        print "implement reading all values"
        self.counter = self.shelve['counter']

        self.lastorder = self.shelve["last order"]
        self.lastaction = self.shelve["last action"]
        self.lastutterance = self.shelve["last utterance"]
        self.lastresults = self.shelve["last results"]
        self.failures = self.shelve["failures"]
        # time
        self.time = self.shelve["time"]
        self.timezone = self.shelve["timezone"]
        # location
        self.location = self.shelve["location"]
        return

    def update(self):
        print "implement setting all values"
        self.shelve['counter'] = self.counter + 1

        self.shelve["last order"] = self.lastorder
        self.shelve["last action"] = self.lastaction
        self.shelve["last utterance"] = self.lastutterance
        self.shelve["last results"] =  self.lastresults
        self.shelve["failures"] = self.failures
        # time
        self.shelve["time"] = self.time
        self.shelve["timezone"] = self.timezone
        # location
        self.shelve["location"] = self.location

        # save to file current context, permanent!
        self.shelve.sync()
        return

    def close(self):
        self.shelve.close()

class VisionContext():
    def __init__(self, name="vision.context"):
        self.log = getLogger("Vision context log")
        self.log.setLevel('WARNING')#uncomment to disable logs
        self.counter = 0
        ####### vision ######
        self.setdefaultcontext()
        self.shelve = shelve.open(name, writeback=True)
        try:
            self.read()
        except:
            pass

    def setdefaultcontext(self):
        ####### vision ######
        self.master = False
        self.person_on_screen = False
        self.was_person_on_screen_before = False
        self.movement = False
        self.multiple_persons = False
        self.smiling = False

        self.num_persons = 0

        self.distance = 0  # from camera

        # cv2 images
        self.mainface = None  # user face pic - biggest face rect if several faces
        self.lefteye = None
        self.righteye = None
        self.smile = None
        self.vision = None
        self.update()

    def resetcounter(self):
        self.counter = 0
        return

    def read(self):
        #read fromn per manent storage
        self.master = self.shelve['master']
        self.person_on_screen = self.shelve['person_on_screen']
        self.was_person_on_screen_before = self.shelve['was_person_on_screen_before']
        self.movement = self.shelve['movement']
        self.multiple_persons = self.shelve['multiple_persons']
        self.num_persons = self.shelve['num']
        self.smiling = self.shelve['smiling']

        self.distance = self.shelve['distance']

        #cv2 images
        self.mainface = self.shelve['mainface']
        self.lefteye = self.shelve['lefteye ']
        self.righteye = self.shelve['righteye']
        self.smile = self.shelve['smile']
        self.vision = self.shelve['vision']

        self.counter = self.shelve['counter']
        return

    def update(self):
        self.shelve['num'] = self.num_persons
        self.shelve['counter'] = self.counter + 1
        self.shelve['distance'] = self.distance
        self.shelve['master'] = self.master
        self.shelve['person_on_screen'] = self.person_on_screen
        self.shelve['was_person_on_screen_before'] = self.was_person_on_screen_before
        self.shelve['movement'] = self.movement
        self.shelve['multiple_persons'] = self.multiple_persons
        self.shelve['smiling'] =self.smiling

        #cv2 images
        self.shelve['mainface'] =self.mainface
        self.shelve['lefteye '] =self.lefteye
        self.shelve['righteye'] =self.righteye
        self.shelve['smile'] =self.smile
        self.shelve['vision'] =self.vision

        # save to file current context, permanent!
        self.shelve.sync()

        return

    def close(self):
        self.shelve.close()

class FreeWillContext():
    def __init__(self, name="freewill.context"):
        self.log = getLogger("Free Will context log")
        self.log.setLevel('WARNING')#uncomment to disable logs

        self.setdefaultcontext()

        self.shelve = shelve.open(name, writeback=True)
        try:
            self.read()
        except:
            pass

    def setdefaultcontext(self):
        ####### vision ######
        ########
        self.dopamine = 0
        self.serotonine = 0
        self.tiredness = 0
        ########
        self.lasttought = "hello world"
        self.lastaction = "do nothing"
        self.mood = "neutral"
        self.dreaming = False
        self.master_last_seen = "never"  # seconds ago
        self.user_last_seen = "never"
        self.counter = 0
        self.time_since_order = 0
        self.timeuser = 29 * 60
        self.update()
        self.time = time.time()

    def resetcounter(self):
        self.counter = 0
        return

    def read(self):
        self.dreaming = self.shelve['dream']

        self.lasttought = self.shelve["last_tought"]
        self.lastaction = self.shelve["last action"]
        self.mood = self.shelve["mood"]

        self.master_last_seen = self.shelve['master_last_seen']
        self.user_last_seen = self.shelve['user_last_seen']

        self.time_since_order = self.shelve['time_since_order']
        self.time = self.shelve['time']
        self.timeuser = self.shelve['time_user']

        #hormones
        self.dopamine = self.shelve['dopamine'] #reward
        self.serotonine = self.shelve['serotonine'] #happiness
        self.tiredness = self.shelve['tiredness']

        self.counter = self.shelve['counter']
        return

    def update(self):

        self.shelve['dream'] = self.dreaming

        self.shelve["last_tought"] = self.lasttought
        self.shelve["last action"] = self.lastaction
        self.shelve["mood"] = self.mood

        self.shelve['master_last_seen'] =self.master_last_seen
        self.shelve['user_last_seen'] =self.user_last_seen

        self.shelve['time_since_order'] =self.time_since_order
        self.shelve['time'] = time.time()
        self.shelve['time_user'] = self.timeuser

        # hormones
        self.shelve['dopamine'] =  self.dopamine   # reward
        self.shelve['serotonine'] = self.serotonine  # happiness
        self.shelve['tiredness'] = self.tiredness

        # save to file current context, permanent!
        self.shelve.sync()
        return

    def close(self):
        self.shelve.close()


