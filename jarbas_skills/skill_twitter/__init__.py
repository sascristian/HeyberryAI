# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


# Visit https://docs.mycroft.ai/skill.creation for more detailed information
# on the structure of this skill and its containing folder, as well as
# instructions for designing your own skill based on this template.


# Import statements: the list of outside modules you'll be using in your
# skills, whether from other files in mycroft-core or from external libraries
from os.path import dirname, join

import tweepy, requests, os, random, time
from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

__author__ = 'btotharye'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

# disable the damn logs
import logging

logging.getLogger("requests_oauthlib.oauth1_auth").setLevel(logging.WARNING)
logging.getLogger("oauthlib.oauth1.rfc5849").setLevel(logging.WARNING)


class TwitterAPI(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret, user):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth)
        self.user = user

    def get_followers(self):
        twitter_user = self.api.get_user(self.user)
        followers = twitter_user.followers_count
        return followers


# The logic of each skill is contained within its own class, which inherits
# base methods from the MycroftSkill class with the syntax you can see below:
# "class ____Skill(MycroftSkill)"
class TwitterSkill(MycroftSkill):
    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(TwitterSkill, self).__init__(name="TwitterSkill")
        self.user = self.config.get('twitter_user')
        self.twitter = TwitterAPI(self.config.get('consumer_key'),
                                  self.config.get('consumer_secret'),
                                  self.config.get('access_token'),
                                  self.config.get('access_secret'),
                                  self.user)

    def get_followers(self):
        user = self.twitter.api.get_user(self.user)
        followers = user.followers_count
        return followers

    # This method loads the files needed for the skill's functioning, and
    # creates and registers each intent that the skill uses
    def initialize(self):
        self.load_data_files(dirname(__file__))
        self.load_regex_files(join(dirname(__file__), 'regex', self.lang))

        get_followers_intent = IntentBuilder("GetFollowersIntent"). \
            require("Followers").optionally("Person").build()
        self.register_intent(get_followers_intent, self.handle_get_followers_intent)

        follow_user_intent = IntentBuilder("FollowUserIntent"). \
            require("FollowUser").optionally("follow").optionally("user").build()
        self.register_intent(follow_user_intent, self.handle_follow_user_intent)

        unfollow_user_intent = IntentBuilder("UnFollowUserIntent"). \
            require("UnFollowUser").optionally("unfollow").optionally("user").build()
        self.register_intent(unfollow_user_intent, self.handle_unfollow_user_intent)

        post_tweet_intent = IntentBuilder("PostTweetIntent"). \
            require("status_post").build()
        self.register_intent(post_tweet_intent, self.handle_post_tweet_intent)

        post_patreon_tweet_intent = IntentBuilder("PostPatreonTweetIntent"). \
            require("TweetPatreon").build()
        self.register_intent(post_patreon_tweet_intent, self.handle_tweet_patreon)

        post_btc_tweet_intent = IntentBuilder("PostBTCTweetIntent"). \
            require("TweetBTC").build()
        self.register_intent(post_btc_tweet_intent, self.handle_tweet_btc)

        # external tweet requests"
        self.emitter.on("tweet.request", self.handle_tweet_request)

    # The "handle_xxxx_intent" functions define Mycroft's behavior when
    # each of the skill's intents is triggered: in this case, he simply
    # speaks a response. Note that the "speak_dialog" method doesn't
    # actually speak the text it's passed--instead, that text is the filename
    # of a file in the dialog folder, and Mycroft speaks its contents when
    # the method is called.
    def handle_get_followers_intent(self, message):
        if message.data.get("Person"):
            pres_user = self.twitter.api.get_user('realDonaldTrump')
            pres_follower_count = pres_user.followers_count
            self.speak("Currently the president has {} followers".format(pres_follower_count))
        else:
            followers_count = self.twitter.get_followers()
            self.speak_dialog("followers", data={"followers_count": followers_count})

    #
    # Follow user intent, takes userid from message and follows them.
    #
    def handle_follow_user_intent(self, message):
        LOGGER.debug("The message data is: {}".format(message.data))
        follow_user = message.data["user"].replace(" ", "")
        LOGGER.debug("Twitter user to follow is: {}".format(follow_user))
        if follow_user is None:
            self.speak("Sorry I'm not sure which twitter user you want me to follow.")
        else:
            self.twitter.api.create_friendship(follow_user)
            self.speak("Successfully followed user {} on twitter".format(follow_user))

    #
    # Follow user intent, takes userid from message and follows them.
    #
    def handle_unfollow_user_intent(self, message):
        LOGGER.debug("The message data is: {}".format(message.data))
        unfollow_user = message.data["user"].replace(" ", "")
        LOGGER.debug("Twitter user to unfollow is: {}".format(unfollow_user))
        if unfollow_user is None:
            self.speak("Sorry I'm not sure which twitter user you want me to unfollow.")
        else:
            self.twitter.api.destroy_friendship(unfollow_user)
            self.speak("Successfully unfollowed user {} on twitter".format(unfollow_user))

    def handle_post_tweet_intent(self, message):
        LOGGER.debug("The message data is: {}".format(message.data))
        status_post = message.data["status_post"]
        if status_post is None:
            self.speak("Sorry I'm not sure what you want me to post.")
            return
        else:
            self.twitter.api.update_status(status=status_post)
            self.speak("Successfully posted status update to twitter.  What I posted is: {}".format(status_post))
        self.emitter.emit(Message("twitter_post", {"post": status_post, "post_type": "text"}))

    def handle_tweet_btc(self, message):
        possible_tweets = ["If you love this, can you buy me a {{HUMAN_BEVERAGE}}? I really appreciate it! Send some satoshi's to",
                           "Send some magic internet money to",
                           "Do you love bitcoin? I do!",
                           "Help my maker build me for a living",
                           "Help me get a body",
                           "Help my development",
                           "Support my development",
                           "Support my maker",
                           "Help me get more abilities",
                           "Support my existence"]

        tweet_text = random.choice(possible_tweets) + " 15B4ZQFY5UfopjRtSRQPx7ibRaFukE1Ntq #BTC #SupportMe"
        if "#JarbasAI" not in tweet_text:
            tweet_text += " #JarbasAI"
        if "#MycroftAI" not in tweet_text:
            tweet_text += " #MycroftAI"
        self.twitter.api.update_status(status=tweet_text)
        self.speak("Successfully posted btc adress to twitter.  What I posted is: {}".format(tweet_text))
        self.emitter.emit(Message("twitter_post", {"post": tweet_text, "post_type": "text"}))

    def handle_tweet_patreon(self, message):
        possible_tweets = ["Help me make stuff for mycroft for a living",
                           "Help my maker build me for a living",
                           "Help my maker code me for a living",
                           "Support my existence",
                           "Help me get a body",
                           "Help my development",
                           "Support my development",
                           "Support my maker",
                           "Help me get more abilities",
                           "Support my existence"]

        tweet_text = random.choice(possible_tweets)+" https://www.patreon.com/jarbasAI #Patreon"
        if "#JarbasAI" not in tweet_text:
            tweet_text += " #JarbasAI"
        if "#MycroftAI" not in tweet_text:
            tweet_text += " #MycroftAI"
        self.twitter.api.update_status(status=tweet_text)
        self.speak("Successfully posted patreon link to twitter.  What I posted is: {}".format(tweet_text))
        self.emitter.emit(Message("twitter_post", {"post": tweet_text, "post_type": "text"}))

    def handle_tweet_request(self, message):
        tweet_type = message.data.get("tweet_type", "text")
        tweet_pic = message.data.get("tweet_pic", None)
        tweet_text = message.data.get("tweet_text", "I Love AI <3")
        if "#JarbasAI" not in tweet_text:
            tweet_text += " #JarbasAI"
        if "#MycroftAI" not in tweet_text:
            tweet_text += " #MycroftAI"
        if tweet_type == "text":
            self.twitter.api.update_status(status=tweet_text)
        elif tweet_type == "image":
            self.twitter.api.update_with_media(tweet_pic, status=tweet_text)
        elif tweet_type == "remote_image":
            self.tweet_image_from_url(tweet_pic, tweet_text)
        else:
            self.log.error("Unknown tweet type")
            return
        self.emitter.emit(Message("twitter_post", {"post": tweet_text, "post_type": tweet_type}))

    def tweet_image_from_url(self, url, text):

        filename = 'tweet_pic_temp.jpg'
        request = requests.get(url, stream=True)
        if request.status_code == 200:
            with open(filename, 'wb') as image:
                for chunk in request:
                    image.write(chunk)

            self.twitter.api.update_with_media(filename, status=text)
            os.remove(filename)
            return True
        else:
            self.log.error("Unable to download image")
        return False

    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, the method just contains the keyword "pass", which
    # does nothing.
    def stop(self):
        pass


# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return TwitterSkill()

