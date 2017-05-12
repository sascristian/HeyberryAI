from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill

import random, math, os, sys
from os.path import dirname
path= dirname(dirname(__file__))
sys.path.append(path)
# import intent layers
from service_intent_layer import IntentParser

__author__ = 'jarbas'


class MathQuestions:
    def __init__(self):
        self.questions = []
        self.init_questions()

    def ft(self, text, randints, randdec, randsgnint):
        return text.format(randints, randdec, randsgnint)

    def init_questions(self):
        # TODO more questions / equation types
        self.questions.append(["Convert {1[0]:0.2f} centimeters into meters.", "{1[0]}*0.01"])
        self.questions.append([
            "What is the length of the line segment with endpoints ({2[1]},{2[2]}) and ({2[3]},{2[4]})?",
            "math.sqrt(({2[3]}-{2[1]})**2 + ({2[4]}-{2[2]})**2)"])
        self.questions.append(["Solve for x in the equation {2[1]}x - {0[2]} = {2[7]}", "({2[7]}+{0[2]})*1./{2[1]}"])

    def ask_question(self):
        question = random.choice(self.questions)
        answer = question[1]
        question = question[0]
        question, answer = self.answer_question(question, answer)
        return question, answer

    def answer_question(self, question, answer):
        randints = []
        randdec = []
        randsgnint = []

        for a in range(1,
                       11):  # Creates three arrays of whole numbers, random decimals, and random signed integers for use in questions.
            randints.append(random.randint(1, 10))
            randdec.append(math.sqrt(random.randint(1, 100)) * random.randint(1, 10))
            randsgnint.append(random.randint(-10, 10))

        question = self.ft(question, randints, randdec,
                            randsgnint)  # The function replaces all symbols in the question with the correct number types
        answer = eval(self.ft(answer, randints, randdec,
                                   randsgnint))  # This stores the numerical answer based on the string provided with the answer.

        return question, answer


class TriviaQuestions:
    def __init__(self):
        self.questions = {} #"categorie" : [[question, answer], [question, answer]]
        self.categories = ["general", "geography", "history", "literature", "movies", "music", "science", "sports"]
        self.load_questions()

    def load_questions(self):
        for cat in self.categories:
            questions = []
            answers = []
            path = os.path.dirname(__file__) + '/' + cat + ".txt"
            with open(path) as f:
                lines = f.readlines()
                i = 1
                for line in lines:
                    if i % 2 == 0:
                        answers.append(line)
                    else:
                        questions.append(line)
                    i += 1

            self.questions[cat] = []
            for i in range(len(questions)):
                self.questions[cat].append([questions[i], answers[i]])

    def ask_question(self, categorie="general"):
        question = random.choice(self.questions[categorie])
        answer = question[1]
        question = question[0]
        return question, answer

class TriviaSkill(MycroftSkill):

    def __init__(self):
        super(TriviaSkill, self).__init__(name="TriviaSkill")
        # initialize your variables
        self.quizz = False
        self.continuous = False
        self.math = MathQuestions()
        self.trivia = TriviaQuestions()
        self.answer = None
        self.categorie = "all"
        self.categories = ["math", "general", "geography", "history", "literature", "movies", "music", "science", "sports"]

    def initialize(self):
        self.intent_parser = IntentParser(self.emitter)
        # register intents
        self.build_intents()

    def build_intents(self):
        # build
        trivia_intent = IntentBuilder("TriviaGameIntent") \
            .require("triviastart").build()
        cat_intent = IntentBuilder("TriviaCategorieIntent") \
            .require("Categorie").build()
        geography_intent = IntentBuilder("GeographyQuestionIntent") \
            .require("geography").build()
        history_intent = IntentBuilder("HistoryQuestionIntent") \
            .require("history").build()
        literature_intent = IntentBuilder("LiteratureQuestionIntent") \
            .require("literature").build()
        math_intent = IntentBuilder("MathQuestionIntent") \
            .require("math").build()
        movie_intent = IntentBuilder("MovieQuestionIntent") \
            .require("movie").build()
        music_intent = IntentBuilder("MusicQuestionIntent") \
            .require("music").build()
        science_intent = IntentBuilder("ScienceQuestionIntent") \
            .require("science").build()
        sports_intent = IntentBuilder("SportsQuestionIntent") \
            .require("sports").build()
        general_intent = IntentBuilder("QuestionIntent") \
            .require("question").build()
        stop_intent = IntentBuilder("StopTriviaIntent") \
            .require("stoptrivia").build()

        # register
        self.register_intent(trivia_intent,
                             self.handle_trivia_game_start)
        self.register_intent(geography_intent,
                             self.handle_geography_question)
        self.register_intent(history_intent,
                             self.handle_history_question)
        self.register_intent(literature_intent,
                             self.handle_literature_question)
        self.register_intent(math_intent,
                             self.handle_math_question)
        self.register_intent(movie_intent,
                             self.handle_movies_question)
        self.register_intent(music_intent,
                             self.handle_music_question)
        self.register_intent(science_intent,
                             self.handle_science_question)
        self.register_intent(sports_intent,
                             self.handle_sports_question)
        self.register_intent(general_intent,
                             self.handle_general_question)
        self.register_intent(cat_intent,
                             self.handle_change_cat_intent)
        self.register_intent(stop_intent,
                             self.handle_stop_quizz)

    def random_question(self):
        if self.categorie == "math":
            self.quizz = True
            question, self.answer = self.math.ask_question()
        elif self.categorie == "all":
            self.quizz = True
            cat = random.choice(self.categories)
            if cat == "math":
                question, self.answer = self.math.ask_question()
            else:
                question, self.answer = self.trivia.ask_question(cat)
        else:
            self.quizz = True
            question, self.answer = self.trivia.ask_question(self.categorie)

        return question

    def handle_trivia_game_start(self, message):
        if self.categorie == "all":
            self.categorie = random.choice(self.categories)
        self.speak_dialog("trivia", {"cat": self.categorie, "question":self.random_question()})
        self.continuous = True

    def handle_change_cat_intent(self, message):
        cat = message.data["Categorie"]
        if cat in self.categories:
            self.categorie = cat
            self.speak_dialog("categorie", {"cat": self.categorie})
        else:
            self.speak(cat + " is an invalid categorie")

    def handle_math_question(self, message):
        self.quizz = True
        question, self.answer = self.math.ask_question()
        self.speak(question, expect_response=True)

    def handle_sports_question(self, message):
        self.quizz = True
        question, self.answer = self.trivia.ask_question("sports")
        self.speak(question, expect_response=True)

    def handle_movies_question(self, message):
        self.quizz = True
        question, self.answer = self.trivia.ask_question("movies")
        self.speak(question, expect_response=True)

    def handle_music_question(self, message):
        self.quizz = True
        question, self.answer = self.trivia.ask_question("music")
        self.speak(question, expect_response=True)

    def handle_literature_question(self, message):
        self.quizz = True
        question, self.answer = self.trivia.ask_question("literature")
        self.speak(question, expect_response=True)

    def handle_history_question(self, message):
        self.quizz = True
        question, self.answer = self.trivia.ask_question("history")
        self.speak(question, expect_response=True)

    def handle_geography_question(self, message):
        self.quizz = True
        question, self.answer = self.trivia.ask_question("geography")
        self.speak(question, expect_response=True)

    def handle_science_question(self, message):
        self.quizz = True
        question, self.answer = self.trivia.ask_question("science")
        self.speak(question, expect_response=True)

    def handle_general_question(self, message):
        self.quizz = True
        question, self.answer = self.trivia.ask_question()
        self.speak(question, expect_response=True)

    def handle_stop_quizz(self, message):
        self.stop()

    def stop(self):
        if self.quizz or self.continuous:
            self.speak("Exiting Quizz mode")
            self.quizz = False
            self.continuous = False
            self.answer = None
            self.categorie = "all"

    def converse(self, transcript, lang="en-us"):
        # check if some of the intents will be handled
        intent, id = self.intent_parser.determine_intent(transcript[0])
        if id == self.skill_id:
            # intent from this skill will be triggered
            # only stop, change categorie, specific questions intents available
            pass
        elif self.continuous and self.answer is not None:
            self.speak_dialog("trivianext", {"ans" : str(self.answer), "question":self.random_question()}, expect_response=True)
            return True
        elif self.quizz and self.answer is not None:
            self.speak("the correct answer is " + str(self.answer), expect_response=True)
            self.quizz = False
            self.answer = None
            return True

        return False


def create_skill():
    return TriviaSkill()