Objective Skill
=====================

A configurable skill that allows the user to configure multiple ways to achieve same result

In the objectives.config file you define keywords with a list of actions that can be taken to achieve the same objective

i tought it was best to have a separate config instead of spamming mycroft config

Example Config:

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

An example wiki objective has been coded in the skill, this created a bunch of ways with different searchterms and searches wikipedia, this is used in small talk goal to say random stuff, a way may also be other objective

There is a way to overload the selector function for both ways and goals, but i havent still worked out how to configure this without using IFTTT in the code for each over-rided objective

Objectives can be registered from other skills/programs by sending a message to messagebus with the format

        Message("Register_Objective", {"name":name,"goals":goals})