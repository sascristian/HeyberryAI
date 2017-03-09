from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import requests
from lxml import html
import bs4
import random
import webbrowser

__author__ = 'jarbas'

logger = getLogger(__name__)


class MovieSkill(MycroftSkill):

    def __init__(self):
        super(MovieSkill, self).__init__(name="MovieSkill")
        self.populate = True
        self.reload_skill = False
        # current movie info
        self.Movie = ""
        self.Synopsis = ""
        self.Director = ""
        self.Stars = ""
        self.Year = ""
        self.imdblink = ""
        # top 250 imdb movies
        self.link = "http://www.imdb.com/chart/top?ref_=ft_250"
        self.movielist = []  # links to top movies
        # movies genres
        self.genres = ["action", "adventure", "animation", "biography", "comedy", "crime","drama","family","fantasy",
                       "film_noir", "history", "horror", "music", "musical", "mystery", "romance", "sci_fi", "sport",
                       "thriller", "war", "western"]
        self.genreslink = "http://www.imdb.com/search/title?genres="
        self.genreslinkparams = "&sort=user_rating,desc&title_type=feature&num_votes=25000,&pf_rd_m=A2FGELUUNOQJNL"
        self.genre_movie_list={}# links to top 50 movies of each genre
        for genre in self.genres:
            self.genre_movie_list.setdefault(genre, [])
        # populate movie db
        if self.populate:
            self.get_movie_list()
            for genre in self.genres:
                self.get_genre_movie_list(genre)

    def initialize(self):

        suggest_intent = IntentBuilder("SuggestMovieIntent") \
            .require("MovieRecomendKeyword").build()

        self.register_intent(suggest_intent,
                             self.handle_suggest_intent)

        genre_suggest_intent = IntentBuilder("SuggestMovieGenreIntent") \
            .require("genre").build()

        self.register_intent(genre_suggest_intent,
                             self.handle_genre_suggest_intent)

        imdbpage_intent = IntentBuilder("IMDBMoviePageIntent") \
            .require("imdbKeyword").build()

        self.register_intent(imdbpage_intent,
                             self.handle_open_imdb_page_intent)

        ## TODO movie by director
        ## TODO movie with actor



    def handle_suggest_intent(self, message):

        if len(self.movielist)==0:
            self.get_movie_list()

        self.imdblink = random.choice(self.movielist)
        self.parse_movie(self.imdblink)

        self.speak_dialog("movie_recommend", {"movie":self.Movie})
        self.speak_dialog("director", {"director":self.Director})
        self.speak_dialog("year", {"year": self.Year})
        self.speak_dialog("stars", {"stars": self.Stars})
        self.speak_dialog("story", {"synopsis":self.Synopsis})

    def handle_genre_suggest_intent(self, message):

        genre = message.data["genre"]
        genre = genre.replace(" film", "")
        genre = genre.replace(" movie", "")
        genre = genre.replace(" ", "_")

        if len(self.genre_movie_list[genre])==0:
            if not self.get_genre_movie_list(genre):
                self.speak_dialog("invalidgenre")
                return

        self.imdblink = random.choice(self.genre_movie_list[genre])

        self.parse_movie(self.imdblink)

        self.speak_dialog("movie_recommend", {"movie":self.Movie})
        self.speak_dialog("director", {"director":self.Director})
        self.speak_dialog("year", {"year": self.Year})
        self.speak_dialog("stars", {"stars": self.Stars})
        self.speak_dialog("story", {"synopsis":self.Synopsis})


    def handle_open_imdb_page_intent(self, message):
        ### TODO check for movie keyword and search instead of only showing recommended movie
        if self.link == "":
            self.speak_dialog("imdbpage_error")
        else:
            self.speak_dialog("imdbpage",{"movie":self.Movie})
            webbrowser.open(self.imdblink)

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

    def get_genre_movie_list(self, genre):
        genre.replace(" ","_")
        #build movie link
        if genre in self.genres:
            # build genre search link
            link = self.genreslink+genre+self.genreslinkparams
            html = self.get_html(link)
            # find movie links
            soup = bs4.BeautifulSoup(html, "lxml")
            movies = soup.findAll('h3')
            for movie in movies:
                temp = movie.find('a')
                try:
                    url = "http://www.imdb.com" + temp['href']
                    if "http://www.imdb.com/title/" in url:  # url is of movie
                        self.genre_movie_list[genre].append(url) #add to link list
                except:
                    pass
            return True
        else:
            return False

    def parse_movie(self, movie_link):
        response = requests.get(movie_link)
        tree = html.fromstring(response.content)
        name = tree.xpath(".//*[@id='title-overview-widget']/div[2]/div[2]/div/div[2]/div[2]/h1/text()")[0]
        try:
            director = tree.xpath(".//*[@id='title-overview-widget']/div[3]/div[1]/div[2]/span/a/span/text()")[0]
        except:  #
            director = tree.xpath(".//*[@id='title-overview-widget']/div[3]/div[2]/div[1]/div[2]/span/a/span/text()")[0]
        story = tree.xpath(".//*[@id='titleStoryLine']/div[1]/p/text()")[0]
        stars = tree.xpath(".//*[@id='title-overview-widget']/div[2]/div[2]/div/div[1]/div[1]/div[1]/strong/span/text()")[0]
        year = tree.xpath(".//*[@id='titleYear']/a/text()")[0]
        self.Movie = name
        self.Director = director
        self.Synopsis = story
        self.Stars = stars
        self.Year = year

    def stop(self):
        pass


def create_skill():
    return MovieSkill()
