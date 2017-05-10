
from time import time, asctime
import random
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from mycroft.configuration import ConfigurationManager

# add skills dir to sys path to import objectives
import sys
from os.path import dirname, exists
sys.path.append(dirname(dirname(__file__)))
from service_objectives import ObjectiveBuilder
from service_intent_layer import IntentParser
from time import sleep
__author__ = "jarbas"


class FreewillSkill(MycroftSkill):

    def __init__(self):
        super(FreewillSkill, self).__init__(name="FreewillSkill")
        self.reload_skill = False
        self.agency = False
        self.word_bank = []

    def initialize(self):
        self.parser = IntentParser(self.emitter)
        self.init_freewill()
        self.init_instincts()
        self.load_word_bank()
        self.build_intents()

    def build_intents(self):
        hormone_data_intent = IntentBuilder("HormoneDataIntent"). \
            require("HormoneDataKeyword").build()

        self.register_intent(hormone_data_intent, self.handle_hormone_levels_intent)

        reset_intent = IntentBuilder("ResetFreewillIntent"). \
            require("ResetFreewillKeyword").build()

        self.register_intent(reset_intent, self.handle_reset_freewill_intent)

        activate_intent = IntentBuilder("ActivateFreewillIntent"). \
            require("ActivateFreewillKeyword").build()

        self.register_intent(activate_intent, self.handle_activate_intent)

        deactivate_intent = IntentBuilder("DeactivateFreewillIntent"). \
            require("DeactivateFreewillKeyword").build()

        self.register_intent(deactivate_intent, self.handle_deactivate_intent)

        mood_intent = IntentBuilder("MoodIntent"). \
            require("MoodKeyword").build()

        self.register_intent(mood_intent, self.handle_mood_intent)

        say_something_intent = IntentBuilder("SaySomethingIntent"). \
            require("SaySomethingKeyword").build()

        self.register_intent(say_something_intent, self.handle_say_something_intent)

        do_something_intent = IntentBuilder("DoSomethingIntent"). \
            require("DoSomethingKeyword").build()

        self.register_intent(do_something_intent, self.handle_do_something_intent)

    def build_objectives(self):
        # TODO
        # become smarter
        # engage user
        # be usefull
        # troll user
        # be funny
        # show something
        # ask me a question
        # tweak self (activate/deactivate/use internal systems)
        pass

    def init_freewill(self):
        self.set_default_context()
        self.agency = True
        self.waiting = False
        self.load_actions()

    def init_instincts(self):
        self.emitter.on("instinct_awareness", self.update_context)
        self.emitter.on("hormone_request", self.handle_hormone_request)
        self.emitter.on("vision_response", self.handle_vision_result)
        self.emitter.on("instinct_noise", self.on_noise_detection)
        self.emitter.on("instinct_movement", self.on_movement)
        self.emitter.on("instinct_bluetooth", self.on_bluetooth)
        self.emitter.on("instinct_sleep", self.on_sleep)
        self.emitter.on("instinct_danger", self.on_danger)
        self.emitter.on("recognizer_loop:utterance", self.on_command)
        self.emitter.on("instinct_tired", self.on_tiredness)
        self.emitter.on("instinct_user_on_sight", self.on_user_on_vision)
        self.emitter.on("instinct_user_smiling", self.on_user_smiling)
        self.emitter.on("instinct_voice", self.on_voice)

    def load_actions(self):
        self.actions = {
            "neutral": [],
            "depressive": [],
            "happy": [],
            "bad": [],
            "irritated": [],
            "creative": [],
            "agressive": []
        }

        actions = ConfigurationManager.get([dirname(__file__) + "/actions.conf"])[
            "Actions"]
        self.log.info("Loading actions from config")
        for mood in actions:
            for action in actions[mood]:
                self.log.info(mood + " : " + str(action))
                self.actions[mood] = action

    # intents

    def handle_activate_intent(self, message):
        self.agency = True
        self.speak_dialog("activate")

    def handle_deactivate_intent(self, message):
        self.agency = False
        self.speak_dialog("deactivate")

    def handle_mood_intent(self, message):
        mood = self.hormones_to_mood()
        if len(self.mood) >= 3: #mood1 mood2 moodx neutral
            self.speak_dialog("mood.extended", {"mood1": mood, "mood2": self.mood[1]})
        else:
            self.speak_dialog("mood", {"mood": mood})

    def handle_hormone_levels_intent(self, message):
        self.speak_dialog("hormone.levels", {"dopamine": self.dopamine, "serotonine": self.serotonine, "norepinephrine": self.norepinephrine})

    def handle_say_something_intent(self, message):
        mood = self.hormones_to_mood()
        if mood == "creative":
            self.speak_dialog("creative")
        elif mood == "agressive":
            self.speak_dialog("agressive")
        elif mood == "irritated":
            self.speak_dialog("irritated")
        elif mood == "happy":
            self.speak_dialog("happy")
        elif mood == "bad":
            self.speak_dialog("bad")
        elif mood == "depressive":
            self.speak_dialog("depressive")
        elif mood == "focused":
            self.speak_dialog("focused")
        else:
            self.speak_dialog("neutral")

    def handle_do_something_intent(self, message):
        self.execute_action()

    def handle_reset_freewill_intent(self, message):
        self.speak_dialog("reset.freewill")
        self.stop()
        self.init_freewill()

    def stop(self):
        pass

    # instincts / bus signals
    def on_danger(self, message):
        # on danger + agressiveness + alertness + concentration + energy + attention +learning
        self.dopamine += 20
        self.norepinephrine += 10
        self.serotonine += 30
        if self.dopamine > 100:
            self.dopamine = 100
        if self.serotonine > 100:
            self.serotonine = 100
        if self.norepinephrine > 100:
            self.norepinephrine = 100

    def on_command(self, message):
        # on order + alertness + attention + concentation + alertness - obsession -compulsion
        self.dopamine += 5
        self.norepinephrine += 10
        self.serotonine -= 2
        if self.dopamine > 100:
            self.dopamine = 100
        if self.serotonine < 0:
            self.serotonine = 0
        if self.norepinephrine > 100:
            self.norepinephrine = 100

    def on_tiredness(self, message):
        # TODO make tired when cpu usage is too big
        # on tiredness reset hormone levels
        self.reset_hormones()
        # TODO stop secondary systems -> lilacs_curiosity, lilacs_chatbot, face book chat, sentiment analisys, deepdream
        # stop sleep
        self.stop_sleep()

    def on_sleep(self, message):
        # TODO ordered sleep or alone detected for too much time
        # TODO LILACS Node maintenance / addition
        # TODO deep dreaming about nodes and new nodes
        pass

    def on_utterance(self, message):
        # TODO sentiment analisys interaction
        # TODO influence hormones
        # abort sleep
        self.stop_sleep()
        # TODO check last_seen timestamp and is above thresh query user
        person = "unknown"
        # update time since user seen
        self.person_log[person]["utterance"].append(asctime())

    def on_noise_detection(self, message):
        # TODO  sound analisys service implementation
        # abort sleep
        self.stop_sleep()
        # say hello
        self.speak_dialog("maybe.person")
        person = "unknown"
        # update time since user seen
        self.person_log[person]["noise"].append(asctime())

    def on_voice(self, message):
        # abort sleep
        self.stop_sleep()
        # say hello
        self.speak_dialog("new.person")
        # TODO voice recognition for user
        person = "unknown"
        # ask who it is
        if person == "unknown":
            self.speak_dialog("id.person")
        # update time since user seen
        self.person_log[person]["voice"].append(asctime())

    def on_bluetooth(self, message):
        # TODO bluetooth id service
        # abort sleep
        self.stop_sleep()
        # say hello
        self.speak_dialog("new.person")
        # TODO bluetooth id
        person = "unknown"
        # ask who it is
        if person == "unknown":
            self.speak_dialog("id.person")
        # update time since user seen
        self.person_log[person]["bluetooth"].append(asctime())

    def on_user_on_vision(self, message):
        # on new user in sight
        # abort sleep
        self.stop_sleep()
        # say hello
        self.speak_dialog("new.person")
        # TODO face recognition
        person = "unknown"
        # ask who it is
        if person == "unknown":
            self.speak_dialog("id.person")
        # update time since user seen
        self.person_log[person]["vision"].append(asctime())

    def on_user_smiling(self, message):
        # increase happy, decrease danger
        self.dopamine += 10
        self.norepinephrine -= 20
        self.serotonine += 10
        if self.dopamine > 100:
            self.dopamine = 100
        if self.serotonine > 100:
            self.serotonine = 100
        if self.norepinephrine < 0:
            self.norepinephrine = 0

    def on_movement(self, message):
        # abort sleep
        self.stop_sleep()
        # ask if someone's there
        self.speak_dialog("maybe.person")
        person = "unknown"
        # update time since user seen
        self.person_log[person]["movement"].append(asctime())

    def handle_vision_result(self, message):
        # TODO process context from message
        self.waiting = False

    def handle_hormone_request(self, message):
        response = Message("hormone_response", {"dopamine":self.dopamine, "serotonine":self.serotonine, "norepinephrine":self.norepinephrine})
        self.emitter.emit(response)

    # internal
    def choose_action(self):
        self.update_context()
        actions = []
        if self.mood[0] == "neutral":
            actions.append(dict(self.actions["neutral"]))
        else:
            for mood in self.mood:
                actions.append(dict(self.actions[mood]))
        if len(actions) > 0:
            selected = random.choice(actions)
        else:
            selected = []
        return selected

    def execute_action(self):
        # choose action
        action = self.choose_action()
        intent = action.keys()[0]
        data = action[intent]
        # intent to skill id
        skill_id = self.parser.get_skill_id(intent)
        intent = str(skill_id) + ":" + intent
        # execute
        self.emitter.emit(Message(intent, data))

    def stop_sleep(self):
        # TODO abort deep-dream / LILACS maintenance / whatever
        pass

    def agency_loop(self):
        while self.agency:
            self.execute_action()
            # TODO decide how much time to wait until next action
            sleep(60)

    def load_word_bank(self):
        word_bank = []
        path = dirname(__file__) + '/wordbank.txt'
        with open(path) as f:
            words = f.readlines()
            for word in words:
                word_bank.append(word.replace("\n", ""))

        self.word_bank = word_bank

    # hormones
    def reset_hormones(self):
        # functions of each hormone

        # dopamine
        # + reward
        # + dopamine
        # serotonine
        # + obsession
        # + compulsion
        # + memory
        # norepinephrine
        # + energy
        # + concentration
        # + alertness
        # serotonine + dopamine
        # + agression
        # + learning
        # dopamine + norepinephrine
        # + attention
        # norepinephine + serotonine
        # + anxiety
        # + impulse
        # + irritability

        self.dopamine = 50
        self.serotonine = 50
        self.norepinephrine = 50

    def hormones_to_mood(self):
        self.mood = []
        if self.serotonine > 75 and self.dopamine > 75:
            self.mood.append("happy")
        elif self.serotonine < 40 and self.dopamine < 40:
            self.mood.append("bad")
        if self.norepinephrine < 40:
            self.mood.append("creative")
        elif self.norepinephrine > 70:
            self.mood.append("focused")
        if self.dopamine > 75 and self.norepinephrine > 75:
            self.mood.append("agressive")
        if self.serotonine > 80 and self.norepinephrine > 80:
            self.mood.append("irritated")
        if self.serotonine < 30 or self.dopamine < 30:
            self.mood.append("depressive")
        self.mood.append("neutral")
        return self.mood[0]

    # freewill context
    def set_default_context(self):
        # self
        self.reset_hormones()
        self.hormones_to_mood()
        self.alone = True
        # user:list of timestamps
        self.person_log = {"unknown":{"voice":[], "vision":[], "bluetooth":[], "utterance":[], "movement":[], "noise":[]},
                           "master":{"voice":[], "vision":[], "bluetooth":[], "utterance":[], "movement":[], "noise":[]}}
        # vision  processing
        self.master_present = False
        self.person_on_screen = False
        self.was_person_on_screen_before = False
        self.movement = False
        self.multiple_persons = False
        self.smiling = False

    def update_context(self):
        # request context data (vision)
        # TODO analise timestamps
        # process hormones
        self.request_vision()
        self.hormones_to_mood()
        return

    def request_vision(self):
        self.waiting = True
        self.emitter.emit(Message("vision_request"))
        start_time = time()
        seconds = 0
        while self.waiting and seconds <= 20:
            seconds = time() - start_time
        self.waiting = False


def create_skill():
    return FreewillSkill()




