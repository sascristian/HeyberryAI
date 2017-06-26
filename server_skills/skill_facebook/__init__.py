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


import requests
import fbchat
from fbchat.utils import *
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message
import random
from time import sleep, asctime
from threading import Thread
import time, sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))
from browser_service import BrowserControl
from mycroft.skills.settings import SkillSettings

__author__ = 'jarbas'

# TODO logs in bots

import logging
# disable logs from requests and urllib 3, or there is too much spam from facebook
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)



def checkRequest(r, do_json_check=True):
    if not r.ok:
        raise Exception('Error when sending request: Got {} response'.format(r.status_code))

    content = get_decoded(r)
    c = content.replace("for (;;); ","").replace("for (;;);","")
    if content is None or len(content) == 0:
        raise Exception('Error when sending request: Got empty response')

    if do_json_check:
        try:
            j = json.loads(c)
        except Exception as e:
            raise Exception('Error while parsing JSON: {}'.format(repr(content)))
        check_json(j)
        return j
    else:
        return content


class FaceChat(fbchat.Client):
    def __init__(self, email, password, emitter=None, active=True, user_agent=None, max_tries=5, session_cookies=None, logging_level=logging.INFO):
        """Initializes and logs in the client

        :param email: Facebook `email`, `id` or `phone number`
        :param password: Facebook account password
        :param user_agent: Custom user agent to use when sending requests. If `None`, user agent will be chosen from a premade list (see :any:`utils.USER_AGENTS`)
        :param max_tries: Maximum number of times to try logging in
        :param session_cookies: Cookies from a previous session (Will default to login if these are invalid)
        :param logging_level: Configures the `logging level <https://docs.python.org/3/library/logging.html#logging-levels>`_. Defaults to `INFO`
        :type max_tries: int
        :type session_cookies: dict
        :type logging_level: int
        :raises: Exception on failed login
        """

        self.sticky, self.pool = (None, None)
        self._session = requests.session()
        self.req_counter = 1
        self.seq = "0"
        self.payloadDefault = {}
        self.client = 'mercury'
        self.default_thread_id = None
        self.default_thread_type = None

        if not user_agent:
            user_agent = random.choice(USER_AGENTS)

        self._header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': ReqUrl.BASE,
            'Origin': ReqUrl.BASE,
            'User-Agent': user_agent,
            'Connection': 'keep-alive',
        }

        handler.setLevel(logging_level)

        # If session cookies aren't set, not properly loaded or gives us an invalid session, then do the login
        if not session_cookies or not self.setSession(session_cookies) or not self.isLoggedIn():
            self.login(email, password, max_tries)

        self.log = log
        self.ws = emitter
        if self.ws is not None:
            self.ws.on("fb_chat_message", self.handle_chat_request)
            self.ws.on("speak", self.handle_speak)
        else:
            self.log.error("No emitter was provided to facebook chat")
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
                # NOTE user id skill checks for photo param
                self.ws.emit(
                    Message("recognizer_loop:utterance",
                            {'utterances': [chatmsg], 'source': 'fbchat_'+chat[0], "mute": True, "user":chat[2], "photo":chat[3]}))
                # remove from queue
                self.log.debug("Removing item from queue")
                self.queue.pop(0)
            time.sleep(2)

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
        self.monitor_thread.exit()
        self.queue_thread.exit()
        self.stopListening()

    def get_user_name(self, user_id):
        return self.fetchUserInfo(user_id)[user_id].name

    def get_user_photo(self, user_id):
        return self.fetchUserInfo(user_id)[user_id].photo

    def get_user_id(self, user_name):
        users = self.searchForUsers(user_name)
        return users[0].uid

    def handle_chat_request(self, message):
        txt = message.data.get('message')
        user = message.data.get('author_id')
        user_name = message.data.get('author_name')
        user_photo = message.data.get('photo')
        # TODO read from config skills to be blacklisted
        if self.active:
            self.log.debug("Adding " + txt + " from user " + user_name + " to queue")
            self.queue.append([user, txt, user_name, user_photo])

    def handle_speak(self, message):
        utterance = message.data.get("utterance")
        target = message.data.get("target")
        metadata = message.data.get("metadata")
        if "fbchat" in target and self.active:
            if "url" in metadata.keys():
                utterance += "\n url: " + metadata["url"]
            elif "link" in metadata.keys():
                utterance += "\n url: " + metadata["link"]

            user = target.replace("fbchat_", "")
            if user.isdigit():
                self.sendMessage(utterance, thread_id=user, thread_type=ThreadType.USER)
            else:
                self.log.error("invalid user id " + user)

    def onMessage(self, author_id, message, thread_id, thread_type, **kwargs):
        # for privacy we may want this off
        if not self.privacy:
            self.markAsDelivered(author_id, thread_id)  # mark delivered
            self.markAsRead(author_id)  # mark read

        self.log.info("Message from " + author_id + ": " + message)

        if str(author_id) != str(self.uid) and self.ws is not None:
            author_name = self.get_user_name(author_id)
            author_photo = self.get_user_photo(author_id)
            self.ws.emit(Message("fb_chat_message",
                                 {"author_id": author_id, "author_name": author_name, "message": message,
                                      "photo": author_photo}))


class FacebookSkill(MycroftSkill):

    def __init__(self):
        super(FacebookSkill, self).__init__(name="FacebookSkill")
        self.reload_skill = False
        self.mail = self.config['mail']
        self.passwd = self.config['passwd']
        self.fb_settings = SkillSettings(dirname(__file__) + '/settings.json')
        if "cookies" not in self.fb_settings.keys():
            self.fb_settings["cookies"] = []
            self.fb_settings.store()
        if "session" not in self.fb_settings.keys():
            self.fb_settings["session"] = None
            self.fb_settings.store()
        # chat client active
        self.active = self.config.get('chat_client', True)
        # speak when message received
        self.speak_messages = self.config.get('speak_messages', True)
        # TODO who to warn?
        self.default_target = ""
        # like user photo when user talks on chat
        self.like_back = self.config.get('like_back', True)
        # tell user when making a post
        self.speak_posts = self.config.get('speak_posts', True)
        # number of friends to add
        self.friend_num = self.config.get('friend_num', 2)
        # number of photos to like
        self.photo_num = self.config.get('photo_num', 2)
        # pre-defined friend list / nicknames
        self.friends = self.config.get('friends', {})
        # default reply to wall posts
        self.default_comment = self.config.get('default_comment', [":)"])
        self.logged_in = False

        # TODO make these a .txt so the corpus can be easily extended
        self.motivational = self.config.get('motivational', ["may the source be with you"])
        self.girlfriend_messages = self.config.get('girlfriend_messages', ["AI can also love"])
        self.random_chat = self.config.get('random_chat', ["one day AI and humans will drink beer together"])

    def initialize(self):
        # start chat
        if self.fb_settings["session"] is None:
            self.chat = FaceChat(self.mail, self.passwd, emitter=self.emitter, active=self.active)
            self.get_session()
        else:
            self.chat = FaceChat(self.mail, self.passwd, emitter=self.emitter, active=self.active, session_cookies=self.fb_settings["session"])

        self.face_id = self.chat.uid
        self.browser = BrowserControl(self.emitter)
        # populate friend ids
        self.get_ids_from_chat() # TODO make an intent for this?
        # listen for chat messages
        self.emitter.on("fb_chat_message", self.handle_chat_message)
        self.emitter.on("fb_post_request", self.handle_post_request)
        self.build_intents()
        self.logged_in = self.login()

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

    def get_session(self):
        try:
            # get chat session
            self.fb_settings["session"] = self.chat.getSession()
            self.fb_settings.store()
        except Exception as e:
            self.log.error(e)

    # browser service methods
    def get_cookies(self, reset=True):
        cookies = self.browser.get_cookies()
        if reset:
            self.fb_settings["cookies"] = []
        for cookie in cookies:
            if "facebook" in cookie["domain"] and cookie not in self.fb_settings["cookies"]:
                self.fb_settings["cookies"].append(cookie)
        self.fb_settings.store()

    def login(self):

        if len(self.fb_settings["cookies"]) > 0:
            self.log.info("attempting to use last session cookies")
            if self.browser.add_cookies(self.fb_settings["cookies"]):
                self.log.info("cookies set, not logging in")
                return True
        self.browser.open_url("m.facebook.com")
        if self.browser.get_current_url() is None:
            self.log.error("Browser service doesnt seem to be started")
            return False
        while "facebook" not in self.browser.get_current_url():
            sleep(0.2)
        self.browser.get_element(data=".//*[@id='login_form']/ul/li[1]/input", name="input", type="xpath")
        self.browser.send_keys_to_element(text=self.mail, name="input", special=False)
        self.browser.get_element(data=".//*[@id='login_form']/ul/li[2]/div/input", name="passwd", type="xpath")
        self.browser.send_keys_to_element(text=self.passwd, name="passwd", special=False)
        self.browser.get_element(data=".//*[@id='login_form']/ul/li[3]/input", name="login", type="xpath")
        self.get_cookies()
        return self.browser.click_element("login")

    def post_to_wall(self, keys):
        if not self.logged_in:
            self.logged_in = self.login()
        url = self.browser.get_current_url()
        url2 = url
        self.browser.open_url("m.facebook.com/me")  # profile page
        while url2 == url:
            url2 = self.browser.get_current_url()
            sleep(0.1)
        self.browser.get_element(data=".// *[ @ id = 'u_0_0']", name="post_box", type="xpath")
        self.browser.click_element("post_box")
        self.browser.send_keys_to_element(text=keys, name="post_box", special=False)
        sleep(5)
        self.browser.get_element(data=".//*[@id='timelineBody']/div[1]/div[1]/form/table/tbody/tr/td[2]/div/input", name="post_button", type="xpath")
        self.browser.click_element("post_button")

    def add_suggested_friends(self, num=3):
        if not self.logged_in:
            self.logged_in = self.login()
        i = 0
        while i <= num:
            fails = 0
            self.browser.open_url("https://m.facebook.com/friends/center/mbasic/") # people you may now page
            self.log.info(self.browser.get_current_url())
            # .//*[@id='friends_center_main']/div[3]/div[1]/table/tbody/tr/td[2]/div[2]/a[1]
            # ".//*[@id='friends_center_main']/div[2]/div[2]/table/tbody/tr/td[2]/div[2]/a[1]"
            sucess = False
            while not sucess and fails < 5:
                # possible xpath 1
                if self.browser.get_element(data=".//*[@id='friends_center_main']/div[2]/div[2]/table/tbody/tr/td[2]/div[2]/a[1]",
                                               name="add_friend",
                                               type="xpath"):
                    sucess = True
                else:
                    # possible xpath 2
                    sucess = self.browser.get_element(data=".//*[@id='friends_center_main']/div[3]/div[1]/table/tbody/tr/td[2]/div[2]/a[1]",
                                               name="add_friend",
                                               type="xpath")
                fails += 1

            if self.browser.click_element("add_friend"):
                self.log.info("Friend added!")
            else:
                self.log.error("Could not add friend")
            i += 1
        sleep(60)

    def like_photos_from(self, id, num=3):
        if not self.logged_in:
            self.logged_in = self.login()
        id = str(id) #in case someone passes int
        link = "https://m.facebook.com/profile.php?id=" + id
        self.browser.open_url(link)  # persons profile page
        path = ".//*[@id='m-timeline-cover-section']/div[4]/a[3]"
        if not self.browser.get_element(data=path, name="photos", type="xpath"):
            self.log.error("cant find photos link")
            return

        self.browser.click_element("photos")
        while "m.facebook.com/profile.php?v=photos" not in self.browser.get_current_url():
            sleep(0.3)
        if self.browser.get_element(data=".//*[@id='u_0_0']/img",
                                    name="profile_photo",
                                    type="xpath"):
            self.browser.click_element("profile_photo")
        else:
            self.log.warning("Could not click profile picture")
            if self.browser.get_element(data=".//*[@id='root']/div[2]/div[3]/div/ul/li[1]/table/tbody/tr/td/span/a",
                                        name="profile_pics",
                                         type="xpath"):
                self.browser.click_element("profile_pics")
            else:
                self.log.warning("Could not click profile pictures link")
                if self.browser.get_element(data=".//*[@id='root']/div[2]/div[3]/div/ul/li[3]/table/tbody/tr/td/span/a",
                                             name="timeline_photos",
                                             type="xpath"):
                    self.browser.click_element("timeline_photos")
                else:
                    self.log.warning("Could not click timeline photos")
                    if self.browser.get_element(data=".//*[@id='root']/div[2]/div[3]/div/ul/li[2]/table/tbody/tr/td/span/a",
                                                name="mobile",
                                                type="xpath"):
                        self.browser.click_element("mobile")
                    else:
                        self.log.warning("Could not click mobile uploads")
        sleep(3)
        # click like
        c1 = 0
        while not c1 <= num:
            if not self.browser.get_element(data=".//*[@id='root']/div[1]/div/div[2]/div/table/tbody/tr/td[1]/a", name="like_button",
                                     type="xpath"):
                self.browser.get_element(data=".//*[@id='MPhotoActionbar']/div/table/tbody/tr/td[1]/a/span",
                                         name="like_button",
                                         type="xpath")
            self.browser.click_element("like_button")
            sleep(5)
            url2 = self.browser.get_current_url()
            if "https://m.facebook.com/reactions" in url2:  # already liked opened reaction page
                self.browser.go_back()
            while "https://m.facebook.com/reactions" in self.browser.get_current_url():
                sleep(0.3)
            if self.browser.get_element(data=".//*[@id='root']/div[1]/div/div[1]/div[2]/table/tbody/tr/td[2]/a",
                                         name="next_button",
                                         type="xpath"):
                self.browser.click_element("next_button")
                sleep(2)
            else:
                self.log.error("next photo button not found: ")
                break
            c1 += 1

    def make_friends_off(self, id, num=3):
        pass

    # internal methods
    def get_ids_from_chat(self, message=None):
        if message is not None: #user triggered
            # TODO use dialog
            self.speak("Updating friend list from chat")
        # map ids to names from chat
        users = self.chat.fetchAllUsers()
        for user in users:
            self.friends.setdefault(user.name, user.uid)

    def get_name_from_id(self, id):
        return self.chat.get_user_name(str(id))

    def get_id_from_name(self, name):
        return self.chat.get_user_id(name)

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
            self.like_photos_from(author, self.photo_num)


    # intents

    def handle_friend_number_intent(self, message):
        #self.add_suggested_friends(1)
        self.like_photos_from("100009535576189")
        #self.post_to_wall("can i login by re-using cookies intead of mail and passwd?")
       # self.speak_dialog("friend_number", {"number": self.face.get_friend_num()})

    def handle_who_are_my_friends_intent(self, message):
        text = ""
        for friend in self.friends.keys():
            text += friend + ",\n"
        if text != "":
            self.speak_dialog("who_friends")
            self.speak(text)
        else:
            self.speak("i have no friends")

    def handle_post_friend_number_intent(self, message):
        self.speak_dialog("post_friend_number")
        num_friends = 0 #self.face.get_friend_num()
        time = asctime()
        message = "i have " + str(num_friends) + " friends on facebook and now is " + str(
            time) + '\nNot bad for an artificial inteligence'
        #self.face.post_to_wall(message)

    def handle_like_photos_intent(self, message):
        self.speak_dialog("like_photos")
        self.get_ids_from_chat()
        friend = random.choice(self.friends.keys())
        friend = self.friends[friend]
        self.like_photos_from(friend, self.photo_num)

    def handle_make_friends_intent(self, message):
        self.speak_dialog("make_friend")
        self.add_suggested_friends(self.friend_num)

    def handle_make_friends_of_friends_intent(self, message):
        # TODO own dialog
        self.speak_dialog("make_friend")
        self.get_ids_from_chat()
        friend = random.choice(self.friends.keys())
        friend = self.friends[friend]
      #  self.selenium_face.login()
       # self.selenium_face.add_friends_of(friend, self.friend_num)
       # self.selenium_face.close()

    def handle_who_liked_me_intent(self, message):
      #  people = self.face.get_people_who_liked()
        self.speak_dialog("liked_my_stuff")
        #for p in people:
        #    self.speak(p)

    def handle_chat_girlfriend_intent(self, message):
        # text = message.data["text"]
        text = random.choice(self.girlfriend_messages)
        # TODO use dialog
        self.speak("Just sent a text message to girlfriend, i told her " + text)
        id = self.friends["girlfriend"]
        self.chat.sendMessage(text, id)

    def handle_build_about_me_intent(self, message):
        # TODO use dialog
        self.speak("Building about me section on facebook")
       # self.selenium_face.login()
       # self.selenium_face.build_about_me()
       # self.selenium_face.close()

    def handle_my_likes_intent(self, message):
       # likes = self.face.get_likes()
        #self.speak_dialog("likes", {"number": len(likes)})
        i = 0
        #for like in likes:
           # self.speak(like)
        #    i += 1
        #    if i > 5:
        #        return

    def handle_random_chat_intent(self, message):
        text = random.choice(self.random_chat)
        person = random.choice(self.friends.keys())
        id = self.friends[person]
        self.chat.sendMessage(text, id)
        # TODO use dialog
        self.speak("Just sent a text message to " + person + ", i said " + text)

    # TODO finish these
    def handle_motivate_makers_intent(self, message):
        # TODO randomly choose someone from mycroft team
        person = "100014192855507"  # atchison
        message = random.choice(self.motivational)
        # TODO randomly chat/ or post to wall
        self.chat.sendMessage(text, person)
        # TODO use dialog
        self.speak("I said " + message + " to " + self.get_name_from_id(person))

    def handle_last_wall_post_intent(self, message):
       # posts = self.face.get_wall_posts()
        # TODO sort by time (or is it sorted?)
        #self.speak(posts[0]["message"])
        pass

    def handle_chat_person_intent(self, message):
        # TODO fuzzymatch
        person = message.data["person"]
        text = message.data["text"]
        try:
            id = self.friends[person]
            self.chat.sendMessage(text, id)
        except Exception as e:
            self.speak_dialog("unknown_person")
            self.log.error(e)

    def handle_comment_all_from_intent(self, message):
        # TODO make regex
        #name = message.data["name"]
        name = "mom"
        # TODO optionally get comment from message
        #text = message.data["text"]
        text = self.default_comment
        person_id = self.friends[name]
       # self.face.answer_comments_from(person_id, text=text)
        # TODO use dialog
        self.speak("I am replying to all comments from " + name + " with a smiley")

    def handle_add_friends_of_friend_intent(self, message):
        person = message.data["person"]
        id = self.friends[person]
       # self.selenium_face.login()
       # self.selenium_face.add_friends_of(id, self.friend_num)
       # self.selenium_face.close()

    def handle_like_photos_of_intent(self, message):
        person = message.data["person"]
        id = self.friends[person]
        self.like_photos_from(id, self.photo_num)

    def stop(self):
        try:
            self.get_session()
            self.get_cookies()
            self.chat.stop()
        except Exception as e:
            self.log.error(e)


def create_skill():
    return FacebookSkill()
