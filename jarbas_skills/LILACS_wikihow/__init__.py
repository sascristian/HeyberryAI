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
from mycroft.skills.displayservice import DisplayService

import bs4
import requests

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACSWikiHowSkill(MycroftSkill):
    def __init__(self):
        super(LILACSWikiHowSkill, self).__init__(
            name="LILACS_Wikihow_Skill")

    def initialize(self):
        self.emitter.on("wikihow.request", self.handle_ask_wikihow)
        test_intent = IntentBuilder("TestWikihowIntent") \
            .require("testh").require("TargetKeyword").build()
        self.register_intent(test_intent, self.handle_test_intent)
        self.display_service = DisplayService(self.emitter, self.name)

    def handle_test_intent(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node).get("wikihow")
        if not result:
            self.speak("Could not get info about " + node + " from wikihow")
            return
        self.speak("found " + str(len(result)) + " how tos in wikihow")
        how_tos = result.keys()
        how_to = how_tos[0]
        data = result[how_to]
        if len(data.get("pics", [])):
            self.display_service.display(data["pics"])
        if "url" in data.keys():
            metadata = {"url": data["url"]}
        else:
            metadata = {}
        self.speak(how_to, metadata=metadata)
        steps = data.get("steps", [])
        i = 0
        for step in steps:
            text = "step " + str(i) + ". " + step
            i += 1
            self.speak(text)
        self.speak("detailed steps are also available")

    def handle_ask_wikihow(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node)
        #self.speak(str(result))
        self.emitter.emit(Message("wikihow.result", result, self.message_context))

    def adquire(self, subject):
        logger.info('WikihowKnowledge_Adquire')
        dict = {}
        if subject is None:
            logger.error("No subject to adquire knowledge about")
        else:
            # get knowledge about
            # TODO exceptions for erros
            try:
                how_to = self.how_to(subject)
                dict["wikihow"] = how_to
            except Exception as e:
                logger.error(
                    "Could not parse wikihow for " + str(subject))
        return dict

    def search_wikihow(self, search_term):
        # print "Seaching wikihow for " + search_term
        search_url = "http://www.wikihow.com/wikiHowTo?search="
        search_term_query = search_term.replace(" ", "+")
        search_url += search_term_query
        # print search_url
        # open url
        html = self.get_html(search_url)
        soup = bs4.BeautifulSoup(html, "lxml")
        # parse for links
        list = []
        links = soup.findAll('a', attrs={'class': "result_link"})
        for link in links:
            url = "http:" + link.get('href')
            list.append(url)
        return list

    def get_html(self, url):
        headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0"}
        r = requests.get(url, headers=headers)
        html = r.text.encode("utf8")
        return html

    def get_steps(self, url):
        # open url
        html = self.get_html(url)
        soup = bs4.BeautifulSoup(html, "lxml")
        # get title
        title_html = soup.findAll("h1", {"class": "firstHeading"})
        for html in title_html:
            url = "http:" + html.find("a").get("href")
        title = url.replace("http://www.wikihow.com/", "").replace("-", " ")
        # get steps
        steps = []
        ex_steps = []
        step_html = soup.findAll("div", {"class": "step"})
        for html in step_html:
            step = html.find("b")
            step = step.text

            trash = str(html.find("script"))
            trash = trash.replace("<script>", "").replace("</script>", "").replace(";", "")
            ex_step = html.text.replace(trash, "")

            trash_i = ex_step.find("//<![CDATA[")
            trash_e = ex_step.find(">")
            trash = ex_step[trash_i:trash_e + 1]
            ex_step = ex_step.replace(trash, "")

            trash_i = ex_step.find("http://")
            trash_e = ex_step.find(".mp4")
            trash = ex_step[trash_i:trash_e + 4]
            ex_step = ex_step.replace(trash, "")

            trash = "WH.performance.mark('step1_rendered');"
            ex_step = ex_step.replace(trash, "")
            ex_step = ex_step.replace("\n", "")

            steps.append(step)
            ex_steps.append(ex_step)

        # get step pic
        pic_links = []
        pic_html = soup.findAll("a", {"class": "image lightbox"})
        for html in pic_html:
            html = html.find("img")
            i = str(html).find("data-src=")
            pic = str(html)[i:].replace('data-src="', "")
            i = pic.find('"')
            pic = pic[:i]
            pic_links.append(pic)

        return title, steps, ex_steps, pic_links, url

    def how_to(self, subject):
        how_tos = {}
        links = self.search_wikihow(subject)
        if links == []:
            print "No wikihow results"
            return
        for link in links:
            try:
                how_to = {}
                # get steps and pics
                title, steps, descript, pics, link = self.get_steps(link)
                how_to["title"] = title
                how_to["steps"] = steps
                how_to["detailed"] = descript
                how_to["pics"] = pics
                how_to["url"] = link
                how_tos[title] = how_to
            except:
                print "error, skipping link " + link
        return how_tos

    def random_how_to(self):
        link = "http://www.wikihow.com/Special:Randomizer"
        # get steps and pics
        title, steps, descript, pics, link = self.get_steps(link)
        how_to = {}
        how_to["title"] = title
        how_to["steps"] = steps
        how_to["detailed"] = descript
        how_to["pics"] = pics
        how_to["url"] = link
        return how_to


def create_skill():
    return LILACSWikiHowSkill()