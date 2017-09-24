# mycroft-speedtest
A Mycroft skill for running speedtests

## Short Demo
https://www.youtube.com/watch?v=1Tm56JKZcAg

## Setup

1. Clone this repo into your third party skills folder (the current default is ~/.mycroft/skills, but it used to be ~/.mycroft/third_party_skills; check your global/local mycroft.conf files if you have issues)
  * `cd ~/.mycroft/skills && git clone https://github.com/ChristopherRogers1991/mycroft-speedtest.git`
2. `cd` into the resulting `mycroft-speedtest` directory
  * `cd ~/.mycroft/skills/mycroft-speedtest`
3. If your mycroft instance runs in a virtual environment, activate it
  * `source ~/.virtualenvs/mycroft/bin/activate`
4. Install the required python libraries
  * `pip install -r requirements.txt`
5. Add the block below to your mycroft.conf file (`~/.mycroft/mycroft.conf`)
```
   "SpeedTestSkill": {
        "host": "",
        "http_debug": 0,
        "runs": <runs, recommend 10>
    }

```

If that file did not already exist (this is the first third party skill you have added), wrap that entire block in { }. The finished file should be valid json. If you have issues, use http://jsonlint.com/ to validate the json.

## Sample Phrases
1. Run a speedtest
2. What is my connection speed?