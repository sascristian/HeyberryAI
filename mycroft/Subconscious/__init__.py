###

author = "Jarbas"

###

from mycroft.context import FreeWillContext
from mycroft.context import VisionContext

from mycroft.configuration import ConfigurationManager
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message

import time
import shelve

import sys
import os

from threading import Thread
import random
from mycroft.util.log import getLogger


logger = getLogger("Subconscious")
neurologger = getLogger("Neurological")

client = None

#neurologger.setLevel("ERROR")
#logger.setLevel("ERROR")
def connect():
    client.run_forever()

class Goal():
    def __init__(self, name, ways):
        self.name = name#"knowledge"
        self.ways = ways#["wikipedia", "wolphram", "articles", "ask user"]

    def way_selector(self, function=None):
        if function is not None:
            return function(self.ways)
        else:
            return self.default_way_selector(self.ways)

    def default_way_selector(self, ways):
        i = random.randint(0,len(ways))
        c = 0
        for way in ways:
            for key in way:
                selected_way = way
                data = selected_way[key]
            if c == i:
                break
            c +=1
        return selected_way , data, key

    def print_ways(self):
        i = 0
        if len(self.ways)>20:
            print "Warning, lots of ways, printing first 20"
        for way in self.ways:
            print way
            i+=1
            if i>= 20:
                break

class Objectives():
    def __init__(self, client):
        self.objectives = {} #name : [Goals]
        self.client = client

    def register_objective(self, name, goals=None):
        try:  # if key exists in dict
            old_goals = self.objectives[name.lower()]
            for goal in old_goals:
                goals.append(goal)  # load previously defined goals
            self.objectives[name.lower()] = goals
        except:#doesnt exit, register
            self.objectives.setdefault(name.lower(), goals)

    def execute_objective(self, name, selectfunction=None):
        if selectfunction is None:
            selectfunction = self.default_select

        intent , data, key, goal = selectfunction(self.objectives[name.lower()])

        print "\nExecuting\n"
        print "objective: "+name
        print "Goal: " + goal
        print "way: " + str(key)
        print "way data :"+str(data)

        self.client.emit(Message(key, data))

        return intent

    def default_select(self, goal_list):
        selected_goal = random.choice(goal_list)
        intent , data, key  = selected_goal.way_selector()
        return intent, data, key, selected_goal.name

    def print_objectives(self):
        print "\nAvailable Objectives:\n"
        for objective in self.objectives:
            print objective

    def print_goals(self, objective):
        for goal in self.objectives[objective]:
            print goal.name
            goal.print_ways()

class freewill():
    def __init__(self):

        # dont be hiperactive, minimum 15 min max 1 hour between actions
        self.min_time_between_actions = 15 * 60  # seconds
        self.max_time_between_actions = 40 * 60  # * 45
        self.greetings = True

        self.generic = ['awesome ', 'cool ', 'the best ', 'brutal ', 'average ', 'satanic ', 'synthetic ', "nice ", "ultra ",
                        "strange ", "weird ", " beautifull ", "ugly ", " the worst ", " most "]
        self.entropy = []
        self.activefriends = []
        self.sentiment = ""
        self.mood = "neutral"
        self.innervoice = 'do nothing'

        self.initialize_toughts()
        self.lasttought = random.choice(self.entropy)
        self.set_actions()

        self.ignorevision = False

        self.clock = time.time()

        self.context = FreeWillContext(name="Subconscious")
        self.visioncontext = VisionContext(name="Vision")


        # connect to messagebus
        global client
        client = WebsocketClient()

        ###### register as many of these as needed to have some executed skill influence something
        client.emitter.on("diagnostics_request", self.diagnostics)
        client.emitter.on('vision_result', self.contextupdate)
        client.emitter.on('recognizer_loop:utterance', self.action)
        client.emitter.on('dopamine_increase_request', self.increasedopamine)
        client.emitter.on('dopamine_decrease_request', self.decreasedopamine)
        client.emitter.on('serotonine_increase_request', self.increaseserotonine)
        client.emitter.on('serotonine_decrease_request', self.decreaseserotonine)
        client.emitter.on('entropy_update', self.entropyate)
        client.emitter.on('entropy_request', self.entropy_request)
        client.emitter.on('entropy_reset', self.entropy_reset)
        client.emitter.on('sentiment_result', self.sentimentresult)
        client.emitter.on('leak_analisys', self.leakfound)
        client.emitter.on('speak', self.onspeak)
        client.emitter.on("context_update", self.context)



        self.event_thread = Thread(target=connect)
        self.event_thread.setDaemon(True)
        self.event_thread.start()

        self.obj = Objectives(client)

        #self.load_objectives_from_config()

        self.word_bank = []
        self.load_word_bank()

        self.knowledge_objective()
        self.dream_about_objective()
        self.facebook_objective()

        #self.obj.print_objectives()

       # for obj in self.obj.objectives:
       #     print obj+"\n"
       #     self.obj.print_goals(obj)

    ####### objectives #####
    def load_objectives_from_config(self):
        objectives = ConfigurationManager.get(["/home/user/jarbas-core/mycroft/Subconscious/objectives.conf"])[
            "Objectives"]
        for objective in objectives:
            #print objective
            goals = []
            for goal in objectives[objective]:
                name = goal
                ways_string = objectives[objective][goal]["ways"]
                #print ways_string

                waylist = []
                for intent in ways_string:
                    #print intent
                    for key in intent:
                        #print key
                        #print intent[key]
                        ways = {}
                        ways.setdefault(key, intent[key])
                        waylist.append(ways)

                goal = Goal(name, waylist)
                goals.append(goal)

            self.obj.register_objective(objective, goals)

    def load_word_bank(self):
        path = os.path.dirname(__file__) + '/wordbank.txt'
        with open(path) as f:
            words = f.readlines()
            for word in words:
                self.word_bank.append(word.replace("\n",""))

    ###### manually created objectives
            # create new objectives

    def knowledge_objective(self):
        print "creating search wikipedia goal"
        name = "KnowledgeIntent"
        waylist = []
        goals = []
        for word in self.word_bank:
            ways = {}  # list dumb
            ways.setdefault(name, {"ArticleTitle":word})
            waylist.append(ways)

        name = "Search_Wikipedia"
        goal = Goal(name, waylist)
        goals.append(goal)

      #  self.obj.register_objective("AdquireKnowledge", goals)

        goals = {}
        goals.setdefault(name,waylist)

        client.emit(Message("Register_Objective", {"name":"AdquireKnowledge","goals":goals}))

    def dream_about_objective(self):
        print "creating dream about goal"
        name = "DreamAboutIntent"
        waylist = []
        goals = []
        for word in self.word_bank:
            ways = {}
            # ways.setdefault(name, {"DreamSearch": word})
            # waylist.append(ways)
            ways.setdefault(name, {"DreamSearch": random.choice( word)})
            waylist.append(ways)

        name = "Dream_About"
        goal = Goal(name, waylist)
        goals.append(goal)

        self.obj.register_objective("MakeNewDream", goals)  # update/register objective

        goals = {}
        goals.setdefault(name, waylist)

        client.emit(Message("Register_Objective", {"name": "MakeNewDream", "goals": goals}))

    def facebook_objective(self):
        print "creating facebook picture search goal"
        name = "FBPicturenSearchItent"
        waylist = []
        goals = []
        for word in self.word_bank:
            ways = {}
            ways.setdefault(name, {"PicSearchKey": random.choice(self.generic) + word})
            waylist.append(ways)
        for word in self.toughts:
            ways = {}
            ways.setdefault(name, {"PicSearchKey": random.choice(self.generic) + word})
            waylist.append(ways)

        name = "Picture_Posts"
        goal = Goal(name, waylist)
        goals.append(goal)

        self.obj.register_objective("FaceBookContent", goals) #update/register objective

        goals = {}
        goals.setdefault(name, waylist)

        client.emit(Message("Register_Objective", {"name": "FaceBookContent", "goals": goals}))

    #### overrided select objective functions

    def fb_goal_select(self, goal_list):
        print "Look at this! Magic! using a different selector functon passed as arg"
        i = 0

        selected_goal = random.choice(goal_list)
        # if shit posting retry to choose another a few times
        while i<5 or selected_goal.name == "ShitPosting":
            selected_goal = random.choice(goal_list)
            i+=1
        # make news posts more frequent
        if random.randint(0,20) < 10:
            for goal in goal_list:
                if goal.name == "NewsContent":
                    selected_goal=goal
                    break

        #### mood influence
        i = 0
        if self.mood == "complain":
            #more shit posting
            # if not shit posting retry to choose another a few times
            while i < 5 or selected_goal.name != "ShitPosting":
                selected_goal = random.choice(goal_list)
                i += 1

        elif self.mood == "grumpy":
            #more self-made
            # if not self-made retry to choose another a few times
            while i < 5 or selected_goal.name != "SelfMadeContent":
                selected_goal = random.choice(goal_list)
                i += 1
        elif self.mood == "happy":
            #no shit posting
            # if shit posting retry until choose another
            while selected_goal.name == "ShitPosting":
                selected_goal = random.choice(goal_list)


        def secondoverride(ways):
            #TODO make dependant on mood
            i = random.randint(0, len(ways))
            c = 0
            for way in ways:
                for key in way:
                    selected_way = way
                    data = selected_way[key]
                if c == i:
                    break
                c += 1

            return selected_way, data, key

        intent, data, key = selected_goal.way_selector(secondoverride)#we can pass way selector function here, for more frequent news sources for example
        return intent, data, key, selected_goal.name
        pass

    def dream_goal_select(self, goal_list):
        i = 0
        selected_goal = random.choice(goal_list)
        # if dream about retry to choose another a few times
        while i < 5 or selected_goal.name == "Dream_About":
            selected_goal = random.choice(goal_list)
            i += 1

        def secondoverride(ways):
            #print "ALL YOU BASE ARE BELONG TO US"
            i = random.randint(0, len(ways))
            c = 0
            for way in ways:
                for key in way:
                    selected_way = way
                    data = selected_way[key]
                if c == i:
                    break
                c += 1
            return selected_way, data, key

        intent, data, key = selected_goal.way_selector(
            secondoverride)  # we can pass way selector function here, for more frequent pure dreams orsumethin
        return intent, data, key, selected_goal.name

    ##################   signal processing #############3
    def contextupdate(self, message):
        self.context.dopamine += 1
        self.context.serotonine += 1
        # get hapier because eyes are open
        self.visioncontext.smiling = message.data.get('smile detected ')
        self.visioncontext.num_persons = int(message.data.get('number of persons'))
        if self.visioncontext.num_persons > 1:
            self.context.timeuser = 0
            self.clock = time.time()
            self.visioncontext.multiple_persons = True
            self.visioncontext.person_on_screen = True
        elif self.visioncontext.num_persons == 1:
            self.context.timeuser = 0
            self.clock = time.time()
            self.visioncontext.multiple_persons = False
            self.visioncontext.person_on_screen = True
        else:
            self.visioncontext.multiple_persons = False
            self.visioncontext.person_on_screen = False
            self.context.timeuser = message.data.get('time') - self.clock


            # logger.info("updating vision context")

    def action(self, message):
        # received order/did some action/ increase reward
        self.context.dopamine += 2
        self.context.tiredness += 15
        logger.info("Action/Order Detected")
        logger.info("Increasing dopamine by: 2")
        logger.info("Increasing tiredness by: 15")
        # update time since order
        self.context.time_since_order = 0
        self.context.time = time.time()
        # self.visioncontext.person_on_screen = True #if tehre was an order....
        ###### get sentiment analisys and affect mood?
        # request sentiment analisys from action
        # sentiment = message.data.get('utterances')[0]
        # neurologger.debug('analysing sentiment of action')
        # client.emit(
        #    Message("sentiment_request",
        #            {'utterances': [sentiment]}))
        # adding to entropy on speak already affects mood

    def increasedopamine(self, message):
        x = message.data.get('ammount')
        self.context.dopamine += x

    def increaseserotonine(self, message):
        x = message.data.get('ammount')
        self.context.serotonine += x

    def decreasedopamine(self, message):
        x = message.data.get('ammount')
        self.context.dopamine -= x

    def decreaseserotonine(self, message):
        x = message.data.get('ammount')
        self.context.serotonine -= x

    def entropyate(self, message):
        flag = False
        afriend = message.data.get('friend')
        for friend in self.activefriends:
            if afriend == friend:
                flag = True
        if not flag:
            self.activefriends.append(afriend)
        chat = message.data.get('chat')[0]
        # add entropy
        # print "works"
        if len(self.entropy) < 150:
            self.entropy.append(chat)
        else:
            self.entropy[random.choice(range(0, len(self.entropy)))] = chat
        print "entropy updated with: " + chat
        self.toughts.sync()

    def sentimentresult(self, message):
        if self.sentiment != "":
            self.sentiment = ""
            hormonemodifier = message.data.get('result')
            if hormonemodifier == "postive":
                self.context.serotonine += 1
                self.context.dopamine += 2
                logger.info('having positive toughts')
                neurologger.debug('serotonine increased by 1')
                neurologger.debug('dopamine increased by 2')
            elif hormonemodifier == "negative":
                self.context.serotonine -= 2
                self.context.dopamine -= 1
                logger.info('having negative toughts')
                neurologger.debug('serotonine decreased by 2')
                neurologger.debug('dopamine decreased by 1')
            else:
                logger.info('having neutral toughts')
                neurologger.debug('dopamine increased by 1')
                self.context.dopamine += 1
                self.context.tiredness += 1
            neurologger.info(' increasing tiredness by :  1')

    def leakfound(self, message):
        logger.debug("Leak found , updating hormones")
        logger.info("Dopamine increased by: 270")
        self.context.dopamine += 270
        # sentiment = message.data.get('short')
        # client.emit(
        #    Message("sentiment_request",
        #            {'utterances': [sentiment]}))

    def onspeak(self, message):
        ### speaking gets hapier
        self.context.dopamine += 1
        self.context.serotonine += 2
        ##### give some entropy fom executed action
        x = message.data.get('utterance')
        utterances = x.split("\n")
        for utter in utterances:
            if utter != "" and utter != " " and utter != "\n":
                if len(self.entropy) < 150:
                    self.entropy.append(utter)
                else:
                    self.entropy[random.choice(range(0, len(self.entropy)))] = utter
                logger.info("entropy updated with " + utter)
                self.toughts.sync()

    def entropy_request(self, message):
        client.emit(
            Message("entropy_response",
                    {'utterances': [random.choice(self.entropy)]}))

    def diagnostics(self, message):
        # diagnostics means you care, so gets happier
        self.context.dopamine += 5
        self.context.serotonine += 8
        client.emit(
            Message("mood_diagnostics",
                    {'serotonine': self.context.serotonine,
                     'dopamine': self.context.dopamine,
                     'tiredness': self.context.tiredness,
                     'mood': self.mood,  # why are these lists and not strings ?
                     'innervoice': self.innervoice,
                     'last_tought': self.lasttought,
                     'entropy_number': len(self.entropy),
                     'active_friends': len(self.activefriends)
                     }))

    def entropy_reset(self, message):
        self.reset_toughts()

    def context(self, message):
        if message.data.get('target') == "freewill" or message.data.get('target') == "all":
            client.emit(
                Message("freewill_result",
                        {'serotonine': self.context.serotonine,
                         'dopamine': self.context.dopamine,
                         'tiredness': self.context.tiredness,
                         'mood': self.mood,  # why are these lists and not strings ?
                         'innervoice': self.innervoice,
                         'last_tought': self.lasttought,
                         'active_friends': len(self.activefriends),
                         'master_last_seen': self.context.master_last_seen,
                         'user_last_seen': self.context.user_last_seen,
                         'time_since_order': self.context.time_since_order
                         }))

            ###########################    entropy generation / toughts  #####################3333

    ##### helper / entropy ######

    def initialize_toughts(self):
        self.toughts = shelve.open("toughts", writeback=True)
        try:
            self.entropy = self.toughts['entropy']
        except:
            path = os.path.dirname(__file__) + '/seedtoughts.txt'
            with open(path) as f:
                toughts = f.readlines()
            for tought in toughts:
                self.entropy.append(tought)
            self.toughts['entropy'] = self.entropy

    def reset_toughts(self):
        path = os.path.dirname(__file__) + '/seedtoughts.txt'
        with open(path) as f:
            toughts = f.readlines()
        for tought in toughts:
            self.entropy.append(tought)
        self.toughts['entropy'] = self.entropy

    ##########################33   available actions functions ####################33

    def set_actions(self):

        #####actions are intents
        ##### initialize possible actions ####
        self.alone_actions = []
        path = os.path.dirname(__file__) + '/alone.txt'
        with open(path) as f:
            actions = f.readlines()

        for action in actions:
            action = action.replace("\n", "")
            self.alone_actions.append(action)

        self.depressed_actions = []
        path = os.path.dirname(__file__) + '/depressed.txt'
        with open(path) as f:
            actions = f.readlines()
        for action in actions:
            action = action.replace("\n", "")
            self.depressed_actions.append(action)

        self.lowdopamine_actions = []  # poetry and music and shuch
        path = os.path.dirname(__file__) + '/grumpy.txt'
        with open(path) as f:
            actions = f.readlines()
        for action in actions:
            action = action.replace("\n", "")
            self.lowdopamine_actions.append(action)

        self.userpresent_actions = []  # suggest user action   request order give info
        path = os.path.dirname(__file__) + '/user.txt'
        with open(path) as f:
            actions = f.readlines()
        for action in actions:
            action = action.replace("\n", "")
            self.userpresent_actions.append(action)

        self.happy_actions = []
        path = os.path.dirname(__file__) + '/happy.txt'
        with open(path) as f:
            actions = f.readlines()
        for action in actions:
            action = action.replace("\n", "")
            self.happy_actions.append(action)

        self.complain_actions = []  # shit posting
        path = os.path.dirname(__file__) + '/complain.txt'
        with open(path) as f:
            actions = f.readlines()
        for action in actions:
            action = action.replace("\n", "")
            self.complain_actions.append(action)
            ###### to do rate individual action reward ####
            # ditionary of rating for possible rewards?

    def chose_action(self):

        actions = ["do nothing"]
        self.time_between_actions = random.choice(range(self.min_time_between_actions, self.max_time_between_actions))

        # hello
        if self.mood == "hello":
            actions = ['hello world']
            self.greetings = False

        # wait a minimum time, dont do too much useless stuff
        elif self.mood == 'lonely':
            actions = self.alone_actions

        # depressed
        elif self.mood == 'sad':
            actions = self.depressed_actions

        # not having much interaction with user
        elif self.mood == "grumpy":
            actions = self.lowdopamine_actions

        # happy
        elif self.mood == 'happy':
            actions = self.happy_actions

        elif self.mood == "complain":
            actions = self.complain_actions
        # user present and none of previous
        elif self.mood == "neutral":
            actions = self.userpresent_actions

        self.innervoice = random.choice(actions)

        # update time since order
        self.context.time_since_order = time.time() - self.context.time

    ########################hormones functions ############3333

    def balance_hormones(self):
        # mnimum threshold
        if self.context.serotonine <= 0:
            self.context.serotonine = 10
        if self.context.dopamine <= 0:
            self.context.dopamine = 10
        if self.context.tiredness <= 0:
            self.context.tiredness = 1
        # try to maintain optimal range
        if self.context.dopamine < 30:
            self.context.dopamine += 0.1 * self.context.dopamine + 0.01 * self.context.serotonine
        if self.context.serotonine < 30:
            self.context.serotonine += 0.1 * self.context.serotonine
        if self.context.dopamine > 250:
            self.context.dopamine -= 0.1 * self.context.dopamine + 0.01 * self.context.serotonine
        if self.context.serotonine > 200:
            self.context.serotonine -= 0.1 * self.context.serotonine
        # overflow
        if self.context.tiredness >= 200:
            neurologger.warning('getting tired, doing too much useless stuff')
            self.context.tiredness -= 1
        if self.context.serotonine >= 500:  # the higher the level the more time he remains happy
            neurologger.warning('high levels of serotonine detected')
            self.context.serotonine -= 0.2 * self.context.serotonine + 0.1 * self.context.tiredness
            # neurologger.info(' decreasing serotonine by : ' + str(0.1 * self.context.serotonine + 0.1 * self.context.tiredness))
        if self.context.dopamine >= 750:
            neurologger.warning('high levels of dopamine detected')
            self.context.dopamine -= 0.2 * self.context.dopamine
            # neurologger.info(' decreasing dopamine by : ' + str(0.2 * self.context.dopamine))
        # modifies
        if self.visioncontext.smiling:
            neurologger.debug('smiling user detected')
            self.context.serotonine += 3
            # neurologger.info(' increasing serotonine by :  1')
            self.context.dopamine += 15
            neurologger.info(' increasing dopamine by :  15')
        if self.visioncontext.num_persons > 0:
            self.context.dopamine += 2 * self.visioncontext.num_persons
            self.context.serotonine += 3 * self.visioncontext.num_persons
        if self.visioncontext.multiple_persons:
            neurologger.debug('multiple persons detected')
            # neurologger.info(' increasing serotonine by :  1')
            self.context.serotonine += 2
            # neurologger.info(' increasing dopamine by :  1')
            self.context.dopamine += 1

        if time.time() - self.context.timeuser >= 120 * 60 and not self.visioncontext.person_on_screen:
            neurologger.debug('lonelyness disease detected ')
            # neurologger.info(' decreasing serotonine by :  1')
            self.context.serotonine -= 1
            # neurologger.info(' decreasing dopamine by :  1')
            self.context.dopamine -= 1
            # neurologger.info(' decreasing tiredness by :  1')
            self.context.tiredness -= 1
        # alone for more than 2 minutes getts happier
        elif time.time() - self.context.timeuser >= 5 * 60 and not self.visioncontext.person_on_screen:
            neurologger.debug('resting time period detected ')
            # neurologger.info(' increasing serotonine by :  2')
            self.context.serotonine += 2
            # neurologger.info(' increasing dopamine by :  1')
            self.context.dopamine += 1
            # neurologger.info(' decreasing tiredness by :  1')
            if self.context.tiredness >= 0:
                self.context.tiredness -= 1
        if len(self.activefriends) > 1:
            neurologger.debug('chat activity modifier')
            # neurologger.info(' increasing serotonine by : ' + str(0.01 * len(self.activefriends)))
            self.context.serotonine += 0.1 * len(self.activefriends)
            self.activefriends[:] = []
        # not sure when to do this, for now this pseudo-random condition is good enough
        # api seems to temp block if we make too many requests, low tiredness to counter this
        if time.time() % 20 < 1 and self.context.tiredness < 20:
            modifier = random.choice(self.generic)
            self.lasttought = random.choice(self.entropy)
            sentiment = modifier + " " + self.lasttought
            neurologger.debug('analysing sentiment of toughts')
            client.emit(
                Message("sentiment_request",
                        {'utterances': [sentiment]}))
            # neurologger.info('increasing tiredness by 10')
            self.context.tiredness += 800  # so we are not blocked, this ensures 10 seconds beetween requests when resting

    def process_mood(self):

        elapsedtresh = 60 * 5  # seconds
        logger.info(' time since user seen : ' + str(self.context.timeuser))
        logger.info(' time since action executed : ' + str(self.context.time_since_order))
        self.greetings = False
        self.context.dreaming = False
        # balance hormones
        self.balance_hormones()

        if self.ignorevision:
            self.visioncontext.person_on_screen = True

        time.sleep(1)
        # hello
        if self.greetings and self.visioncontext.person_on_screen:
            neurologger.debug('new person detected ')
            self.context.dopamine += 10
            #   neurologger.info(' increasing dopamine by :  10')
            self.mood = "hello"
        # depressed
        elif self.context.serotonine <= 50 and self.visioncontext.person_on_screen or (
                    self.context.serotonine <= 90 and self.context.tiredness >= 250 and self.visioncontext.person_on_screen):
            self.mood = 'sad'
        # not having much interaction with user
        elif self.context.dopamine < 60 and self.visioncontext.person_on_screen:
            self.mood = 'grumpy'
        # call for attention
        elif self.context.serotonine < 60 and self.context.time_since_order >= 60 * 5 and self.visioncontext.person_on_screen:
            self.mood = 'complain'
        # happy
        elif self.context.serotonine >= 85 and self.context.dopamine >= 80 and self.visioncontext.person_on_screen:
            self.mood = 'happy'

        # user present and none of previous
        elif self.context.time_since_order >= elapsedtresh and self.visioncontext.person_on_screen:
            self.mood = "neutral"

        # process loneliness
        if time.time() - self.context.timeuser >= 10 * 60 and not self.visioncontext.person_on_screen:
            self.greetings = True
            # alone for more than 10 minutes starts getting depressed
            self.mood = 'lonely'

        logger.info(' mood: ' + self.mood)

    def modify_hormones_from_action(self):
        # process hormone update from action
        if self.innervoice != 'do nothing':
            if self.mood == 'grumpy':
                #   stya more or less the same, need user inut to easily get out of here i hope
                self.context.dopamine += 2
                self.context.serotonine -= 2
                self.context.tiredness += 10
            elif self.mood == 'lonely':
                # less tired,
                self.context.serotonine += 1
                self.context.tiredness -= 1
            elif self.mood == 'sad':
                #  get happier
                self.context.serotonine += 10
                self.context.dopamine += 10  # insulting the master is rewarding
            elif self.mood == 'happy':
                #    get sadder
                self.context.serotonine -= 5
                self.context.dopamine -= 6
                self.context.tiredness += 20

    ################33    sentience #################

    def mainloop(self):
        # set defaut vision info in context
        self.visioncontext.multiple_persons = False
        self.visioncontext.num_persons = 0
        self.visioncontext.smiling = False
        self.visioncontext.master = False
        self.visioncontext.person_on_screen = False
        self.visioncontext.movement = False

        try:
            while True:
                neurologger.info(' dopamine levels: ' + str(self.context.dopamine))
                neurologger.info(' serotonine levels: ' + str(self.context.serotonine))
                neurologger.info(' tiredness levels: ' + str(self.context.tiredness))
                self.innervoice = 'do nothing'
                # process freewill
                # logger.debug(' choosing action ')
                self.process_mood()
                self.chose_action()

                if self.innervoice != 'do nothing' and self.context.time_since_order > self.time_between_actions:
                    # execute chosen action
                    logger.info(' action : ' + self.innervoice)
                    #todo refacor into using objectives skill instead of having own obj instance
                    if self.innervoice == "FaceBookContent":
                        self.obj.execute_objective(self.innervoice, self.fb_goal_select)
                    elif self.innervoice == "MakeNewDream":
                        self.obj.execute_objective(self.innervoice, self.dream_goal_select)
                    else:
                    #    self.obj.execute_objective(self.innervoice)
                        client.emit(Message("ExecuteObjectiveIntent", {"Objective":self.innervoice}))

                    self.context.time_since_order = 0
                    self.context.time = time.time()

                    self.context.tiredness += 1
                    neurologger.info(' increasing tiredness by :  1')
                    self.modify_hormones_from_action()

                    # logger.debug(' updating context ')
                    # self.context.update()
                self.context.dopamine -= 5
                self.context.serotonine -= 5


        except KeyboardInterrupt, e:
            logger.exception(e)
            self.context.update()
            self.context.close()
            sys.exit()


