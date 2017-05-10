# Jarbas Core

![alt tag](https://github.com/JarbasAI/jarbas---pygtk---GUI/blob/master/screenshot.jpg)

a fork of mycroft-core , the following things were changed

# Centralized APIs

Lots of APIs are used and sometimes more than once, they were centralized in a single section of the config file

[PR#557](https://github.com/MycroftAI/mycroft-core/pull/557)

# Converse method

This allows any skill to handle an utterance before intent parsing, sets an internal id for each skill

use cases: intent execution interception, passive utterance listening

[PR#539](https://github.com/MycroftAI/mycroft-core/pull/539)

# Intent Parsing and Intent Layers

[Intent Parser and Intent Layers](https://github.com/JarbasAI/service_intent_layer) are tools for continuous dialog

Intent Parser allows any skill to get a intent from an utterance, or the skill to which an intent belongs too

Intent Layers makes it possible to give state to mycroft inside skills, we can switch layers to have different intents active at different times

use cases: continuous dialog, converse method tools

# Objectives

[Objectives](https://github.com/JarbasAI/service_objectives) can be used instead / in additon to intents

An objective is something that can be achieved by any of various goals, a goal is something that can be achieved by any of various ways, a way is an intent and it's parameters

Goals and ways are weighted and the weights can be adjusted

use cases: training mycroft to prefer some actions, randomization

# Vision Service

[Vision service](https://github.com/JarbasAI/service_vision) uses opencv to detect faces, eyes and smiles, can be queried by outside skills for info

Controls webcam and allows to take pictures / apply filters

In the future will handle face recognition / user id

use cases: take pictures, give processed visual info to outside (security skill can warn on face detection if on alert mode)

# Display Service

[Display service](https://github.com/JarbasAI/service_display) allows any skill to display pictures, at the same time allowing user to choose how and where to display them

use cases: dont require skill makers to code image display, allow vocal selection of backend

# Audio Service

Forslunds [audio service](https://github.com/forslund/mycroft-core/tree/audio-service/) was repackaged as a skill, allows user to control audio play and to choose how and where to play

use cases: dont require skill makers to code audio play and control, allow vocal selection of backend

# Freewill Service

This is not to be taken very seriously, mimics an hormonal system to influence "mood" of mycroft, randomly executes an action depending on current mood

use cases: make a cool toy, simulate user presence

# LILACS

Jarbas core uses [LILACS](https://github.com/ElliotTheRobot/LILACS-mycroft-core), a learning and comprehension subsystem, this replaces wolfram alpha fallback mechanism and attempts to implement learning capabilities and memory

# Sentiment Analisys Service

[Sentiment Analisys](https://github.com/JarbasAI/mycroft---sentiment-analisys---skill)  - Classifies sentences into positive and negative, can be queried by other skills


# Other Changes

- blacklisted skills now loaded from config instead of hard-coded
- added priority skills loading, services should be loaded first (in order to not miss messages from other skills)
- standard skills folder is now jarbas_skills, msm may need changes because skill_dir path is hardcoded
- do not install default skills using msm
- created a folder named database that is populated with created/scraped content during jarbas life-time (offline db)
- implement disable speak flag for mute skill


# Included skills by default

Lots of skills are bundled by default with this fork, following list may be outdated

### Basic Skills

        these skills are more or less passive, they are mostly helper skills to be used elsewhere

[Feedback Skill](https://github.com/JarbasAI/mycroft-feedback-skill) - Gives positive or negative feedback to last executed action

[Event Skill](https://github.com/forslund/event_skill) - chains of events , programmable times

[Command Skill](https://github.com/forslund/cmd_skill) - execute system commands


### Entertainment Skills

        skills that entertain you

[Parrot Skill](https://github.com/JarbasAI/mycroft---parrot-skill) - Speaks Everything back to user

[Music Skill](https://github.com/JarbasAI/mycroft-music-skill) - Download and play music from youtube

[Random Quotes Skill](https://github.com/JarbasAI/mycroft---quotes---skill) - Movie Quotes / Number Facts / Time left to live

[Pickup Line Skill](https://github.com/JarbasAI/mycroft---pick-up-line---skill) - Pickup Lines

[Konami Code Skill](https://github.com/JarbasAI/mycroft---konami-code) - cheat code sequence

[Fortune Skill](https://github.com/jaevans/mycroft-fortuneskill) - Tells you your fortune

[Daily Meditation Skill](https://github.com/kfezer/daily_meditation) - Meditation podcast

[Small Talk, Dice, Coin Flip, Rock Paper Scissors Skills](https://github.com/apquinit/mycroft-skills)

[Astronomy Picture of the Day](https://github.com/JarbasAI/mycroft---astronomy-picture-of-teh-day) - Downloads and display NASA astronomy picture of the day

[EPIC Satellite Skill](https://github.com/JarbasAI/mycroft---EPIC-skill) - Near real time Earth satellite imagery

[LILACS Chatbot](https://github.com/ElliotTheRobot/LILACS-mycroft-core/tree/dev/mycroft/skills/LILACS_chatbot) - chatbot mode, intercepts utterances and answers with "crap"

[Troll Objective]() - Attempts to troll user by showing a video or website randomly


### Control Skills

        skills that help you control stuff

[Mute Skill](https://github.com/JarbasAI/mycroft---mute-skill) - Disables and enables speech on demand

[Wallpaper Skill](https://github.com/JarbasAI/mycroft---wallpaper---skill) - download and change wallpapers

[Diagnostics Skill](https://github.com/the7erm/mycroft-skill-diagnostics) - System Info



### Productivity Skills

        skills that help you create/do stuff

[Dictation Skill](https://github.com/JarbasAI/mycroft-dictation-skill) - Writes everything user says to disk

[Dream Skill](https://github.com/JarbasAI/mycroft-deepdream-skill) - Create Deep Dream Images

[Poetry Skill](https://github.com/JarbasAI/mycroft-poetry-skill) - Create Poetry

[Picture Search Skill](https://github.com/JarbasAI/mycroft-pictureskill) - Search and download pictures

[Facebook Skill](https://github.com/JarbasAI/mycroft-facebook-skill) - Facebook Interaction, warns about chat messages, gives info and simulates some user actions

[Facebook content objective]() - Makes posts on facebook

[Proxy Scrapping Skill](https://github.com/JarbasAI/mycroft--proxy-scrapping---skill) - Get https proxys


### Informational Skills

        skills that give you information

[LILACS Knowledge](https://github.com/ElliotTheRobot/LILACS-mycroft-core/tree/dev/mycroft/skills/LILACS_knowledge) - searches several web sources for answers to different kinds of questions

[Random wikipedia objective]() - Tells you a wikipedia entry about a random subject

[Dumpmon Skill](https://github.com/JarbasAI/mycroft---dumpmon-skill) - Monitors dumpmon twitter for leaks and gives some stats

[Translate Skill](https://github.com/jcasoft/TranslateSkill) - Translate and speak sentences into other languages

[PhotoLocation Skill](https://github.com/JarbasAI/mycroft-photolocation-skill) - photos from locations

[Bitcoin Price Skill](https://github.com/chrison999/mycroft-skill-bitcoin-enhanced) - current bitcoin price

[Articles Skill](https://github.com/JarbasAI/mycroft-articles-skill) - read/open articles from websites

[Movie Recommendation Skill](https://github.com/JarbasAI/mycroft---movie-recommend-skill) - Recommends Movies from imdb top

[Metal Recomendation Skill](https://github.com/JarbasAI/mycroft---metal-recomend---skill) - Recommends metal bands

[Euromillions Skill](https://github.com/JarbasAI/mycroft---euromillions-skill) - last lottery numbers

[Space Launch Skill](https://github.com/marksev1/Mycroft-SpaceLaunch-Skill) - Next rocket launch

[Traffic Skill](https://github.com/BongoEADGC6/mycroft-traffic) - traffic driving times between locations

[Solar Times Skill](https://github.com/marksev1/Mycroft-SunSkill) - times for solar events (dusk, dawn...)

[Sunspot Count Skill](https://github.com/BoatrightTBC/sunspots) - number of currently visible sunspots

[Ping Skill](https://github.com/nogre/ping-skill) - get target website ping time or status

[Near Earth Object Tracking Skill](https://github.com/JarbasAI/mycroft---near-earth-object-tracker/) - tracks near earth objects

[Fox News](https://github.com/chrison999/mycroft-skill-fox-news) - play fox news

[CBC News](https://github.com/chrison999/mycroft-skill-cbc-news) - play CBC news

### New Clients

these are old experiments half-working, should not be used until a refactor is done

- [Facebook Chat Client](https://github.com/JarbasAI/mycroft---facebookchat---client) <- WIP
- [Graphic User Interface](https://github.com/JarbasAI/jarbas---pygtk---GUI) <- WIPO

# Developing skills for Jarbas

A [template skill](https://github.com/JarbasAI/jarbas-core/blob/dev/mycroft/skills/template_skill/__init__.py) is available as a guideline

### Showing pictures

        import sys
        from os.path import dirname
        # add skills folder to imports
        sys.path.append(dirname(dirname(__file__)))
        from service_display.displayservice import DisplayService

        in initialize -> self.display_service = DisplayService(self.emitter)

        in skill_handling -> self.display_service.show(pic_path, utterance)

### Playing Sound

        import sys
        from os.path import dirname
        # add skills folder to imports
        sys.path.append(dirname(dirname(__file__)))
        from service_audio.audioservice import AudioService

        in initialize -> self.audio_service = AudioService(self.emitter)

        in skill_handling -> self.audio_service.play([file_path], utterance)

### Objective Builder

You can use objectives to have several ways of accomplishing something / randomness in intents

        from mycroft.skills.core import MycroftSkill
        import sys
        from os.path import dirname
        # add skills folder to imports
        sys.path.append(dirname(dirname(__file__)))
        from service_objectives import ObjectiveBuilder

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

                # require keywords
                keyword = "TestKeyword"
                my_objective.require(keyword)

                # get objective intent and handler
                intent, self.handler = my_objective.build()

                # objective can still be executed without registering intent by saying
                # "objective " objective_name , and directly using objective skill
                self.register_intent(intent, self.handler)

            def stop(self):
                pass


        def create_skill():
            return TestRegisterObjectiveSkill()


in the above example saying "stupid test" , which is the sentence in TestKeyword.voc, will trigger one of the objective ways,
in this case "speak" intent and say "this is test" or "testing alright"

### Continuous Dialog

on every skill there is a converse method, this can be used to allow last executed skill to process next utterance

returning True will stop the utterance from triggering an intent and allow it to be processed by the skill instead of IntentService

If you expect a response right away in order to make the dialog more realistic you can do

            self.speak("Listening to you ", expect_response=True)

This will be the same as mycroft hearing the wakeword so you dont' need to say his name again

Here is an example of parrot skill, that will talk back everything to user

            def converse(self, transcript, lang="en-us"):
                if self.parroting:
                    if "stop" in transcript[0].lower():
                        self.parroting = False
                        self.speak("Parrot Mode Stopped")
                    else:
                        # keep listening without wakeword
                        self.speak(transcript[0], expect_response=True)
                    return True
                else:
                    return False

### Sequential Events - Registering and de-registering intents, passive utterance interception

It is also possible to require a few steps in order to achieve some action

We can use converse method to passively intercept utterance and (de)register intents in case (in)correct utterance is heard

May be useful if you dont need to parse the utterance to determine intent, just determine if it is expected/valid somehow

            def initialize(self):
                ....
                self.disable_intent('KonamiLeftIntent')
                self.disable_intent('KonamiRightIntent')
                self.disable_intent('KonamiBIntent')
                self.disable_intent('KonamiAIntent')

            def handle_up_intent(self, message):
                .....
                self.disable_intent('KonamiUpIntent')
                self.enable_intent("KonamiDownIntent")
                self.next_cheat = "down"

            def converse(self, transcript, lang="en-us"):
                if self.next_cheat not in transcript:
                    self.enable_intent('KonamiUpIntent')
                    self.disable_intent('KonamiDownIntent')
                    self.disable_intent('KonamiLeftIntent')
                    self.disable_intent('KonamiRightIntent')
                    self.disable_intent('KonamiBIntent')
                    self.disable_intent('KonamiAIntent')
                    self.next_cheat = "up"
                return False



# Intent Parsing inside skills

 with some changes to IntentService class we can now determine intents inside a skill and know which skill they belong to


            import sys
            from os.path import dirname
            # add skills folder to imports
            sys.path.append(dirname(dirname(__file__)))
            from service_intent_layer import IntentParser

            in initialize -> self.intent_parser = IntentParser(self.emitter)

            on converse method -> get intent instead of manually parsing utterance
                def converse(self, transcript, lang="en-us"):
                     # check if some of the intents will be handled
                    intent, id = self.intent_parser.determine_intent(transcript[0])
                    if id == 0:
                        # no intent will be triggered
                        pass
                    elif id != self.skill_id:
                        # no longer inside this conversation
                        skill_id = self.intent_parser.get_skill_id(intent)
                        # utterance will trigger skill_id
                        if self.intercept_flag:
                            # dont let intent class handle this if you dont want to
                            return True
                    return False


# Coding States - Intent Layers

Each layer has different intents available to be executed, this allows for much easier sequential event programming

[Konami Code Example](https://github.com/JarbasAI/jarbas-core/blob/dev/mycroft/skills/konami_code/__init__.py) - layers with a single intent

            in initialize

            layers = [["KonamiUpIntent"], ["KonamiUpIntent"], ["KonamiDownIntent"], ["KonamiDownIntent"],
                    ["KonamiLeftIntent"], ["KonamiRightIntent"], ["KonamiLeftIntent"], ["KonamiRightIntent"],
                    ["KonamiBIntent"], ["KonamiAIntent"]]

            # 60 is the number of seconds for the layer timer
            self.layers = IntentLayer(self.emitter, layers, 60)

            to activate next layer/state -> self.layers.next()
            to activate previous layer/state -> self.layers.previous()
            to activate layer/state 0 -> self.layers.reset()
            to get current layer/state -> state = self.layers.current_layer

            each tree has a timer, after changing state this timer starts and at the end resets the tree
            to disable timer, after doing next/previous -> self.layers.stop_timer()

            to go directly to a layer do -> self.tree.activate_layer(layer_num)
            in this case no timer is started so you should also do - > self.layers.start_timer()

            on converse -> parse intent/utterance and manipulate layers if needed (bad sequence)


# Multiple Intent Layers

"Trees" can be made by making a IntentLayer for each intent, we can use layers as branches and do

            self.branch = IntentLayer(self.emitter, layers, 60)
            self.branch.disable()

and to activate later when needed

            self.branch.reset()

intent parsing in converse method can manipulate correct tree branch if needed

this allows for much more complex skills with each intent triggering their own sub-intents / sub - trees

on demand manipulation of tree layers may also open several unforeseen opportunities for intent data structures

            self.branch.add_layer([intent_list])
            self.branch.remove_layer(layer_num)
            self.branch.replace_layer(self, layer_num, intent_list)
            list_of_layers_with_this_intent_on_it = self.branch.find_layer(self, intent_list)



# Privacy Enhancements (requires network manager)

removed from now, to be reworked without network manager

- wifi disable/enable

allows you to connect/disconnect mycroft from the internet, starts off by default

- vpn connect

trys to connect to vpns configured in network manager, if you dont have one try [cryptofree](https://github.com/cryptostorm/cryptostorm_client_configuration_files/tree/master/cryptofree)

- anonsurf start /stop

starts a global tor tunnel, all traffic is routed trough tor, requires [anonsurf](https://github.com/ParrotSec/anonsurf) to be installed in your system

- give me a proxy

gets you a https proxy

- TODO - auto proxy setup
- TODO - local/offline speech to text
- TODO - traffic blackhole if vpn goes down
- TODO - wicd network manager version / any other common network managers?


the most private setup would be "wifi enable" + "vpn connect" + "anonsurf start" , "wifi disable" whenever intenert connection is not needed


Forked from Mycroft 
==========

Full docs at: https://docs.mycroft.ai

Release notes at: https://docs.mycroft.ai/release-notes

Pair Mycroft instance at: https://home.mycroft.ai

Join the Mycroft Slack(chat) channel: http://mycroft-ai-slack-invite.herokuapp.com/

Looking to join in developing?  Check out the [Project Wiki](../../wiki/Home) for tasks you can tackle!

# Getting Started in Ubuntu - Development Environment
- run `build_host_setup.sh` (installs debian packages with apt-get, please read it) 
- run `dev_setup.sh` (feel free to read it, as well)
- Restart session (reboot computer, or logging out and back in might work).

# Getting Started in other environments

The following packages are required for setting up the development environment,
 and are what is installed by `build_host_setup.sh`

 - `git`
 - `python 2`
 - `python-setuptools`
 - `python-virtualenv`
 - `pygobject`
 - `virtualenvwrapper`
 - `libtool`
 - `libffi`
 - `openssl`
 - `autoconf`
 - `bison`
 - `swig`
 - `glib2.0`
 - `s3cmd`
 - `portaudio19`
 - `mpg123`
 - `flac`
 - `curl`

 added in this fork

 - fortune
 - libxml2-dev
 - libxslt1-dev
 - libopencv-dev
 - python-opencv

## Home Device and Account Manager
Mycroft AI, Inc. - the company behind Mycroft maintains the Home device and account management system. Developers can sign up at https://home.mycroft.ai

By default the Mycroft software is configured to use Home, upon any request such as "Hey Mycroft, what is the weather?", you will be informed that you need to pair and Mycroft will speak a 6-digit code, which you enter into the pairing page on the [Home site](https://home.mycroft.ai).

Once signed and a device is paired, the unit will use our API keys for services, such as the STT (Speech-to-Text) API. It also allows you to use our API keys for weather, Wolfram-Alpha, and various other skills.

Pairing information generated by registering with Home is stored in:

`~/.mycroft/identity/identity2.json` <b><-- DO NOT SHARE THIS WITH OTHERS!</b>

OR MAYBE DO SHARE! SEND NOISE! MAKE USERS ALL LOOK THE SAME! NO ID WITH SERVERS! USE VPN!
Skill to change identitys from "community" ids?

It's useful to know the location of the identity file when troubleshooting device pairing issues.

## Using Mycroft without Home.
If you do not wish to use our service, you may insert your own API keys into the configuration files listed below in <b>configuration</b>.

The place to insert the API keys looks like the following:

`"APIS": {`
`    "WolframAlphaAPI": "key",`
`    "WeatherAPI": "key",`
`    "GoogleMapsDirectionsAPI": "key",
`    "GraphAPI": "key",`
`    "NASAAPI": "DEMO_KEY",`
`    "MashapeAPI": "key",`
`    "WikimapiaAPI": "key",`
`    "CloudsightAPI": "key",`
`    "RedditAPI": "key",`
`    "CloudsightSecret": "secret",`
`    "RedditSecret": "secret"`
`  },`


Put the relevant key in between the quotes and Mycroft Core should begin to use the key immediately.

### APIs and dependencies in this fork ###

requirements.txt / dev_setup.sh will be updated in the future, check skill links for dependencies and watch skills log for debug on missing dependencies

### API Key services

mycroft apis:

- [STT API, Google STT](http://www.chromium.org/developers/how-tos/api-keys)
- [Weather Skill API, OpenWeatherMap](http://openweathermap.org/api)
- [Wolfram-Alpha Skill](http://products.wolframalpha.com/api/)

new apis:

- [Facebook Graph API](https://developers.facebook.com/docs/graph-api/) 
- [Reedit API](https://www.reddit.com/dev/api) 
- [Mashape API](https://market.mashape.com) 
- [CloudSight API](http://cloudsight.ai/api_client_users/new) 
- [Wikimapia API](http://wikimapia.org/api/)
- [Google Drive Maps API] (https://console.developers.google.com/apis/api/directions_backend)
- [NASA API](https://api.nasa.gov/index.html#apply-for-an-api-key)

## Configuration
Mycroft configuration consists of 3 possible config files.
- `mycroft-core/mycroft/configuration/mycroft.conf`
- `/etc/mycroft/mycroft.conf`
- `$HOME/.mycroft/mycroft.conf`

When the configuration loader starts, it looks in those locations in that order, and loads ALL configuration. Keys that exist in multiple config files will be overridden by the last file to contain that config value. This results in a minimal amount of config being written for a specific device/user, without modifying the distribution files.

# Running Mycroft Quick Start
To start the essential tasks run `./mycroft.sh start`. Which will start the service, skills, voice and cli (using --quiet mode) in a detched screen and log the output of the screens to the their respective log files (e.g. ./log/mycroft-service.log).
Optionally you can run `./mycroft.sh start -v` Which will start the service, skills and voice. Or `./mycroft.sh start -c` Which will start the service, skills and cli.

To stop Mycroft run `./mycroft.sh stop`. This will quit all of the detached screens.
To restart Mycroft run './mycroft.sh restart`.

Quick screen tips
- run `screen -list` to see all running screens
- run `screen -r [screen-name]` (e.g. `screen -r mycroft-service`) to reatach a screen
- to detach a running screen press `ctrl + a, ctrl + d`
See the screen man page for more details 

# Running Mycroft
## With `start.sh`
Mycroft provides `start.sh` to run a large number of common tasks. This script uses the virtualenv created by `dev_setup.sh`. The usage statement lists all run targets, but to run a Mycroft stack out of a git checkout, the following processes should be started:

- run `./start.sh service`
- run `./start.sh skills`
- run `./start.sh voice`
- run `./start.sh cli`

*Note: The above scripts are blocking, so each will need to be run in a separate terminal session.*

## Without `start.sh`

Activate your virtualenv.

With virtualenv-wrapper:
```
workon mycroft
```

Without virtualenv-wrapper:
```
source ~/.virtualenvs/mycroft/bin/activate
```


- run `PYTHONPATH=. python client/speech/main.py` # the main speech detection loop, which prints events to stdout and broadcasts them to a message bus
- run `PYTHONPATH=. python client/messagebus/service/main.py` # the main message bus, implemented via web sockets
- run `PYTHONPATH=. python client/skills/main.py` # main skills executable, loads all skills under skills dir

*Note: The above scripts are blocking, so each will need to be run in a separate terminal session. Each terminal session will require that the virtualenv be activated. There are very few reasons to use this method.*

# FAQ/Common Errors

#### When running mycroft, I get the error `mycroft.messagebus.client.ws - ERROR - Exception("Uncaught 'error' event.",)`

This means that you are not running the `./start.sh service` process. In order to fully run Mycroft, you must run `./start.sh service`, `./start.sh skills`, and `./start.sh voice`/`./start.sh cli` all at the same time. This can be done using different terminal windows, or by using the included `./mycroft.sh start`, which runs all process using `screen`.

#### this fork is a mess because of Y

ask me questions and help you shall receive

#### What are you going to do next ?

https://github.com/JarbasAI/jarbas-core/blob/dev/todolist.txt

Or you could make a suggestion? open issues

##### What are the Privacy Concerns i should worry about regarding AI assistants?

https://github.com/JarbasAI/jarbas-core/blob/dev/PrivacyConcerns.txt

##### is Jarbas alive ?

        He has a nervous system - the messagebus
        He has eyes - webcam
        He has a "brain section" to process vision
        He has ears - microphone
        He has a "brain section" for sound processing 
        He has "hormones"
        He has a "brain section" for decision making 
        He has some agency
        He has non-human senses - wifi, command line, chat, decentralized internet database
        He has abilities / impact in the real world
        He consumes energy
        
        BUT
            He does not reproduce
            He is not self-aware
            He is not self-owned
        
 Answer: Soon he will be!
    
