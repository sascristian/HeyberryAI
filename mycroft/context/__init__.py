#
#
#
# bool values to be checked and saved to file
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

        #self.log.basicConfig(filename='example.log',level=logging.DEBUG)
        #self.shelve = shelve.open("contexts/current")
        #self.read()

        #self.last = shelve.open("contextast", writeback = True)
        #self.last = self.shelve
        #self.last.sync()
        #self.last.close()
        ####

        ####
        self.dopamine = 0
        self.serotonine = 0
        self.tiredness = 0

        ####### vision ######
        self.master = False
        self.person_on_screen = False
        self.was_person_on_screen_before = False
        self.movement = False
        self.multiple_persons = False

        self.dreaming = False
        self.smiling = False

        self.num_persons = 0
        self.master_last_seen = "never" #seconds ago
        self.user_last_seen = "never"
        self.counter = 0
        self.distance = 0  # from camera
        self.time_since_order = 0
        self.time = time.time()
        self.timeuser = 29*60

        # cv2 images
        self.mainface = None  # user face pic - biggest face rect if several faces
        self.lefteye = None
        self.righteye = None
        self.smile = None
        self.vision = None

        self.shelve = shelve.open(name, writeback=True)
        try:
            self.read()
        except:
            pass
        #self.printcontext()

    def setdefaultcontext(self):
        ####### vision ######
        self.master = False
        self.person_on_screen = False
        self.was_person_on_screen_before = False
        self.movement = False
        self.multiple_persons = False

        self.smiling = False
        self.dreaming = False

        self.num_persons = 0
#only on first run
        #self.master_last_seen = "never" #seconds ago
        #self.user_last_seen = "never"
        #self.counter = 0
        self.distance = 0 #from camera
        #self.time_since_order = 0

        #cv2 images
        self.mainface = None # user face pic - biggest face rect if several faces
        self.lefteye = None
        self.righteye = None
        self.smile = None
        self.vision = None
        self.time = time.time()
        #self.timeuser = 99999
        self.update()

    def resetcounter(self):
        self.counter = 0
        return

    def printcontext(self):

        #print "distance to user:  " + str(self.distance)
        #print "last order received: " + str(self.time_since_order)
        self.log.info(' context number: ' + str(self.counter))
        self.log.info(' time: ' + str(time.time()))
        self.log.info(' user last seen: ' + str(self.user_last_seen))
        #self.log.info(' master last seen: ' + str(self.master_last_seen))
        #self.log.info(' master: ' + str(self.master))
        self.log.info(' time elapsed since user seen: ' + str(self.timeuser))
        self.log.info(' time elapsed since action executed: ' + str(self.time_since_order))
        self.log.info(' number of person: ' + str(self.num_persons+1))
        self.log.info(' smiling: ' + str(self.smiling))
        self.log.info(' dreaming: ' + str(self.dreaming))
        self.log.info(' dopamine: ' + str(self.dopamine))
        self.log.info(' serotonine: ' + str(self.serotonine))
        self.log.info(' tiredness: ' + str(self.tiredness))

        return

    def read(self):
        #read fromn per manent storage
        self.master = self.shelve['master']
        self.person_on_screen = self.shelve['person_on_screen']
        self.was_person_on_screen_before = self.shelve['was_person_on_screen_before']
        self.movement = self.shelve['movement']
        self.multiple_persons = self.shelve['multiple_persons']
        self.num_persons = self.shelve['num']
        self.dreaming = self.shelve['dream']
        self.smiling = self.shelve['smiling']

        self.master_last_seen = self.shelve['master_last_seen']
        self.user_last_seen = self.shelve['user_last_seen']
        self.distance = self.shelve['distance']
        self.time_since_order = self.shelve['time_since_order']
        self.time = self.shelve['time']
        self.timeuser = self.shelve['time_user']
        #cv2 images
        self.mainface = self.shelve['mainface']
        self.lefteye = self.shelve['lefteye ']
        self.righteye = self.shelve['righteye']
        self.smile = self.shelve['smile']
        self.vision = self.shelve['vision']
        self.counter = self.shelve['counter']

        #hormones
        self.dopamine = self.shelve['dopamine'] #reward
        self.serotonine = self.shelve['serotonine'] #happiness
        self.tiredness = self.shelve['tiredness']
        return

    def update(self):
        self.shelve['num'] = self.num_persons
        self.shelve['counter'] = self.counter + 1
        self.shelve['master'] = self.master
        self.shelve['person_on_screen'] = self.person_on_screen
        self.shelve['was_person_on_screen_before'] = self.was_person_on_screen_before
        self.shelve['movement'] = self.movement
        self.shelve['multiple_persons'] = self.multiple_persons
        self.shelve['dream'] = self.dreaming
        self.shelve['smiling'] =self.smiling

        self.shelve['master_last_seen'] =self.master_last_seen
        self.shelve['user_last_seen'] =self.user_last_seen
        self.shelve['distance'] =self.distance
        self.shelve['time_since_order'] =self.time_since_order
        self.shelve['time'] = time.time()
        self.shelve['time_user'] = self.timeuser
        #cv2 images
        self.shelve['mainface'] =self.mainface
        self.shelve['lefteye '] =self.lefteye
        self.shelve['righteye'] =self.righteye
        self.shelve['smile'] =self.smile
        self.shelve['vision'] =self.vision

        # hormones
        self.shelve['dopamine'] =  self.dopamine   # reward
        self.shelve['serotonine'] = self.serotonine  # happiness
        self.shelve['tiredness'] = self.tiredness

        # save to file current context, permanent!
        self.shelve.sync()




        #####testing stuff

        return

    def close(self):
        self.shelve.close()
