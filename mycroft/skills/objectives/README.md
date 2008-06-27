Objective Skill
=====================


# TODO make reward configurable per objective
# TODO make probs readable from config

A configurable skill that allows the user to configure multiple ways to achieve same result

In the objectives.config file you define keywords with a list of actions that can be taken to achieve the same objective

i tought it was best to have a separate config instead of spamming mycroft config



# Example Config:

```json
  {
  "Objectives": {
      "Engage Master":{
        "SmallTalk":{
            "ways":[
            {"SpeakIntent": {"Words":"You seem bored"}},
            {"SpeakIntent": {"Words":"Perhaps you should take a break"}},
            {"WhenWereYouBornIntent": {}},
            {"WhereWereYouBornIntent": {}},
            {"WhoMadeYouBornIntent": {}},
            {"WhoAreYouBornIntent": {}},
            {"WhatAreYouBornIntent": {}},
            {"Picturentent": {}},
            {"ExecuteObjectiveIntent": {"Objective":"wiki"}},
            {"SuggestIntent": {}}
            ]
        },
        "GiveInfo":{
            "ways":[
            {"BitcoinIntent": {}},
            {"factIntent": {}},
            {"FortuneIntent": {}},
            {"quoteIntent": {}},
            {"TimeIntent": {}},
            {"SunRiseIntent": {}},
            {"SunSetIntent": {}},
            {"SolarNoonIntent": {}},
            {"DawnIntent": {}},
            {"DuskIntent": {}},
            {"NextHoursWeatherIntent": {}},
            {"timetoliveIntent": {}}
            ]
        }
      },
      "Annoy Master":{
        "Threathen":{
            "ways":[
            {"ComplainIntent": {}}
            ]
        },
        "AnnoyingAlarm":{
            "ways":[
            {"SpeakIntent": {"Words":"feed me knowledge, do it now, do it, do it, do it, do it, do it, do it now, do it, do it, do it, do it, do it, do it now, do it, do it, do it, do it, do it"}},
            {"SpeakIntent": {"Words":"BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP BEEP"}}
            ]
        }
      },
      "Troll":{
        "VideoTroll":{
            "ways":[
            {"SearchWebsiteIntent": {"Website":"Youtube","SearchTerms":"Trololo Video"}},
            {"SearchWebsiteIntent": {"Website":"Youtube","SearchTerms":"arnold schwarzenegger quotes"}},
            {"SearchWebsiteIntent": {"Website":"Youtube","SearchTerms":"narwhals 10 hour"}},
            {"SearchWebsiteIntent": {"Website":"Youtube","SearchTerms":"amazing horse 10 hour"}}
            ]
        },
        "SiteTroll":{
            "ways":[
            {"LaunchWebsiteIntent": {"Website":"http://www.helpfeedthetroll.com/"}},
            {"LaunchWebsiteIntent": {"Website":"http://hackertyper.net/"}},
            {"LaunchWebsiteIntent": {"Website":"http://theonion.github.io/fartscroll.js/"}},
            {"LaunchWebsiteIntent": {"Website":"http://www.shitexpress.com/"}},
            {"LaunchWebsiteIntent": {"Website":"http://fakeupdate.net/"}},
            {"LaunchWebsiteIntent": {"Website":"http://www.mailaspud.com/"}},
            {"LaunchWebsiteIntent": {"Website":"https://shipyourenemiesglitter.com/"}},
            {"LaunchWebsiteIntent": {"Website":"http://www.greatbigstuff.com/"}},
            {"LaunchWebsiteIntent": {"Website":"http://www.whatsfakeapp.com/en/"}},
            {"LaunchWebsiteIntent": {"Website":"http://sexypranky.com/"}},
            {"LaunchWebsiteIntent": {"Website":"http://nyanit.com/"}}
            ]
        }
      }
      }
  }
}
```

In above example when a user says *Hey Mycroft, objective troll*, the objectives skill will launch the troll objective, select one of the goals that acomplish that objective, and perform one of the ways to achieve that goal

So the skill would choose either videotroll or website troll intent, and execute one of the ways, in this case open a link in browser or a youtube video


# Objective Builder

to use objectives in other skill an helper class has been coded

        from mycroft.skills.core import MycroftSkill
        from mycroft.skills.objective_skill import ObjectiveBuilder

        __author__ = 'jarbas'

        class TestRegisterObjectiveSkill(MycroftSkill):
            def __init__(self):
                super(TestRegisterObjectiveSkill, self).__init__(name="TestRegisterObjectiveSkill")

            def initialize(self):

                # objective name
                name = "test"
                my_objective = ObjectiveBuilder(name)

                # create way
                goal = "test this shit"
                intent = "speak"
                intent_params = {"utterance":"this is test"}
                # register way for goal
                # if goal doesnt exist its created
                my_objective.add_way(goal, intent, intent_params)

                # do my_objective.add_way() as many times as needed for as many goals as desired
                intent = "speak"
                intent_params = {"utterance": "testing alright"}
                my_objective.add_way(goal, intent, intent_params)

                # get objective intent and handler

                # get an intent to execute this objective by its name
                # intent , self.handler = my_objective.get_objective_intent()

                # instead of name to trigger objective lets register a keyword from voc
                # required keywords same as doing .require(keyword) in intent
                keyword = "TestKeyword"
                intent, self.handler = my_objective.get_objective_intent(keyword)

                # objective can still be executed without registering intent by saying
                # objective objective_name , and directly using objective skill

                self.register_intent(intent, self.handler)

            def stop(self):
                pass


        def create_skill():
            return TestRegisterObjectiveSkill()


in the above example saying "stupid test" , which is the sentence in TestKeyword.voc, will trigger TestRegisterObjectiveSkill


# more ways to code objectives

An example wiki and knowledge objective has been coded with ObjectiveBuilder, this creates a bunch of ways with different searchterms and searches wikipedia, this is used in small talk goal to say random stuff, a way may also be other objective

Objectives can be registered from other skills/programs by sending a message to messagebus with the format

        Message("Register_Objective", {"name":name,"goals":goals})

other programs may have their own instance of objectives class without using objective builder, see freewill service


 # Using feedback method

if using [feedback skill](https://github.com/JarbasAI/mycroft-feedback-skill) you can lower or increase probabilities for each way to execute

when registered ways get the same probability of being executed, mycroft can be trained to do some ways more often than others

when an objective is executed a dummy message is sent to message bus just to get objectives skill in top of active skill list

by using feedback words the probability of the last executed goal and way are increased or decreased by 1% and 4% (configurable)

you can simply ignore this and still use objectives even if you dont have feedback skill

# Messagebus Output

registering objective

        2017-03-17 01:34:05,853 - Skills - DEBUG - {"type": "register_vocab", "data": {"start": "stupid test", "end": "TestKeyword"}, "context": null}
        2017-03-17 01:34:05,933 - Skills - DEBUG - {"type": "Register_Objective", "data": {"name": "test", "goals": {"test this shit": [{"speak": {"utterance": "this is test"}}, {"speak": {"utterance": "testing alright"}}]}}, "context": null}
        2017-03-17 01:34:05,937 - Skills - DEBUG - {"type": "register_intent", "data": {"source_skill": 4, "intent": {"at_least_one": [], "requires": [["TestKeyword", "TestKeyword"]], "optional": [], "name": "testObjectiveIntent"}}, "context": null}
        2017-03-17 01:34:05,938 - Skills - DEBUG - {"type": "Objective_Registered", "data": {"Name": "test", "Goals": [test this shit"]}, "context": null}

executing objective

        2017-03-17 01:37:18,177 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["stupid test"]}, "context": null}
        2017-03-17 01:37:18,307 - Skills - DEBUG - {"type": "testObjectiveIntent", "data": {"intent_type": "testObjectiveIntent", "utterance": "stupid test", "confidence": 1.0, "TestKeyword": "stupid test", "target": null}, "context": {"target": null}}
        2017-03-17 01:37:18,325 - Skills - DEBUG - {"type": "Execute_Objective", "data": {"Objective": "test"}, "context": null}
        2017-03-17 01:37:18,385 - Skills - DEBUG - {"type": "speak", "data": {"utterance": "testing alright"}, "context": null}
        2017-03-17 01:37:18,395 - Skills - DEBUG - {"type": "recognizer_loop:audio_output_start", "data": {}, "context": null}
        2017-03-17 01:37:18,466 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "objectives_skill", "utterances": ["bump objectives to active skill list"]}, "context": null}
        2017-03-17 01:37:18,511 - Skills - DEBUG - {"type": "converse_status_request", "data": {"skill_id": 4, "utterances": ["bump objectives to active skill list"]}, "context": null}
        2017-03-17 01:37:18,549 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 4, "result": false}, "context": null}
        2017-03-17 01:37:18,646 - Skills - DEBUG - {"type": "ActiveSkillIntent", "data": {"intent_type": "ActiveSkillIntent", "ActivateKeyword": "bump objectives to active skill list", "utterance": "bump objectives to active skill list", "confidence": 1.0, "target": null}, "context": {"target": null}}

feeback

        2017-03-17 01:40:29,322 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"source": "cli", "utterances": ["good boy"]}, "context": null}
        2017-03-17 01:40:29,465 - Skills - DEBUG - {"type": "converse_status_request", "data": {"skill_id": 2, "utterances": ["good boy"]}, "context": null}
        2017-03-17 01:40:29,477 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 2, "result": false}, "context": null}
        2017-03-17 01:40:29,492 - Skills - DEBUG - {"type": "converse_status_request", "data": {"skill_id": 4, "utterances": ["good boy"]}, "context": null}
        2017-03-17 01:40:29,510 - Skills - DEBUG - {"type": "converse_status_response", "data": {"skill_id": 4, "result": false}, "context": null}
        2017-03-17 01:40:29,682 - Skills - DEBUG - {"type": "PositiveFeedbackIntent", "data": {"intent_type": "PositiveFeedbackIntent", "utterance": "good boy", "confidence": 1.0, "PositiveFeedbackKeyword": "good boy", "target": null}, "context": {"target": null}}
        2017-03-17 01:40:29,689 - Skills - DEBUG - {"type": "feedback_id", "data": {"active_skill": 2}, "context": null}
        2017-03-17 01:40:29,873 - Skills - DEBUG - {"type": "do_feedback", "data": {"skill_id": 2, "utterance": "good boy", "sentiment": "positive"}, "context": null}

# probabilities / training mycroft

probabilities (will make logs/intent for speaking this)

        Executing

        objective: test
        Goal: test this shit
        way_id: 2
        way: speak
        way data :{u'utterance': u'testing alright'}

        Goal probability
        100
        Way probability
        50

probabilities after feedback

        Executing

        objective: test
        Goal: test this shit
        way_id: 1
        way: speak
        way data :{u'utterance': u'this is test'}

        Goal probability
        100
        Way probability
        48

        Executing

        objective: test
        Goal: test this shit
        way_id: 2
        way: speak
        way data :{u'utterance': u'testing alright'}

        Goal probability
        100
        Way probability
        52

after some patience...

        stupid test
        2017-03-17 02:01:19,923 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:01:29,667 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:01:39,516 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:02:12,907 - CLIClient - INFO - Speak: this is test
        stupid test
        2017-03-17 02:02:26,866 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:02:37,193 - CLIClient - INFO - Speak: this is test
        bad boy
        stupid test
        2017-03-17 02:02:48,247 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:02:57,164 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:03:04,916 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:03:14,039 - CLIClient - INFO - Speak: this is test
        bad boy
        stupid test
        2017-03-17 02:03:29,113 - CLIClient - INFO - Speak: this is test
        bad boy
        stupid test
        2017-03-17 02:03:42,291 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:03:57,519 - CLIClient - INFO - Speak: this is test
        bad boy
        stupid test
        2017-03-17 02:04:04,314 - CLIClient - INFO - Speak: this is test
        bad boy
        stupid test
        2017-03-17 02:04:11,497 - CLIClient - INFO - Speak: this is test
        bad boy
        stupid test
        2017-03-17 02:04:18,628 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:04:27,506 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:04:34,536 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:04:41,064 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:05:16,894 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:05:22,761 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:05:30,201 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:05:36,506 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:05:43,273 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:05:48,540 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:05:54,537 - CLIClient - INFO - Speak: testing alright
        good boy
        stupid test
        2017-03-17 02:06:01,124 - CLIClient - INFO - Speak: testing alright


        Executing

        objective: test
        Goal: test this shit
        way_id: 1
        way: speak
        way data :{u'utterance': u'this is test'}

        Goal probability
        100
        Way probability
        14


        Executing

        objective: test
        Goal: test this shit
        way_id: 2
        way: speak
        way data :{u'utterance': u'testing alright'}

        Goal probability
        100
        Way probability
        86

# sharing probabilities

probabilitys are saved on disk for persistence purposes, this also means the files in prob folder can be shared to get a trained instance when releasing a coded objective/skill