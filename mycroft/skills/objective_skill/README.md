Objective Skill
=====================

A configurable skill that allows the user to configure multiple ways to achieve same result

In the objectives.config file you define keywords with a list of actions that can be taken to achieve the same objective

i tought it was best to have a separate config instead of spamming mycroft config

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


# Example Config:

```json
  {
  "Objectives": {
      "EngageMaster":{
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
      "AnnoyMaster":{
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



# more ways to code objectives

An example wiki objective has been coded with ObjectiveBuilder, this creates a bunch of ways with different searchterms and searches wikipedia, this is used in small talk goal to say random stuff, a way may also be other objective

There is a way to overload the selector function for both ways and goals, but i havent still worked out how to configure this, used in freewill service to select fb posts

Objectives can be registered from other skills/programs by sending a message to messagebus with the format

        Message("Register_Objective", {"name":name,"goals":goals})

 # future

 probabilities for each way executing, integration with feedback skill to adjust probabilities
