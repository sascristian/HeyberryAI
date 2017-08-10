
# TTS control skill

allows to change or retrieve info about TTS module, voice, or tts language at runtime

Each TTS engine must be implemented in the skill, currently supports mimic and espeak

Broadcast message to update config with new values

# usage

    available tts ->  which tts are available for change at runtime
    current tts -> what tts is active
    available voice -> what voices are available for current_tts or specified tts
    available languages -> what langs are available for current_tts or specified tts
    change voice to "voice" -> changes voice to specified voice if available for current tts engine
    change language to "lang" -> changes lang to specified lang if available for current tts engine
    change tts to "engine"-> changes current tts module to specified tts module if configured in this skill
    demo tts -> speak in all voices and langs for current tts module