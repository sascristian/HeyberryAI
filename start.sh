#!/usr/bin/env bash
TOP=$(cd $(dirname $0) && pwd -L)
VIRTUALENV_ROOT=${VIRTUALENV_ROOT:-"${HOME}/.virtualenvs/mycroft"}

case $1 in
	"service") SCRIPT=${TOP}/mycroft/messagebus/service/main.py ;;
	"skills") SCRIPT=${TOP}/mycroft/skills/main.py ;;
	"skill_container") SCRIPT=${TOP}/mycroft/skills/container.py ;;
	"voice") SCRIPT=${TOP}/mycroft/client/speech/main.py ;;
	"cli") SCRIPT=${TOP}/mycroft/client/text/main.py ;;
	"audiotest") SCRIPT=${TOP}/mycroft/util/audio_test.py ;;
	"collector") SCRIPT=${TOP}/mycroft_data_collection/cli.py ;;
	"unittest") SCRIPT=${TOP}/test/main.py ;;
	"audioaccuracytest") SCRIPT=${TOP}/audio-accuracy-test/audio_accuracy_test.py ;;
	"sdkdoc") SCRIPT=${TOP}/doc/generate_sdk_docs.py ;;
    "enclosure") SCRIPT=${TOP}/mycroft/client/enclosure/main.py ;;
    "wifi") SCRIPT=${TOP}/mycroft/client/wifisetup/main.py ;;
    "sentiment") SCRIPT=${TOP}/mycroft/SentimentAnalisys/main.py ;;
    "dumpmon") SCRIPT=${TOP}/mycroft/dumpmon/main.py ;;
    "freewill") SCRIPT=${TOP}/mycroft/Subconscious/main.py ;;
    "vision") SCRIPT=${TOP}/mycroft/OpticalNerve/main.py ;;
    "audioanalisys") SCRIPT=${TOP}/mycroft/ears/main.py ;;
    "fbclient") SCRIPT=${TOP}/mycroft/client/FacebookChat/main.py ;;
    "context") SCRIPT=${TOP}/mycroft/context/main.py ;;
	*) echo "Usage: start.sh [service | skills | skill_container | voice | cli | audiotest | collector | unittest | enclosure | sdkdoc | wifi | sentiment | dumpmon | freewill | vision | context |audioanalisys |fbclient ]"; exit ;;
esac

echo "Starting $@"

shift

source ${VIRTUALENV_ROOT}/bin/activate
PYTHONPATH=${TOP} python ${SCRIPT} $@
