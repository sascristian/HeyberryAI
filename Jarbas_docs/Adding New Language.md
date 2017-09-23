# how to add a new language

There seems to be some confusion on how to add a new language to Mycroft-core, here is an overview of what is needed

# step 1 - find a STT engine that supports your language

list of languages supported by [google](https://stackoverflow.com/questions/14257598/what-are-language-codes-in-chromes-implementation-of-the-html5-speech-recogniti)

list of languages supported by [ibm_bluemix](https://www.ibm.com/watson/developercloud/speech-to-text/api/v1/#sessionless_methods)

for Wit the recognition language is configured in the Wit.ai app settings

if your language isn't supported add a new [STT engine](https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst) that supports it,

another option is to use local PocketSphinx, this is not supported by Mycroft-core, a POC can be found [here](https://github.com/SoloVeniaASaludar/mycroft-core/tree/next/mycroft/client/lspeech)

# step 2 - find a TTS engine that supports your language

choose a TTS engine that supports your language, [espeak](http://espeak.sourceforge.net/languages.html) should support most

if your language is not supported find a online solution or add a new TTS engine, [PicoTTS](https://github.com/JarbasAI/JarbasAI/blob/patch-15/mycroft/tts/pico_tts.py) supports some languages

# step 3 - Change your config file

Change your config file to use TTS and STT engine of choice

        "lang": "pt-pt",
        ...
        "tts": {
          "module": "espeak",
          ...
          "espeak": {
            "lang": "pt-pt",
            "voice": "m1"
          }
        "stt": {
          "module": "ibm",
          ...
          "ibm":{
            "credential" : {
                "username": "xxxxxxxxxxxxxxx",
                "password": "xxx"
                }
          }


Previous changes may be lost if remote configuration is enabled, depending on
which config you made them, optionally edit mycroft.conf to disable it:


        "server": {
         ...
         "update": false,
         ...
        },



# step 4 - Translate missing pieces

A guide to translate to a new language can be found [here](https://github.com/MycroftAI/mycroft-core/projects/2)
Languages need parsing code to be implemented, this means translating spoken
numbers to digits and normalization

example [pt-pt parsing PR](https://github.com/MycroftAI/mycroft-core/pull/1049)

Standard dialog files must also be translated, example [pt-pt translation PR](https://github.com/MycroftAI/mycroft-core/pull/1033)

finally, [individual skills](https://github.com/JarbasAI/JarbasAI/tree/patch-15/jarbas_skills/skill_hello_world/vocab) may also need translation

# step 5 - tweak core

optionally add Language support [PR](https://github.com/MycroftAI/mycroft-core/pull/1111) to no load skills that don't support current language

optionally hack the TTS/STT python files for [failsafes](https://github.com/JarbasAI/JarbasAI/blob/patch-15/mycroft/stt/__init__.py#L98) like pt-pt not supported but pt-br supported

# step 6 - New Wake word

Optionally add a new wake_word for your language, if use [Snowboy](https://www.youtube.com/watch?v=GIkBh0VFmbc) nothing special must be done

if using Pocketsphinx you can try using phonemes from the english language or download a new model

Pocketsphinx is the default subsystem used to recognize the wake-up word,
default is English "Hi, Mycroft". You can add support for other languages.

| Language | Download (L)anguage (M)odel | Download DICT | Download HMM | Language Code |
| ------------- |-------------| -----|------|----|
| Spanish | [Download LM ES](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Spanish/es-20k.lm.gz/download) | [Download DICT ES](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Spanish/es.dict/download) | [Download HMM ES](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Spanish/cmusphinx-es-5.2.tar.gz/download) | es
| German | [Download LM DE](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/German/cmusphinx-voxforge-de.lm.gz/download) | [Download DICT DE](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/German/cmusphinx-voxforge-de.dic/download) | [Download HMM DE PTM Version](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/German/cmusphinx-de-ptm-voxforge-5.2.tar.gz/download) | de

During the next steps please replace LC with your code - e.g.: "es" or "de"

For just changing the wake word the "HMM" download (means, mdef, ...) is enough. The *.dict and *.lm files are required for using complete localized stt (see step 1).

Create model directory for your language in mycroft installation directory.

    mkdir _your_base_dir_/mycroft/client/speech/model/LC

### if directory /usr/share/pocketsphinx/LC exists

If you have your dedicated pocketsphinx installation within /usr/share/pocketsphinx, please check that the following files exist (HMM Download).

* /usr/share/pocketsphinx/model/LC/LC/feat.params
* /usr/share/pocketsphinx/model/LC/LC/noisedict
* /usr/share/pocketsphinx/model/LC/LC/means
* /usr/share/pocketsphinx/model/LC/LC/mdef
* /usr/share/pocketsphinx/model/LC/LC/mixture_weights
* /usr/share/pocketsphinx/model/LC/LC/sendump
* /usr/share/pocketsphinx/model/LC/LC/transition_matrices
* /usr/share/pocketsphinx/model/LC/LC/variances

After verifying that these files exist you have to link or copy them to your mycroft directory structure.
* ln -s /usr/share/pocketsphinx/model/LC/LC _your_base_dir_/mycroft/client/speech/model/LC/hmm

### if directory /usr/share/pocketsphinx/LC does NOT exist
* Create directory _your_base_dir_/mycroft/client/speech/model/LC/hmm
* Copy the HMM files (see above) to _your_base_dir_/mycroft/client/speech/model/LC/hmm

