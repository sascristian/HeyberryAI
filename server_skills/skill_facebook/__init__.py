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

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

import fb
import fbchat
import random
from time import sleep, asctime
from threading import Thread
import time

__author__ = 'jarbas'

# TODO logs in bots


class FaceBot():
    def __init__(self, token):
        self.token = token
        self.facebook = fb.graph.api(self.token)
        self.id = self.get_self_id()

    def get_self_id(self):
        return self.get_field("id", "me")["id"]

    def get_friends(self, id="me"):
        return self.facebook.get_object(cat='single', id=id, fields=['friends'])

    def get_field(self, field, id = "me"):
        return self.facebook.get_object(cat='single', id=id, fields=[field])

    def get_friend_num(self, id="me"):
        friends = self.facebook.get_object(cat='single', id=id, fields=['friends'])
        try:
            friends = friends["friends"]["summary"]["total_count"]
            print "number of friends: " + str(friends)
        except:
            pass
            #print "you dont have acess to this users friends"
        return friends

    def post_to_wall(self, text="My facebook status", id="me", link=None):
        if link is not None:
            return self.facebook.publish(cat="feed", id=id, message=text, link=link)
        else:
            return self.facebook.publish(cat="feed", id=id, message=text)

    def comment_object(self, object_id, comment="My comment"):
        return self.facebook.publish(cat="comments", id=object_id, message=comment)

    def create_album(self, name="Album Name", message="Album Details", id="me"):
        return self.facebook.publish(cat="albums", id=id, name=name, message=message)

    def delete_status(self, status_id):
        return self.facebook.delete(id=status_id)

    def delete_comment(self, comment_id):
        return self.facebook.delete(id=comment_id)

    def clean_profile(self, profile):
        try:
            profile["age_range"] = profile["age_range"]["min"]
        except:
            pass

        try:
            l = []
            for language in profile["languages"]:
                l.append(language["name"])
            profile["languages"] = l
        except:
            pass

        try:
            profile["friends"] = profile["friends"]["summary"]["total_count"]
        except:
            pass

        try:
            ed = []
            for e in profile["education"]:
                d = {}
                d.setdefault("name", e["school"]["name"])
                d.setdefault("type", e["type"])
                ed.append(d)
            profile["education"] = ed
        except:
            pass

        try:
            work = []
            for w in profile["work"]:
                wr = {}
                wr.setdefault("name", w["position"]["name"])
                wr.setdefault("start_date", w["start_date"])
                wr.setdefault("end_date", w["end_date"])
                wr.setdefault("employer", w["employer"]["name"])
                work.append(wr)
            profile["work"] = work
        except:
            pass

        try:
            profile["feed"] = profile["feed"]["data"]
        except:
            pass

        try:
            profile["likes"] = profile["likes"]["data"]
        except:
            pass

        try:
            profile["albums"] = profile["albums"]["data"]
        except:
            pass

        try:
            profile["picture"] = profile["picture"]["data"]["url"]
        except:
            pass

        return profile

    def get_profile(self, id="me"):

        try:
            print self.facebook.get_object(cat='single', id=id, fields=[])["error"]["message"]
            return {}
        except:
            pass

        profile = {}
        keys = ["birthday", "about", "age_range", "education", "devices", "email", "first_name", "gender", "hometown",
                  "inspirational_people", "interested_in", "location", "languages", "last_name", "political",
                  "public_key", "quotes", "religion", "relationship_status", "significant_other", "work", "albums",
                  "friends", "family", "feed", "likes", "picture", "cover"]

        for key in keys:
            try:
                field = self.get_field(key, id)
                profile.setdefault(key, field[key])
            except:
                profile.setdefault(key)

        return self.clean_profile(profile)

    def get_wall_post_ids(self, id="me"):
        # return id of wall_posts
        # return "events" from wall
        e = []
        try:
            p = self.get_field("feed", id)["feed"]["data"]
        except: #no acess
            return e
        for i in p:
            try:
                e.append(i["id"])
            except:
                pass
        return e

    def get_wall_posts(self, id="me"):
        # return "events" from wall
        p = self.get_field("feed", id)
        e = []
        try:
            p = p["feed"]["data"]
        except:
            # no acess to this users
            return e

        for i in p:
            try:
                l = {}
                l.setdefault("message", i["message"])
                l.setdefault("created_time", i["created_time"])
                l.setdefault("id", i["id"])
                e.append(l)
            except:
                pass
        return e

    def get_wall_events(self, id="me"):
        # return "events" from wall
        e = []
        try:
            p = self.get_field("feed", id)["feed"]["data"]
        except:
            return e
        for i in p:
            try:
                l = {}
                l.setdefault("story", i["story"])
                l.setdefault("created_time", i["created_time"])
                l.setdefault("id", i["id"])
                e.append(l)
            except:
                pass
        return e

    def get_wall_comments(self, id="me"):
        ids = self.get_wall_post_ids(id)
        comments = {}
        for i in ids:
            comme = self.get_field("comments", i)
            try:
                comments.setdefault(i, comme["comments"]["data"])
            except:
                # " no comments"
                pass
        cleaned = []
        for wall_post_id in comments:
            com = {}
            com.setdefault("wall_post_id", wall_post_id)
            for comment in comments[wall_post_id]:
                com.setdefault("comment_id", comment["id"])
                com.setdefault("comment", comment["message"].encode("utf8"))
                com.setdefault("sender", comment["from"]["name"].encode("utf8"))
                com.setdefault("sender_id", comment["from"]["id"])
                com.setdefault("date", comment["created_time"])
                cleaned.append(com)
        return cleaned

    def get_likes(self, id="me"):
        lik = []
        try:
            likes = self.get_field("likes", id)["likes"]["data"]
        except:  # no acess
            return lik
        for like in likes:
            lik.append(like["name"])
        return lik

    def get_detailed_like_info(self, id="me"):
        lik = []
        try:
            likes = self.get_field("likes", id)["likes"]["data"]
        except: #no acess
            return lik

        for like in likes:
            l = {}
            l.setdefault("name", like["name"])
            p = self.get_profile(like["id"])
            for key in p:
                l.setdefault(key, p[key])
            lik.append(l)
        return lik

    def get_albums(self, id="me"):
        try:
            print self.facebook.get_object(cat='single', id=id, fields=[])["error"]["message"]
            return []
        except:
            pass

        al = []
        try:
            albums = self.get_field("albums", id)["albums"]["data"]
        except:# no acess
            return al

        for f in albums:
            a = {}
            a.setdefault("name", f["name"])
            a.setdefault("id", f["id"])
            a.setdefault("created_time", f["created_time"])
            try:
                photos = self.get_field("photos", f["id"])["photos"]["data"]
            except:
                photos = None

            a.setdefault("photos", photos)
            try:
                likes = self.get_field("likes", f["id"])["likes"]["data"]
                a.setdefault("likes", likes)
            except:
                a.setdefault("likes")
            al.append(a)
        return al

    def get_people_who_liked(self, id="me"):
        people = {}
        # get people who liked feed posts
        posts = self.get_wall_post_ids(id)
        for p in posts:
            try:
                likes = self.get_field("likes", p)["likes"]["data"]
                for like in likes:
                    people.setdefault(like["name"], like["id"])
            except:
                pass #no likes
        # get people who liked albums
        albums = self.get_albums(id)
        for a in albums:
            try:
                likes = a["likes"]
                for like in likes:
                    people.setdefault(like["name"], like["id"])
            except:
                pass  # no likes
        # get people who commented
        comments = self.get_wall_comments(id)
        for c in comments:
            people.setdefault(c["sender"], c["sender_id"])

        return people

    def commented_on(self, id="me"):
        answered = False
        replys = self.get_field("comments", id)
        replys = replys["comments"]["data"]
        for reply in replys:
            if reply["from"]["id"] == self.id:
                answered = True
        return answered

    def like(self, id):
        # TODO fix some other way
        liked = self.facebook.publish(cat="likes", id=id)
        try:
            print liked["error"]["message"]
        except:
            print liked

    def answer_comments_from(self, from_id="me", where_id="me", text=":)"):
        # TODO answer posts in wall
        # answer replys to posts in wall
        comments = self.get_wall_comments(where_id)
        for comment in comments:
            if comment["sender_id"] == from_id:
                answered = self.commented_on(comment["comment_id"])
                if not answered:
                    self.comment_object(comment["comment_id"], text)

    def delete(self, id):
        # TODO fix permissions
        return self.facebook.delete(id=id)

    def create_event(self):
        # TODO change, deprecated
        return self.facebook.publish(cat="events", id="me", name="Become self aware", start_time="2018-10-16-12:20",
                         end_time="2018-10-18-14:30")


class FaceChat(fbchat.Client):

    def __init__(self, email, password, emitter=None, active=False, debug=True, user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"):
        fbchat.Client.__init__(self, email, password, debug, user_agent)
        self.log = getLogger("Facebook Chat")
        self.emitter = emitter
        self.emitter.on("fb_chat_message", self.handle_chat_request)
        self.emitter.on("speak", self.handle_speak)
        self.queue = [] #[[author_id , utterance, name]]
        self.monitor_thread = None
        self.queue_thread = None
        self.start_threads()
        self.privacy = False
        self.active = active

    def activate_client(self):
        self.active = True

    def deactivate_client(self):
        self.active = False

    def _queue(self):
        while True:
            # check if there is a utterance in queue
            if len(self.queue) > 0:
                self.log.debug("Processing queue")
                chat = self.queue[0]
                # send that utterance to skills
                self.log.debug("Processing utterance " + chat[1] + " for user " + str(chat[0]))
                chatmsg = chat[1]
                self.emitter.emit(
                    Message("recognizer_loop:utterance",
                            {'utterances': [chatmsg], 'source': 'fbchat_'+chat[0], "mute": True, "user":chat[2]}))
                # remove from queue
                self.log.debug("Removing item from queue")
                self.queue.pop(0)
            time.sleep(0.3)

    def start_threads(self):
        self.log.debug("Starting chat listener thread")
        self.monitor_thread = Thread(target=self.listen)
        self.monitor_thread.setDaemon(True)
        self.monitor_thread.start()

        self.log.debug("Starting utterance queue thread")
        self.queue_thread = Thread(target=self._queue)
        self.queue_thread.setDaemon(True)
        self.queue_thread.start()

    def stop(self):
        if self.listening():
            self.stop_listening()
        self.monitor_thread.exit()
        self.queue_thread.exit()

    def get_last_messages(self, id):
        last_messages = self.getThreadInfo(id, 0)
        last_messages.reverse()  # messages come in reversed order

        for message in last_messages:
            print(message.body)

        return last_messages

    def get_user_name(self, user_id):
        users = self.getAllUsers()
        for user in users:
            if user.uid == user_id:
                return user.name

    def on_message(self, mid, author_id, author_name, message, metadata):
        # for privacy we may want this off
        if not self.privacy:
            self.markAsDelivered(author_id, mid) #mark delivered
            self.markAsRead(author_id) #mark read

        # if you are not the author, process
        if str(author_id) != str(self.uid) and self.emitter is not None:
            author_name = self.get_user_name(author_id)
            self.emitter.emit(Message("fb_chat_message", {"author_id": author_id, "author_name": author_name, "message": message}))

    def handle_chat_request(self, message):
        txt = message.data.get('message')
        user = message.data.get('author_id')
        user_name = message.data.get('author_name')
        # TODO check with intent parser if intent from control center wont be used (change run-level)
        # read from config skills to be blacklisted
        if self.active:
            self.log.debug("Adding " + txt + " from user " + user_name + " to queue")
            self.queue.append([user, txt, user_name])

    def handle_speak(self, message):
        utterance = message.data.get("utterance")
        target = message.data.get("target")
        metadata = message.data.get("metadata")
        if "fbchat" in target and self.active:
            if "dream_url" in metadata.keys():
                utterance += " " + metadata["dream_url"]
            user = target.replace("fbchat_", "")
            if user.isdigit():
                self.send(user, utterance)
            else:
                self.log.error("invalid user id " + user)


class FacebookSkill(MycroftSkill):

    def __init__(self):
        super(FacebookSkill, self).__init__(name="FacebookSkill")
        self.reload_skill = True
        try:
            self.api_key = self.config_apis['GraphAPI']
        except:
            self.api_key = self.config['graph_api_key']
        self.mail = self.config['mail']
        self.passwd = self.config['passwd']
        self.active = self.config['chat_client']
        self.default_target = self.config['default_target']
        self.speak_messages = self.config['speak_messages']
        self.like_back = self.config['like_back']
        self.speak_posts = self.config['speak_posts']
        self.firefox_path = self.config['firefox_path']
        self.friend_num = self.config['friend_num'] #number of friends to add
        self.photo_num = self.config['photo_num'] #number of photos to like
        self.friends = self.config['friends']
        self.default_comment = self.config['default_comment']
        # TODO make these a .txt so the corpus can be easily extended
        self.motivational = self.config['motivational']
        self.girlfriend_messages = self.config['girlfriend_messages']
        self.random_chat = self.config['random_chat']

    def initialize(self):
        # start bots
        self.face = FaceBot(self.api_key)
        self.selenium_face = None #SeleniumFaceBot(self.mail, self.passwd, self.firefox_path)
        self.chat = FaceChat(self.mail, self.passwd, self.emitter, debug=False, active=self.active)
        self.face_id = self.face.get_self_id()
        # populate friend ids
        self.get_ids_from_chat() # TODO make an intent for this?
        # listen for chat messages
        self.emitter.on("fb_chat_message", self.handle_chat_message)
        self.emitter.on("fb_post_request", self.handle_post_request)
        self.build_intents()
        time.sleep(60)

    def build_intents(self):
        # build intents
        friend_number_intent = IntentBuilder("FbGetFriendNumberIntent").\
            require("friend_numberKeyword").build()
        self.register_intent(friend_number_intent,
                             self.handle_friend_number_intent)

        who_friend_intent = IntentBuilder("FbGetFriendNamesIntent"). \
            require("who_friendsKeyword").build()
        self.register_intent(who_friend_intent,
                             self.handle_who_are_my_friends_intent)

        like_random_intent = IntentBuilder("FbLikeRandomPhotoIntent"). \
            require("Like_Random_Photos_Keyword").build()
        self.register_intent(like_random_intent,
                             self.handle_like_photos_intent)

        suggested_friends_intent = IntentBuilder("FbAddSuggestedFriendIntent"). \
            require("Add_Suggested_Friends_Keyword").build()
        self.register_intent(suggested_friends_intent,
                             self.handle_make_friends_intent)

        friends_of_friends_intent = IntentBuilder("FbAddFriendsofFriendsIntent"). \
            require("Add_Friends_of_Friends_Keyword").build()
        self.register_intent(friends_of_friends_intent,
                             self.handle_make_friends_of_friends_intent)

        who_liked_intent = IntentBuilder("FbWhoLikedMeIntent"). \
            require("who_liked_me_Keyword").build()
        self.register_intent(who_liked_intent,
                             self.handle_who_liked_me_intent)

        motivate_mycroft_intent = IntentBuilder("FbMotivateMycroftIntent"). \
            require("motivate_mycroft_Keyword").build()
        self.register_intent(motivate_mycroft_intent,
                             self.handle_motivate_makers_intent)

        chat_girlfriend_intent = IntentBuilder("FbChatGirlfriendIntent"). \
            require("chat_girlfriend_Keyword").build()
        self.register_intent(chat_girlfriend_intent,
                             self.handle_chat_girlfriend_intent)

        about_me_intent = IntentBuilder("FbBuildAboutMeIntent"). \
            require("make_about_me_Keyword").build()
        self.register_intent(about_me_intent,
                             self.handle_build_about_me_intent)

        chat_someone_intent = IntentBuilder("FbChatRandomIntent"). \
            require("chat_random_Keyword").build()
        self.register_intent(chat_someone_intent,
                             self.handle_random_chat_intent)

        my_likes_intent = IntentBuilder("FbMyLikesIntent"). \
            require("what_do_i_like_Keyword").build()
        self.register_intent(my_likes_intent,
                             self.handle_my_likes_intent)

        answer_mom_intent = IntentBuilder("FbReplyMomIntent"). \
            require("comment_all_from_mom_Keyword").build()
        self.register_intent(answer_mom_intent,
                             self.handle_comment_all_from_intent)

        refresh_friendlist_intent = IntentBuilder("FbRefreshListIntent"). \
            require("refresh_friendlist_Keyword").build()
        self.register_intent(refresh_friendlist_intent,
                             self.get_ids_from_chat)

    def get_ids_from_chat(self, message=None):
        if message is not None: #user triggered
            # TODO use dialog
            self.speak("Updating friend list from chat")
        # map ids to names from chat
        users = self.chat.getAllUsers()
        for user in users:
            self.friends.setdefault(user.name, user.uid)

    def get_name_from_id(self, id):
        for friend in self.friends:
            if self.friends[friend] == id:
                return friend

    def handle_post_request(self, message):
        # TODO get target from message
        #type = message.data["type"]
        text = message.data["text"].encode("utf8")
        link = message.data["link"]
        speech = message.data["speech"]
        id = message.data["id"]
        #if type == "text" or type == "link":
        self.face.post_to_wall(text=text, id=id, link=link)
        #else:
            # TODO more formatted post types
        #    pass
        if self.speak_posts:
            self.speak(speech)

    def handle_chat_message(self, message):
        text = message.data["message"]
        author = message.data["author_id"]
        # on chat message speak it
        if self.speak_messages:
            text = self.get_name_from_id(author) + " said " + text
            self.speak(text)
        # on chat message like that persons photos
        if self.like_back:
            self.selenium_face.login()
            self.selenium_face.like_photos_from(author, self.photo_num)
            self.selenium_face.close()

    def handle_who_are_my_friends_intent(self, message):
        text = ""
        for friend in self.friends.keys():
            text += friend + ",\n"
        if text != "":
            self.speak_dialog("who_friends")
            self.speak(text)
        else:
            self.speak("i have no friends")

    def handle_friend_number_intent(self, message):
        self.speak_dialog("friend_number", {"number": self.face.get_friend_num()})

    def handle_post_friend_number_intent(self, message):
        self.speak_dialog("post_friend_number")
        num_friends = self.face.get_friend_num()
        time = asctime()
        message = "i have " + str(num_friends) + " friends on facebook and now is " + str(
            time) + '\nNot bad for an artificial inteligence'
        self.face.post_to_wall(message)

    def handle_like_photos_old_intent(self, message):
        self.speak_dialog("like_photos")
        self.selenium_face.login()
        self.selenium_face.like_photos(number=self.photo_num)
        self.selenium_face.close()

    def handle_like_photos_intent(self, message):
        self.speak_dialog("like_photos")
        self.get_ids_from_chat()
        friend = random.choice(self.friends.keys())
        friend = self.friends[friend]
        self.selenium_face.login()
        self.selenium_face.like_photos_from(friend, self.photo_num)
        self.selenium_face.close()

    def handle_make_friends_intent(self, message):
        self.speak_dialog("make_friend")
        self.selenium_face.login()
        self.selenium_face.add_suggested_friends(num=self.friend_num)
        self.selenium_face.close()

    def handle_make_friends_of_friends_intent(self, message):
        # TODO own dialog
        self.speak_dialog("make_friend")
        self.get_ids_from_chat()
        friend = random.choice(self.friends.keys())
        friend = self.friends[friend]
        self.selenium_face.login()
        self.selenium_face.add_friends_of(friend, self.friend_num)
        self.selenium_face.close()

    def handle_who_liked_me_intent(self, message):
        people = self.face.get_people_who_liked()
        self.speak_dialog("liked_my_stuff")
        for p in people:
            self.speak(p)

    def handle_chat_girlfriend_intent(self, message):
        # text = message.data["text"]
        text = random.choice(self.girlfriend_messages)
        # TODO use dialog
        self.speak("Just sent a text message to girlfriend, i told her " + text)
        id = self.friends["girlfriend"]
        self.chat.send(id, text)

    def handle_build_about_me_intent(self, message):
        # TODO use dialog
        self.speak("Building about me section on facebook")
        self.selenium_face.login()
        self.selenium_face.build_about_me()
        self.selenium_face.close()

    def handle_my_likes_intent(self, message):
        likes = self.face.get_likes()
        self.speak_dialog("likes", {"number": len(likes)})
        i = 0
        for like in likes:
            self.speak(like)
            i += 1
            if i > 5:
                return

    def handle_random_chat_intent(self, message):
        text = random.choice(self.random_chat)
        person = random.choice(self.friends.keys())
        id = self.friends[person]
        self.chat.send(id, text)
        # TODO use dialog
        self.speak("Just sent a text message to " + person + ", i said " + text)

    # TODO finish these
    def handle_motivate_makers_intent(self, message):
        # TODO randomly choose someone from mycroft team
        person = "100014192855507"  # atchison
        message = random.choice(self.motivational)
        # TODO randomly chat/ or post to wall
        self.chat.send(person, message)
        # TODO use dialog
        self.speak("I said " + message + " to " + self.get_name_from_id(person))

    def handle_last_wall_post_intent(self, message):
        posts = self.face.get_wall_posts()
        # TODO sort by time (or is it sorted?)
        self.speak(posts[0]["message"])

    def handle_chat_person_intent(self, message):
        person = message.data["person"]
        text = message.data["text"]
        try:
            id = self.friends[person]
            self.chat.send(id, text)
        except:
            self.speak_dialog("unknown_person")

    def handle_comment_all_from_intent(self, message):
        # TODO make regex
        #name = message.data["name"]
        name = "mom"
        # TODO optionally get comment from message
        #text = message.data["text"]
        text = self.default_comment
        person_id = self.friends[name]
        self.face.answer_comments_from(person_id, text=text)
        # TODO use dialog
        self.speak("I am replying to all comments from " + name + " with a smiley")

    def handle_add_friends_of_friend_intent(self, message):
        person = message.data["person"]
        id = self.friends[person]
        self.selenium_face.login()
        self.selenium_face.add_friends_of(id, self.friend_num)
        self.selenium_face.close()

    def handle_like_photos_of_intent(self, message):
        person = message.data["person"]
        id = self.friends[person]
        self.selenium_face.login()
        self.selenium_face.like_photos_from(id, self.photo_num)
        self.selenium_face.close()

    def stop(self):
        self.chat.stop()
        try:
            self.selenium_face.close()
        except:
            pass


def create_skill():
    return FacebookSkill()
