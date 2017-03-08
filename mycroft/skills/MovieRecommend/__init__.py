from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import requests
from lxml import html
import bs4
import random

__author__ = 'jarbas'

logger = getLogger(__name__)


class MovieSkill(MycroftSkill):

    def __init__(self):
        super(MovieSkill, self).__init__(name="MovieSkill")
        self.Movie = ""
        self.Synopsis = ""
        self.Director = ""
        self.Stars = ""
        self.link = "http://www.imdb.com/chart/top?ref_=ft_250"
        self.movielist = []

    def initialize(self):

        suggest_intent = IntentBuilder("SuggestMovieIntent") \
            .require("MovieRecomendKeyword").build()

        self.register_intent(suggest_intent,
                             self.handle_suggest_intent)
        ## TODO movie categories
        ## TODO movie by director
        ## TODO movie with actor

        self.get_movie_list()

    def handle_suggest_intent(self, message):

        if len(self.movielist)==0:
            self.get_movie_list()

        link = random.choice(self.movielist)
        self.parse_movie(link)

        self.speak_dialog("movie_recommend", {"movie":self.Movie})
        self.speak_dialog("director", {"director":self.Director})
        self.speak_dialog("stars", {"stars": self.Stars})
        self.speak_dialog("story", {"synopsis":self.Synopsis})

       # self.add_result("Movie_Name",self.Movie)
       # self.add_result("Movie_Director",self.Director)
       # self.add_result("Movie_Stars", self.Stars)
       # self.add_result("Movie_Synopsis", self.Synopsis)
       # self.add_result("IMDB_Link", link)
       # self.emit_results()

    def get_html(self, url):
        headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0"}
        r = requests.get(url, headers=headers)
        html = r.text.encode("utf8")
        return html

    def get_movie_list(self):
        html = self.get_html(self.link)
        soup = bs4.BeautifulSoup(html, "lxml")
        movies = soup.findAll('td', attrs={'class': "titleColumn"})
        for movie in movies:
            temp = movie.find('a')
            url = "http://www.imdb.com" + temp['href']
            self.movielist.append(url)
            print url

    def parse_movie(self, url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        name = tree.xpath(".//*[@id='title-overview-widget']/div[2]/div[2]/div/div[2]/div[2]/h1/text()")[0]
        try:
            director = tree.xpath(".//*[@id='title-overview-widget']/div[3]/div[1]/div[2]/span/a/span/text()")[0]
        except:  #
            director = tree.xpath(".//*[@id='title-overview-widget']/div[3]/div[2]/div[1]/div[2]/span/a/span/text()")[0]
        story = tree.xpath(".//*[@id='titleStoryLine']/div[1]/p/text()")[0]
        stars = \
        tree.xpath(".//*[@id='title-overview-widget']/div[2]/div[2]/div/div[1]/div[1]/div[1]/strong/span/text()")[0]
        self.Movie = name
        self.Director = director
        self.Synopsis = story
        self.Stars = stars

    def stop(self):
        pass


def create_skill():
    return MovieSkill()
