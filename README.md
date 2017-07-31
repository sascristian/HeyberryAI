# Jarbas 

Stable branch
==========

This branch is a work in progress, all jarbas changes are being merged one by one to make this a stable version

Check the jarbas_docs folder for more info on each change as it is added

This should install in a virtual env just like mycroft, only debian scripts were updated

virtual env is named jarbas , it should be possible to have both mycroft and jarbas at same time, each one running in a different virtual env

whenever official mycroft documentation mentions "workon mycroft" use "workon jarbas"

not everything will work out of the box, expect bumps

- no online config, must edit files
- STT is currently broken (trying to get pocket sphinx stt option broke wake
word)
- no mycroft stt, must configure Kaldi or other online service
- no shared api keys (twitter/facebook/weather/wolfram...)
- some skills not fully functional  / added yet / configured for server


# Want to help me work on mycroft full time?

Support me on [Patreon](https://www.patreon.com/jarbasAI)

Or send me some [magic internet money](https://en.wikipedia.org/wiki/Bitcoin) to 15B4ZQFY5UfopjRtSRQPx7ibRaFukE1Ntq

# The idea

Personal assistants today are glorified voice activated script runners, with the bonus of mining your data for some company

Stick some hardware and they are glorified alarm clocks than run scripts instead

Jarbas fork intends to show that mycroft is much more than this by harnessing the power of open source,
an AI assistant should do AI stuff on demand, where is the AI in mycroft/jarbas?

# TODO links in each one

The essential parts that make it work, many options available for each

        - speech to text
        - text to speech
        - intent from text (text to action)

The "AI stuff" it can already do for you

        - Image classification
        - Object recognition
        - Face recognition
        - Voice recognition (wip)
        - deep dreaming
        - Generate names
        - Generate Poetry
        - Copy the style of any artist
        - Colorize Black and White photos
        - Chatbot
        - Auto complete your stories
        - Learn and build a database of what it learns

And dont forget the "not really AI" stuff

        - post to facebook / twitter / instagram
        - control a browser and do any kind of stuff
        - generate psychedelic images using mathematics
        - search the internet for answers
        - Search and play music from youtube (or spotify or more places!)
        - Stuff not worth mentioning like parrot back, dictation, tell jokes, hows
        the weather, which asteroids are near earth, how many sunspots currently
        visible, show you the latest image of earth from orbit..


![](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/jarbas.png?raw=true)
![](https://github.com/JarbasAI/JarbasAI/blob/patch-15/mycroft/client/server/ssl.jpeg?raw=true)
![](https://github.com/JarbasAI/client_server_idea/raw/master/Untitled%20Diagram.jpg)

# Changes in this fork

            - no pairing
            - no config update from mycroft.ai
            - added "intent.start", "intent.end", "intent.failed" messages
            - in skills/core.py SKILLS_DIR is now jarbas_skills folder instead of opt
            - do not remove articles in normalize (too much normalization IMO)

            # temporary changes
            - no msm


# Forslund audio service

Audio playback is now handled by forslund's [audio service](https://github.com/forslund/mycroft-core/tree/audio-service)

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

# [PR#925](https://github.com/MycroftAI/mycroft-core/pull/925)

[Converse method](https://github.com/JarbasAI/JarbasAI/blob/patch-15/Jarbas_docs/Converse.md), allow skills to handle utterances instead of intent service

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

- webchat client
- black and white photo colorize
- instagram skill
- snowboy wakeword
- pocket sphinx offline stt
- kaldi install scripts
- update skills using caffe for tensorflow version (already in server)
- class vizualization/deep draw in tensorflow
- models download script (they auto download on first skill run which takes...long)