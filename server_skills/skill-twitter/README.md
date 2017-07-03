# Twitter skill

Currently skill gets the follower count of the user that is specified in the mycroft.conf file.  It also gets the current amount of followers for the president.

## Setup Twitter API
Go over to https://apps.twitter.com/ and create an app.  This will give you the following information that you need to put into your mycroft.conf file located in /etc/mycroft/mycroft.conf.  Populate the fields accordingly, whatever the twitter_user is what is used for follower count, etc.

```
"TwitterSkill": {
    "consumer_key": "",
    "consumer_secret": "",
    "access_token": "",
    "access_secret": "",
    "twitter_user": ""
  }
```

## Installation

Clone the repository into your `~/.mycroft/skills` directory. Then install the
dependencies inside your mycroft virtual environment:

If on picroft just skip the workon part and the directory will be /opt/mycroft/skills

```
cd ~/.mycroft/skills
git clone https://github.com/btotharye/mycroft-twitter-skill.git TwitterSkill
workon mycroft
cd TwitterSkill
pip install tweepy
```

## Current state

Working phrases:
 - How many twitter followers do I have
 - How many twitter followers does trump have
 - How many twitter followers does the president have.
 - Follow br1anhopkins - To follow me on twitter, otherwise can be any twitter userid.
 - Unfollow br1anhopkins - To unfolow me but why would you want to do that :).  Same way any userid.
 - Post to twitter today is a great day to tweet from mycroftai - This will post a tweet with anything after the post to twitter part, use with caution no verify yet before it posts to twitter.

Known issues:
 - ...

TODO:
 - Whats trending
 - Search users
 - Get last status update from President (aka what he last tweeted)
