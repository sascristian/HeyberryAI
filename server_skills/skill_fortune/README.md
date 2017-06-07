# FortuneSkill

This is just a simple [Mycroft](https://mycroft.ai) skill that reads the output of the `fortune` program. My first attempt to learn the `skill-sdk`.

`fortune-mod` must be installed for the skill to work. There's not currently any error checking, or interaction beyond starting the skill.

## Installation

Before installing the Fortune skill, you need to create a new virtual environment and install the [Skills SDK](https://docs.mycroft.ai/development/skills-framework).

First, clone the repostiory to a new directory.

```
$ git clone https://github.com/jaevans/mycroft-fortuneskill.git
```

Start the skill

```
$ workon fortuneskill
(fortuneskill) $ mycroft-skills-container fortuneskill
```

## Usage

Say one of the trigger phrases:

* "Mycroft, tell me my fortune"
* "Mycroft, read me a fortune"
* "Mycroft, tell my fortune"
* "Mycroft, tell me a fortune"


## Known Issues

Currently there is no error checking in the code, not even to see if `fortune` program is installed. 
