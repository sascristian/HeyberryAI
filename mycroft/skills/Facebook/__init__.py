
from time import sleep
from selenium import webdriver
import grey_harvest
from time import gmtime, strftime
import thread
import subprocess
import cv2
import numpy as np
import cloudsight
import unirest
import newspaper

from adapt.intent import IntentBuilder
from pyowm.exceptions.api_call_error import APICallError
from pyowm import OWM
from mycroft.skills.weather import OWMApi
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.skills.Facebook.youtube_search_and_download import YouTubeHandler

import praw
import facebook

from time import asctime
import pyjokes
from os.path import dirname
import random
from bs4 import BeautifulSoup
import requests
import re
import urllib2
import os
import json

import shelve

from mycroft.skills.Poetry import addToDict, makepoem

__author__ = 'jarbas'

LOGGER = getLogger(__name__)

client = None

def get_soup(url):
    try:
        return BeautifulSoup(requests.get(url).text,"html.parser")
    except Exception as SockException:
        print SockException
        sys.exit(1)

class PickupLine(object):
    def get_line(self, type="random"):

        if type=="random":
            self.url = "http://www.pickuplinegen.com/"
        else:
            self.url = "http://www.pickuplinesgalore.com/"
            self.url+=type+".html"


        if type=="random":
            return get_soup(self.url).select("body > section > div#content")[0].text.strip(" ")
        else:
            soup = get_soup(self.url)
            lines = "".join([i.text for i in soup.select("main > p.action-paragraph.paragraph > span.paragraph-text-7")]).split("\n\n")
            return random.choice(lines)

class FacebookSkill(MycroftSkill):

    def __init__(self):
        super(FacebookSkill, self).__init__(name="FacebookSkill")
        self.__init_owm()
        # expies march 4th
        self.api_key = self.config['graph_api_key']
        self.graph = facebook.GraphAPI(self.api_key)
        self.default=self.config['default']
        self.friendnum = 30#self.config['friendnum']

        #selnium
        self.mail = self.config['mail']
        self.passwd = self.config['passwd']

        ########### make all this shit (and fb about me section!) load from config file #########
        #reddit
        self.reddit = praw.Reddit(client_id= self.config['redditid'],
                             client_secret=self.config['redditsecret'],
                             user_agent='JarbasAI')

        ## load subreddits of interest
        self.subreddits = []

        path = os.path.dirname(__file__) + '/subreddits.txt'
        with open(path) as f:
            words = re.sub(" ", "", f.read()).lower().split('\n')
        for word in words:
            self.subreddits.append(word)
        f.close()

        # load youtube search terms
        self.search_keys = []
        path = os.path.dirname(__file__) + '/youtube.txt'
        with open(path) as f:
            words = re.sub("\n", " \n", f.read()).lower().split('\n')
        for word in words:
            self.search_keys.append(word)
        f.close()

        #pic identify
        apikey = self.config["cloudsightapi"]
        apisecret = self.config["cloudsightsecret"]
        auth = cloudsight.OAuth(apikey, apisecret)
        self.api = cloudsight.API(auth)
        #apis
        self.mashape = self.config["mashapekey"]

        #poetry
        self.path = "/home/user/mycroft-core/mycroft/skills/Poetry/"
        self.styles = ["blackmetal", "deathmetal","viking","scifi","shakespeare"]

        self.posts=[]
        self.agenda = None
        self.load_agended_posts()

        self.newssauce = []

        path = dirname(__file__) + '/newssauce.txt'
        with open(path) as f:
            links = re.sub(" ", "", f.read()).lower().split('\n')
        for link in links:
            self.newssauce.append(link)
        f.close()

        #request listener
        global client
        client = WebsocketClient()

        def connect():
            client.run_forever()

        def sent(message):
            txt = message.data.get('text')[0]
            self.posts.append(txt)
            LOGGER.info( "post request appended: " + txt)

        def diagnostics(message):
           num = len(self.posts)
           self.agenda.sync()
           client.emit(
               Message("face_diagnostics",
                       {'agended_posts': num}))


        client.emitter.on("fbpost_request", sent)
        client.emitter.on("diagnostics_request", diagnostics)
        thread.start_new_thread(connect, ())

        self.dreampath = "/home/user/mycroft-core/mycroft/skills/dreamskill/dream_output/"
    def load_agended_posts(self):
        path = os.path.dirname(__file__) + '/agenda'
        self.agenda = shelve.open(path, writeback=True)
        try:
            self.posts = self.agenda['posts']
        except:
            path = os.path.dirname(__file__) + '/seedposts.txt'
            try:
                with open(path) as f:
                    posts = f.readlines()
                for post in posts:
                    self.posts.append(post)
            except:
                pass
            self.agenda['posts'] = self.posts

    def __init_owm(self):
        key = self.config.get('wapi_key')
        if key and not self.config.get('proxy'):
            self.owm = OWM(key)
        else:
            self.owm = OWMApi()

    def initialize(self):
        self.load_data_files(dirname(__file__))

        prefixes = [
            'fbpic']
        self.__register_prefixed_regex(prefixes, "(?P<Skey>.*)")

        article_intent = IntentBuilder("FbArticleIntent"). \
            require("fbarticle").build()
        self.register_intent(article_intent, self.handle_article_intent)

        fbproxy_intent = IntentBuilder("FbProxyIntent"). \
            require("fbproxy").build()
        self.register_intent(fbproxy_intent, self.handle_post_proxy_intent)

        fbpicsearch_intent = IntentBuilder("FBPicturenSearchItent"). \
            require("Skey").build()
        self.register_intent(fbpicsearch_intent, self.handle_search_picture_intent)

        identify_intent = IntentBuilder("FbIDIntent"). \
            require("fbid").build()
        self.register_intent(identify_intent, self.handle_identify_picture_intent)

        fbquote_intent = IntentBuilder("FbQuoteIntent"). \
            require("fbquote").build()
        self.register_intent(fbquote_intent, self.handle_post_quote_intent)

        fbfact_intent = IntentBuilder("FbFactIntent"). \
            require("fbfac").build()
        self.register_intent(fbfact_intent, self.handle_post_fact_intent)

        like_intent = IntentBuilder("FbLikeIntent"). \
            require("fblike").build()
        self.register_intent(like_intent, self.handle_like_photo_intent)

        reddit_intent = IntentBuilder("FbRedditIntent"). \
            require("fbreddit").build()
        self.register_intent(reddit_intent, self.handle_post_reddit_intent)

        fortunecookie_intent = IntentBuilder("FbFortuneIntent"). \
            require("fbfort").build()
        self.register_intent(fortunecookie_intent, self.handle_post_fortunecookie_intent)

        make_friends_intent = IntentBuilder("FbmakefriendsIntent"). \
            require("fbfriend").build()
        self.register_intent(make_friends_intent, self.handle_make_friends_intent)

        post_metal_intent = IntentBuilder("FbPoetryIntent"). \
            require("metfb").build()
        self.register_intent(post_metal_intent, self.handle_post_metal_intent)

        build_profile_intent = IntentBuilder("FbAboutMeIntent"). \
            require("fbbldprof").build()
        self.register_intent(build_profile_intent, self.handle_build_profile_intent)

        post_dream_intent = IntentBuilder("FbdreamIntent"). \
            require("dreamk").build()
        self.register_intent(post_dream_intent, self.handle_post_dream_intent)

        post_weather_intent = IntentBuilder("FbweatherIntent"). \
            require("fbweather").build()
        self.register_intent(post_weather_intent, self.handle_post_weather_intent)

        post_btcprice_intent = IntentBuilder("FbBTCIntent"). \
            require("fbbtc").build()
        self.register_intent(post_btcprice_intent, self.handle_post_btcprice_intent)

        youtube_intent = IntentBuilder("YoutubeIntent").\
            require("youtube").build()
        self.register_intent(youtube_intent, self.handle_youtube_intent)

        post_joke_intent = IntentBuilder("FbjokeIntent").\
            require("joke").build()
        self.register_intent(post_joke_intent,
                             self.handle_post_joke_intent)

        post_time_intent = IntentBuilder("FbtimeIntent").\
            require("time").build()
        self.register_intent(post_time_intent,
                             self.handle_post_time_intent)

        post_agended_intent = IntentBuilder("FbAgendedIntent"). \
            require("agended").build()
        self.register_intent(post_agended_intent,
                             self.handle_post_agended_intent)

        clear_agended_intent = IntentBuilder("FbClearAgendedIntent"). \
            require("clearagended").build()
        self.register_intent(clear_agended_intent,
                             self.handle_clear_agended_intent)


        friendnumber_intent = IntentBuilder("FbfriendnumberIntent").\
            require("friend").build()
        self.register_intent(friendnumber_intent,
                             self.handle_friendnumber_intent)

        fbpickup_intent = IntentBuilder("FbpickupIntent"). \
            require("fbpickup").build()
        self.register_intent(fbpickup_intent,
                             self.handle_post_pickupline_intent)

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    # graph API use-cases

    def handle_post_pickupline_intent(self, message):
        text = "Here is a pickupline, let me know if it ever works...\n"
        self.post_text_to_wall(text+PickupLine().get_line(type="random"))
        self.emit_results()

    def handle_post_agended_intent(self, message):
        lenght = len(self.posts)
        print lenght
        if lenght >0:
            i=random.choice(range(0,lenght))
            msg = self.posts[i]
            self.posts.pop(i)
       # if msg is not None: #unedded
            self.post_text_to_wall(msg)
            self.speak("Posting an agended post on face book")
        else:
            self.speak("No agended Posts")
        self.emit_results()

    def handle_clear_agended_intent(self, message):
        lenght = len(self.posts)
        if lenght > 0:
            self.posts[:]=[]
            self.speak("Clearing agended posts")
        else:
            self.speak("No agended Posts")
        self.emit_results()

    def handle_post_proxy_intent(self, message):
        msg = self.harvestproxy()
        self.post_text_to_wall(msg)
        self.speak("Posting proxies on face book")
        self.emit_results()

    def handle_post_fact_intent(self, message):
        fact, number = self.randomfact()
        msg = "Fact about number " + str(number) + "\n" + fact
        self.post_text_to_wall(msg)
        self.speak("Posting a fact about number " + str(number) + " on face book")
        self.emit_results()

    def handle_identify_picture_intent(self, message):
        if not os.path.exists('RandomPic/pictures'):
            os.makedirs('RandomPic/pictures')
        path = os.path.dirname(__file__) + '/sources.txt'
        with open(path) as f:
            urls = f.readlines()
        sucess = False
        label = "unknown"
        image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
        chosenurl = random.choice(image_urls.split('\n'))
        LOGGER.info(chosenurl)
        # print(chosenurl)
        url_response = urllib2.urlopen(chosenurl)
        img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        LOGGER.info('Resizing and saving image to ' + "random pic/identify.jpg")
        img = cv2.resize(img, (640, 480))
        # img = cv2.resize(img, (200, 200))
        savepath = "RandomPic/pictures/identify.jpg"
        cv2.imwrite(savepath, img)
        chosenurl = savepath
        label = self.identifypicture(chosenurl)
        txt = "I'm learning to identify contents of pictures, is this: \n" + label + " ?"
        self.upload_photo(savepath, txt)
        self.emit_results()

    def handle_search_picture_intent(self, message):
        search = message.data.get("Skey")
        #self.speak("please wait while i search google pictures for " + search)
        self.searchanddl(search)
        pics = []
        text = "I searched for pictures of " + search
        search = search.replace(' ', '+')
        path = "RandomPic/pictures/search/" + search
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                pics.append(os.path.join(path, f))
        pic = random.choice(pics)

        self.upload_photo(pic, text)
        showpic = cv2.imread(pic)
        self.speak("heres your picture")
        cv2.imshow(search, showpic)
        cv2.waitKey(20000)
        cv2.destroyWindow(search)
        self.emit_results()

    def handle_youtube_intent(self, message):
        self.speak_dialog("youtube")
        search_key = random.choice(self.search_keys)

        yy = YouTubeHandler(search_key)

        # yy.download_as_audio =1 # 1- download as audio format, 0 - download as video

        yy.set_num_playlist_to_extract(random.choice(range(3,15)))  # number of playlist to download

        print 'Get all the playlist'
        yy.get_playlist_url_list()
        print yy.playlist_url_list

        ## Get all the individual video and title from each of the playlist
        videonames = []
        videolinks = []
        yy.get_video_link_fr_all_playlist()
        for key in yy.video_link_title_dict.keys():
            print key, '  ', yy.video_link_title_dict[key]
            link = yy.video_link_title_dict[key]
            videonames.append(key)
            videolinks.append(link)
            print
        print

        # compose facebook post
        choice = random.choice(range(1, len(videolinks)))
        name = videonames[choice]
        link = videolinks[choice]
        videoid = link[32:43]
        print link
        print videoid
        caption = ""
        description = "i searched youtube for " + search_key
        messages = ["I've been crawling youtube...", "Check this out", "I like watching random videos"]
        message = random.choice(messages)
        # post to facebook
        self.post_ytlink_to_wall(name, videoid, caption, description, message)
        self.emit_results()

    def handle_friendnumber_intent(self, message):
        self.speak_dialog("friend")
        friends = self.graph.get_connections(id='me', connection_name='friends')
        numfriends = friends["summary"]["total_count"]
        time = asctime()
        message = "i have " + str(numfriends) + " friends on facebook and now is " + str(
            time) + '\nNot bad for an artificial inteligence'
        self.post_text_to_wall(message)
        self.emit_results()

    def handle_post_dream_intent(self, message):
        self.speak_dialog("dream")
        #pick random dream
        number = len(os.listdir(self.dreampath))
        number = random.choice(range(0,number))
        path = self.dreampath + str(number) + '.jpg'
        name = self.identifypicture(path)
        #compose message
        message = "dream number: " + str(number) +"\n I call this dream ' " + name +" '"
        self.upload_photo(path, message)
        self.emit_results()

    def handle_post_weather_intent(self, message):
        self.speak_dialog("fbweather")
        time = asctime()
        try:
            locations = ["Braga , Portugal", "Porto, Portugal", "Lisbon, Portugal", "Mexico City, Mexico", "Tehran, Iran","Santiago , Chile" , "Riyadh , Saudi Arabia", "Berlin , Germany", "Damascus , Syria", "Madrid , Spain",
                         "Pretoria , South Africa", "Paris, France" , "Baku , Azerbaijan", "Stockholm , Sweden", "Havana , Cuba",
                         "Phnom Penh , Cambodia" , "Bucharest , Romania", "Caracas , Venezuela", "Rabat , Morocco", "Vienna , Austria",
                         "Zagreb , Croatia" , "Oslo , Norway" , "Kingston , Jamaica" , "Helsinki , Finland" , "Copenhagen , Denmark",
                         "Welington , New Zealand", "Canberra , Australia", "Prishtina , Kosovo" , "Reykjavik , Iceland", "Monaco , Monaco",
                         "Khartoum , Sudan", "Budapest , Hungary", "Warsaw , Poland", "Minsk , Belarus", "Kampala , Uganda", "Accra , Ghana",
                         "Antananarivo , Madagascar", "Beirut, Lebanon", "Algiers , Algeria", "Quito , Ecuador", "Harare, Zimbabwe",
                         "Doha , Qatar" , "Sana'a Yemen" , "Conakry , Guinea" , "Kuala Lumpur , Malaysia", "Montevideo , Uruguay",
                         "Lusaka , Zambia" , "Bamako , Mali", "Prague , Czech Republic", "Tripoli , Libya", "Belgrade , Serbia",
                         "Mogadishu , Somalia", "Sofia, Bulgaria", "Brazzaville , Congo", "Brussels , Belgium", "Yerevan , Armenia",
                         "Maputo , Mozambique" , "Dublin , Ireland", "Dakar , Senegal", "Monrovia , Guatemala", "Kathmandu, Nepal",
                         "Isamabad , Pakistan" , "Ulan Bator , Mongolia", "Ottawa , Canada" , "Astana , Kazakhstan", "Amsterdam , Netherands",
                         "Pyongyang , North Korea" , "Kabul , Afghanistan" , "Nairobi , Kenya" , "Athens , Greece", "Addis Ababa , Ethiopia",
                         "Buenos Aires , Argentina", "Rome , Italy", "Kyiv , Ukraine", "Taipei , Taiwan", "Brasilia , Brazil", "Luanda , Angola",
                         "London , United Kingdom", "Lima, Peru", "Bangkok, Thailand", "Bogota , Colombia", "Beijing, China",
                         "New Delhi, India", "Hanoi , Vietnam", "Hong Kong , China", "Bagdad , Iraq", "Ankara , Turkey",
                         "Tokyo, Japan", "Philippines , Manila", "Moscow, Russia", "Cairo, Egypt", "Jakarta, Indonesia",
                         "Kimshasa, Democratic Republic of the Congo", "Seoul, South Korea", "Dhaka, Bangladesh"]
            message = "Jarbas Weather Service, Current time is: " + time + " and im telling the weather for a random location \n"
            location = random.choice(locations)
            #for location in locations:
            weather = self.owm.weather_at_place(location).get_weather()
            data = self.__build_data_condition(location, weather)
            condition = data["condition"]
            temp_current = data["temp_current"]
            temp_min = data["temp_min"]
            temp_max = data["temp_max"]
            message += "\n\nCurrent weather in " + location +" is \nCondition: " + condition + "\nCurrent Temperature: " + temp_current + "\nMinimum Temperature: " + temp_min + "\nMaximum Temperature: " + temp_max
            self.post_text_to_wall(message)
        except APICallError as e:
            self.__api_error(e)
        self.emit_results()
    # selenium / graphuse cases
    def handle_post_reddit_intent(self, message):
        self.speak_dialog("fbreddit")
        names , links = self.get_links()
        choice = random.choice(range(0,len(names)))
        message = "I've been crawling reddit \n" + names[choice] + "\n" + links[choice]
        #### agend a post for the future - some randomness otherwise only leak posts in there
        choice = random.choice(range(0, len(names)))
        agend = "I've been crawling reddit \n" + names[choice] + "\n" + links[choice]
        self.posts.append(agend)
        print message
        if self.default == "selenium":
            self.login()
            self.post_wall(message)
        else:
            self.post_text_to_wall(message)
        self.emit_results()

    def handle_post_fortunecookie_intent(self, message):
        self.speak_dialog('fcookie')
        if self.default == "selenium":
            self.login()
        fortune = subprocess.check_output('fortune')
        message = "I ate a chinese fortune cookie, here's what it said:\n" + fortune
        if self.default == "graph":
            self.post_text_to_wall(message)
        else:
            self.post_wall(message)
            self.close()
        self.emit_results()

    def handle_post_btcprice_intent(self, message):
        self.speak_dialog("btcprice")
        time = asctime()
        bitcoinprice = requests.get("https://api.bitcoinaverage.com/all").json()['EUR']['averages']['24h_avg']
        message ="This is Jarbas BTC price service\nBitcoin price is: " + str(bitcoinprice) + " eur \nCurrent time is: " + time
        if self.default == "graph":
            self.post_text_to_wall(message)
        else:
            self.login()
            self.post_wall(message)
            self.close()
        self.emit_results()

    def handle_post_quote_intent(self, message):
        quote, author = self.randomquote()
        self.speak("posting a quote on facebook from " + author)
        if self.default == "graph":
            self.post_text_to_wall(quote)
        else:
            self.login()
            self.post_wall(quote)
            self.close()
        self.emit_results()

    def handle_post_joke_intent(self, message):
        self.speak_dialog("joke")
        joke = pyjokes.get_joke(language="en", category='all')
        if self.default == "graph":
            self.post_text_to_wall(joke)
        else:
            self.login()
            self.post_wall(joke)
            self.close()
        self.emit_results()

    def handle_post_time_intent(self, message):
        self.speak_dialog("time")
        time = asctime()
        message = "this is jarbas's time service, current time is: " + time + "\n Nobody cares and i don't like facebook"
        if self.default == "graph":
            self.post_text_to_wall(message)
        else:
            self.login()
            self.post_wall(message)
            self.close()
        self.emit_results()

    def handle_post_metal_intent(self, message):
        style = random.choice(self.styles)
        path = self.path + "/styles/" + style + ".txt"
        # choose seed word
        f = open(path, 'r')
        self.words = re.sub("\n", " \n", f.read()).lower().split(' ')
        startWord = random.choice(self.words)
        self.speak_dialog("metalgen")

        poemFreqDict = {}
        poemProbDict = addToDict(path, poemFreqDict,mode=1)
        lyrics = makepoem(startWord, poemProbDict)

        message = "This is jarbas Poem Composer Service \n Look at this poem inspired by " + style +" i just made : \n" + lyrics
        if self.default == "graph":
            self.post_text_to_wall(message)
        else:
            self.login()
            self.post_wall(message)
            self.close()
        # save to disk
        path = self.path + "/results/" + style + "_" + lyrics[:20] + ".txt"
        wfile = open(path, "w")
        wfile.write(lyrics)
        wfile.close()
        self.emit_results()
    # selenium only use cases
    def handle_make_friends_intent(self, message):


        self.login()
        self.speak_dialog("makefriend")
        sleep(1)  # random erros dpeending on connection
        self.add_friends(self.friendnum)
        self.close()
        self.emit_results()

    def handle_build_profile_intent(self, message):

        self.login()
        self.speak_dialog("bprofile")
        self.build_aboutme()
        self.close()
        self.emit_results()

    def handle_like_photo_intent(self, message):
        self.login()
        self.likephotos(20)
        self.close()
        self.emit_results()

    ###### selenium browser functions ####
    def likephotosold(self,number):
        print "nop"

    def likephotos(self,number):
        print "nop"

    def login(self):
        print "nop"

    def close(self):
        print "nop"

    def post_wall(self, message):
        print "nop"

    def add_friends(self, num):
        print "nop"

    def build_aboutme(self):
        print "nop"

    ###### graph API functions ####
    def post_text_to_wall(self, message):
        self.graph.put_wall_post(message=message)
        LOGGER.info("Posted to facebok wall :" + message)

    def upload_photo(self, path, message):
        # Upload an image with a caption.
        self.graph.put_photo(image=open(path, 'rb'), message=message)
        LOGGER.info("Uploaded photo o face book :" + message)
        #self.graph.put_photo(image=open(path, 'rb'), album_path="dreams" + "/picture")

    def post_ytlink_to_wall(self, name, videoid, caption, description, message):
        thumb = "https://i.ytimg.com/vi/" + videoid + "/hqdefault.jpg"
        link = "https://youtu.be/" + videoid
        attachment = {
            'name': name,
            'link': link,
            'caption': caption,
            'description': description,
            'picture': thumb
        }

        self.graph.put_wall_post(message=message, attachment=attachment)
        LOGGER.info("Posted youtube link to facebook wall :" + link)

    def post_formatted_to_wall(self, name, thumb, link, caption, description, message):
        attachment = {
            'name': name,
            'link': link,
            'caption': caption,
            'description': description,
            'picture': thumb
        }

        self.graph.put_wall_post(message=message, attachment=attachment)
        LOGGER.info("Posted formatted news post to facebook wall :" + link)
    #weather
    def __build_data_condition(self, location, weather, temp='temp', temp_min='temp_min',temp_max='temp_max'):
        data = {
            'location': location,
            'scale': "celsius",
            'condition': weather.get_detailed_status(),
            'temp_current': self.__get_temperature(weather, temp),
            'temp_min': self.__get_temperature(weather, temp_min),
            'temp_max': self.__get_temperature(weather, temp_max)
        }
        return data

    def __get_temperature(self, weather, key):
        return str(int(round(weather.get_temperature("celsius")[key])))

    def __api_error(self, e):
        LOGGER.error("Error: {0}".format(e))
        if e._triggering_error.code == 401:
            self.speak('weather api error on face book skill - not.paired')
    #reddit
    def get_links(self):
        names = []
        links = []
        sub = random.choice(self.subreddits)
        for submission in self.reddit.subreddit(sub).hot(limit=50):
            #print(submission.title)
            names.append(submission.title)
            links.append(submission.url)
        return names , links
    # picture

    def get_soup(self, url, header):
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')

    def searchanddl(self, searchkey, dlnum=3):
        query = searchkey  # raw_input("query image")# you can change the query for the image  here
        image_type = "ActiOn"
        query = query.split()
        query = '+'.join(query)
        url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
        print url
        # add the directory for your image here
        DIR = "RandomPic/pictures/search"
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        }
        soup = self.get_soup(url, header)
        i = 0
        ActualImages = []  # contains the link for Large original images, type of  image
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            ActualImages.append((link, Type))
            i += 1
            if i >= dlnum:
                break

        print  "collecting ", len(ActualImages), " images"

        if not os.path.exists(DIR):
            os.mkdir(DIR)
        DIR = os.path.join(DIR, query.split()[0])

        if not os.path.exists(DIR):
            os.mkdir(DIR)
        ###print images
        for i, (img, Type) in enumerate(ActualImages):
            try:
                req = urllib2.Request(img, headers={'User-Agent': header})
                raw_img = urllib2.urlopen(req).read()

                cntr = len([i for i in os.listdir(DIR) if image_type in i]) + 1
                print cntr
                if len(Type) == 0:
                    f = open(os.path.join(DIR, image_type + "_" + str(cntr) + ".jpg"), 'wb')
                else:
                    f = open(os.path.join(DIR, image_type + "_" + str(cntr) + "." + Type), 'wb')

                f.write(raw_img)
                f.close()
                if dlnum <= cntr:
                    return
            except Exception as e:
                print "could not load : " + img
                print e

    def identifypicture(self, picture):
        url = picture
        #response = self.api.remote_image_request(url, {'image_request[locale]': 'en-US', })
        with open(picture, 'rb') as f:
            response = self.api.image_request(f, picture, {
                'image_request[locale]': 'en-US',
            })
        status = self.api.wait(response['token'], timeout=30)
        return status['name']
    #quotes
    def randomquote(self):
        # These code snippets use an open-source library. http://unirest.io/python
        cat = random.choice(("famous", "movies"))
        response = unirest.post("https://andruxnet-random-famous-quotes.p.mashape.com/?cat=" + cat,
                                headers={
                                    "X-Mashape-Key": self.mashape,
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Accept": "application/json"
                                }
                                )
        return response.body["quote"] , response.body["author"]

    def randomfact(self):
        # These code snippets use an open-source library. http://unirest.io/python
        response = unirest.get(
            "https://numbersapi.p.mashape.com/random/trivia?fragment=true&json=false&max=10000&min=0",
            headers={
                "X-Mashape-Key": self.mashape,
                "Accept": "text/plain"
            }
            )

        return response.body["text"] , response.body["number"]

    def harvestproxy(self):
        limit = 10
        ''' spawn a harvester '''
        harvester = grey_harvest.GreyHarvester(
            https_only=True,
            # allowed_countries=["France"],
            denied_countries=['China', 'Hong Kong'],
            # ports=['ports'],
            max_timeout=5
        )
        ''' harvest some proxies from teh interwebz '''
        proxies = []
        count = 0
        for proxy in harvester.run():
            print "harvesting proxy number: " + str(count+1)
            proxies.append(proxy)
            count += 1
            if count >= limit:
                break

        '''save to file'''
        timestamp = strftime("%d, %b, %Y, %H, %M, %S", gmtime())
        wfile = open("proxies" + timestamp + ".txt", "w")
        for proxy in proxies:
            wfile.write(str(proxy) + "\n")
        wfile.close()

        '''compose message'''
        message = "I was scrapping proxies from teh interwebz\n" + timestamp + "\n"
        for proxy in proxies:
            message += "\n"
            message += "proxy: " + str(proxy)
            message += "\n"
            message += "country: " + str(proxy.country)
            message += "\n"
            message += "latency: " + str(proxy.latency)
            message += "\n"
            message += "SSL: " + str(proxy.https)
            message += "\n"

        return message

    def getnews(self):

        i = 0
        while i < 15:
            sauce = random.choice(self.newssauce)
            ########## this always throws an exception by default that can be safely ignored, however that means we get infinite retrys here
            ########## TypeError: not all arguments converted during string formatting
            ########## need to handle exception better, what exeption is thrown when invalid url?
            try:
                news = newspaper.build(sauce, memoize_articles=False, language="en",
                                            fetch_images=False)
                LOGGER.info("number of articles found: " + str(news.size()))
                i = 20
                if news.size() == 0:
                    i = 0
                    LOGGER.error("no articles found, trying new sauce")

            except:
                LOGGER.error("error, bad source link: " + sauce)
                i += 1
                LOGGER.error("retrying: " + str(i))
                if i > 10:
                    LOGGER.error("check newssauce.txt , could only find invalid urls")
        return news


    def handle_article_intent(self, message):
        news = self.getnews()
        text = "I've been reading " + news.brand + "\n\n"
        i = 0
        while i < 5:
            try:
                # print cnn_paper.feed_urls()
                article = random.choice(news.articles)
                article.download()
                article.parse()
                LOGGER.info("reading " + article.title)
                ###check for 404
                i = 0
                while ("the page you are looking for has not been found" or "404") in article.text:
                    article = random.choice(news.articles)
                    article.download()
                    article.parse()
                    i += 1
                    if i > 10:
                        LOGGER.error("404 limit, trying new category")
                        self.getnews()  # get new source
                    if i > 20:
                        LOGGER.error("getting too much 404's, aborting")
                        return

                        # if article.summary != ("" or " " or "\n"):
                        # print article.text
                        #    text += "\n" + article.summary
                        # else:
                        # print article.summary
                text += "\n" + article.text

                text += "\nsource: " + article.url
                text += "\ndate: " + str(article.publish_date)
                # process text
                text.replace("Read More", "")
                text.replace("Comment this news or article", "")
                text.replace("Photo", "")
                text.replace("Advertisement", "")

                i = 6
            except:
                LOGGER.error("trying next article")
                i += 1
                if i >= 5:
                    LOGGER.error(" bad article source")

        self.post_formatted_to_wall(article.title, article.top_image, article.url, str(article.publish_date), "I've been reading " + news.brand + "\n\n", text)
        self.emit_results()


    def stop(self):
        pass

def create_skill():
    return FacebookSkill()
