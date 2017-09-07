

# Jarbas

Jarbas is a fork of mycroft-core


# THERE BE DRAGONS

##### WARNING ######

# THERE BE DRAGONS

everything can break anytime!
things designed for mycroft may not work with jarbas!
some things designed for jarbas wont work in mycroft!
support for this branch is limited to me alone, folks from mycroft community may not be able to help


that said, everything that works in mycroft i try to make work with jarbas,
but i give absolutely no warranty of this!

- bus address is different, but it is supposed to be configured in config file,
that means the 3rd party should support it and not hard code it
- msm temporarly removed, skill install is old-school manual install
- no use of mycroft.ai, this means no web ui (yet) and harder setup
- no online config, must edit files
- no mycroft stt, must configure Kaldi or other online service
- no shared api keys (weather/wolfram...)
- some skills not fully functional  / added yet / configured for server / undocumented setup

Still interested?


Dev branch
==========

This branch (patch-15) is a work in progress, forever in development, the other
branches should all be considered broken / abandoned / temporary

Check the jarbas_docs folder for more info on each change, expect this to be
outdated

This should install in a virtual env just like mycroft, only debian
install scripts were updated

virtual env is named jarbas , it is possible to have both mycroft and jarbas at
same time, each one running in a different virtual env and using different bus
adress

whenever official mycroft documentation mentions "workon mycroft" use "workon jarbas"

not everything will work out of the box, expect bumps


# The idea

Personal assistants today are glorified voice activated script runners, with the bonus of mining your data for some company

Stick some hardware and they are glorified alarm clocks than run scripts instead

Jarbas fork intends to show that mycroft is much more than this by harnessing the power of open source,
an AI assistant should do "AI stuff" on demand, where is the AI in mycroft/jarbas?

         #### TODO links in each one ####

The essential parts that make it work, many options available for each

        - speech to text
        - text to speech
        - intent from text (text to action)

The "AI stuff" it can already do for you

        - Image classification
        - Object recognition
        - Face recognition
        - Voice recognition (wip)
        - Deep Dreaming
        - Generate names with Restricted Boltzman Machines
        - Generate Poetry with MarkovChains
        - Copy the style of any artist using Style Transfer
        - Colorize Black and White photos
        - Chatbot using AIML
        - Auto complete your stories with a Char-RNN (training...)
        - Learn and build a database of what it learns with LILACS

And dont forget the "not really AI" stuff

        - post to facebook / twitter / instagram
        - control a browser like a real human and do any kind of stuff with it
        - generate psychedelic images using mathematics
        - search the internet for answers
        - Search and play music from youtube (or spotify or more places!)
        - Stuff not worth mentioning like parrot back, dictation, tell jokes, hows
        the weather, which asteroids are near earth, how many sunspots currently
        visible, show you the latest image of earth from orbit..

In practice it can act as a vocal search engine, a helper for disabled people, a desktop automation/OS framework, an artificial pet, a Art assistant, a Writers Assistant, an educational toy for children, A work of art by its own merit...

![](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/jarbas.png?raw=true)
![](https://github.com/JarbasAI/JarbasAI/blob/patch-15/mycroft/client/server/ssl.jpeg?raw=true)
![](https://github.com/JarbasAI/client_server_idea/raw/master/Untitled%20Diagram.jpg)

# Main changes in this fork

            - no pairing
            - no config update from mycroft.ai
            - added "intent.start", "intent.end", "intent.failed" messages
            - skills/core.py SKILLS_DIR is now jarbas_skills folder instead of opt but configurable
            - do not remove articles in normalize (too much normalization IMO)
            - allow for multiple hot words of various kinds
            - offline stt (pocketpshinx) <- WIP
            - wakeword/hotword/standupword snowboy support
            - fallback skill order override in config file
            - apis centralized in self.APIS for all skills
            - message_context update methods added to MycroftSkill
            - update_config method added to MycroftSkill
            - screen display service
            - speech messages transmit metadata together with speech
            - speech messages set adapt context for LastSpeech and every metadata field
            - recognizer_loop:speak / hotword / external stt message types
            - save utterances if desired (configurable, disabled by default)
            - utterance and hotword save paths configurable
            - external STT requests (transcribe audio from a skill)
            - runtime shutdown/reload of skills
            - runtime changes of configuration (tts/stt/hotwords)
            - centralized API section in config
            - ConfigurationManager.save checks for config existence before loading it
            - webchat client
            - encrypted multi instance networking (server/client)
            - multiple connected clients support, authorization per client per action
            - many helper classes
            - many skills bundled by default

            # temporary changes
            - no msm

# Videos


Display Service Demo

[![Display Service Demo](https://img.youtube.com/vi/y9rb1wKZiUs/0.jpg)](http://www.youtube.com/watch?v=y9rb1wKZiUs)


Hotwords/Snowboy Demo

[![Hotwords/Snowboy Demo](https://img.youtube.com/vi/GIkBh0VFmbc/0.jpg)](http://www.youtube.com/watch?v=GIkBh0VFmbc)


TTS runtime change Demo

[![TTS runtime change Demo](https://img.youtube.com/vi/cKc_RxRbJ3U/0.jpg)](http://www.youtube.com/watch?v=cKc_RxRbJ3U)

# very old videos


Facebook chat client Demo

[![Facebook chat client Demo](https://img.youtube.com/vi/oh1Y9f16xTk/0.jpg)](http://www.youtube.com/watch?v=oh1Y9f16xTk)


LILACS learning demo

[![LILACS learning demo](https://img.youtube.com/vi/BPYOC1Dass4/0.jpg)](http://www.youtube.com/watch?v=BPYOC1Dass4)


Morse Code TTS engine joke

[![Morse Code TTS engine joke](https://img.youtube.com/vi/ZEhA8VXzLII/0.jpg)](http://www.youtube.com/watch?v=ZEhA8VXzLII)


AIML chatbot demo

[![AIML chatbot demo](https://img.youtube.com/vi/6gbKz2u-q8k/0.jpg)](http://www.youtube.com/watch?v=6gbKz2u-q8k)


# Install

only debian officially supported, ubuntu complains because firefox package name is different

- build_host_setup_debian.sh
- build_dev_setup.sh

# light install

if you don't care about pre-packaged skills / using a pi

- build_host_setup_debian_light.sh
- build_dev_setup_light.sh

this won't install most skill requirements, only core and client/server requirements

in the future will install pymimic instead of mimic

# Update

to update packages:
- git pull -> for merging this fork changes
- re-run host setup script -> for updating system packages
- run dev-update.sh or dev-update-light.sh -> update python packages in virtual env

using full update scripts:

this means overwrite all changes and revert to current github state, update host
 packages, and update dev packages

- full_update_debian.sh or full_update_debian_light.sh

# Usage

to start it is the same as mycroft-core, jarbas.sh and mycroft.sh are duplicates

- TODO - all usage flags -c -v -cl -s -w
- ./jarbas.sh start

or with different processes

- ./start.sh service
- ./start.sh skills
- ./start.sh audio
- ./start.sh display
- ./start.sh voice
- ./start.sh cli
- ./start.sh server
- ./start.sh client
- ./start.sh webchat


# Other scripts

all others scripts are not meant for use, open them to understand what they do,
comments explain most things

of interest:
- pymimic install scripts
- tensorflow model download scripts in jarbas_models/model_folder
- all mimic voices download script

##### EVERYTHING BELLOW IS NOT UPDATED OFTEN , SORRY ########

# MOAR CHANGES IN THIS FORK

# Intent Layers

[IntentLayers](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/intent_layer.md) class, allows to activate and deactivate intents grouped in layers

Example usage in [KonamiCode Skill](https://github.com/JarbasAI/JarbasAI/tree/patch-15/jarbas_skills/skill_konami_code)

# Services

[Backend Service](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/service.md), A helper class to emit and wait for bus messages was added, needed in several skills

Used for inter skill communication in image recognition, face recognition, object recognition, deep dream, style transfer, vision, user manager...

# MarkovChain

[Markov Chain](https://github.com/JarbasAI/JarbasAI/blob/patch-15/mycroft/util/markov.py) helper class, save and load functionality

Example usage in [Poetry Skill](https://github.com/JarbasAI/JarbasAI/tree/patch-15/jarbas_skills/skill_poetry)

# Art util

Generate random [pictures utility](https://github.com/JarbasAI/JarbasAI/blob/patch-15/mycroft/util/art.py) based on [this blog post](https://jeremykun.com/2012/01/01/random-psychedelic-art/)

Example usage in [Art Skill](https://github.com/JarbasAI/JarbasAI/tree/patch-15/jarbas_skills/skill_art)


# [PR#859](https://github.com/MycroftAI/mycroft-core/pull/859)

 [IntentParser](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/Intent_parse.md) class

            - helper class added to intent_service
            - intent from utterance
            - skill from intent
            - skill from utterance

# [PR#858](https://github.com/MycroftAI/mycroft-core/pull/858)

[priority skills](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/Priority_skills.md) list

            - priority skills are loaded first
            - read from config

# [PR#860](https://github.com/MycroftAI/mycroft-core/pull/860)

needed for [intent_layers](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/intent_layer.md)

            - enable / disable intent can be requested in messagebus

# [PR#783](https://github.com/MycroftAI/mycroft-core/pull/783)

control skills externally, allow run-levels, [external skill load and reload](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/external_reload_shutdown.md))

            - skills have internal id, internal id used instead of name in intent messages
            - skills main now listens for external messages for skill_manifest, skill_shutdown and skill_reload

# [PR#790](https://github.com/MycroftAI/mycroft-core/pull/790)

[target bus messages](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/speech_target.md)

            - uses message context to target messages to source of utterance
            - uses message context to mute (not trigger tts)
            - uses message context to tell if more speech is expected
            - adds "metadata" field to speak method
            - clients check if they are the target of utterance before processing it
            - adds data to message context:
                - target = cli/speech/facebook - default = "all"
                - mute = trigger tts or not - default = "false"
                - more_speech = more speak messages expected- default = "False"
                - destinatary = used to track remote_client to send message to
                - source = source of message, default = source skill / source client

# [PR#556](https://github.com/MycroftAI/mycroft-core/pull/556)

[stop speak messages](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/mute_unmute.md)

            - adds disable_speak_flag to speech and cli
            - this flag is a global mute switch, if set no tts is ever made
            - skill to mute/unmute not yet merged



# Server/Client

[jarbas networking](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/Server_Client.md)

            - client / server (a "firewall" that connects to the mycroft messagebus )
            - client connects to server, by secure websockets
            - server sends public pgp key
            - client sends public pgp encrypted with server pgp
            - server sends AES key encrypted with client pgp, client pgp key authorizes client / creates account in server
            - all communication after is AES encrypted, if plaintext received client is kicked
            - server does all kinds of processing (receiving files, requesting stuff from clients, authorizing action per client)
            - on first run a new pgp key is automatically created (client and server)

client server basically connect jabas/mycroft instances, server can work as:

            - fallback mechanism
            - chat room
            - relay
            - ...

# Essential Skills

Lots of skills pre-packaged

[Browser Service](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/browser_service.md)

[Objectives Service](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/objectives.md)

[TTS Control]() - change voice at runtime vocally

[Control Center]() - shutdown/restart skills , enforce run levels

[Vision Service]() - process webcam input

[RBM Service]() - Generate new words

[Object Recognition]()

[Image Classification]()

[Face Recognition]()

[Dictation]() - Write to txt user speech

[News]() - Plays news

[Mute]() - Mute TTS

[Again]() - Repeat last action

[LILACS]() - Search wikipedia, wikidata, dbpedia, conceptnet, wordnik, wolframalpha and learn

TODO finish this


# Blacklisted skills by default

some skills are blacklisted because they are either not common, heavy, or because i run them in server

- browser service
- server fallback
- LILACS_core
- LILACS_storage
- LILACS_teach
- LILACS_users
- LILACS_curiosity
- deep dream
- image recognition
- object recognition
- colorize
- vision
- facebook
- twitter
- instagram

# Skills that fallback to server

these skills have a flag in their init method to ask server or run locally

consider them broken, get them from server branch if you really want them

- image recognition
- face recognition
- object recognition
- deep dream
- style transfer
- colorize

these skills have a flag to ask client

- vision service # wip

# Currently working on

not updated often

- Help Skill
- R2D2 TTS
- instagram skill
- pocket sphinx offline stt
- kaldi install scripts
- class vizualization/deep draw in tensorflow
- models download script (they auto download on first skill run which takes...long)