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


from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

__author__ = 'jarbas'

logger = getLogger(__name__)

import spotlight
import urlfetch
import json
from adapt.intent import IntentBuilder
from mycroft.skills.displayservice import DisplayService


class LILACSDBpediaSkill(MycroftSkill):
    def __init__(self):
        super(LILACSDBpediaSkill, self).__init__(
            name="LILACS_DBpedia_Skill")
        self.host = "http://model.dbpedia-spotlight.org/en/annotate"

    def initialize(self):
        self.emitter.on("dbpedia.request", self.handle_ask_dbpedia)
        test_intent = IntentBuilder("TestdbpediaIntent") \
            .require("testd").require("TargetKeyword").build()
        self.register_intent(test_intent, self.handle_test_intent)
        self.display_service = DisplayService(self.emitter, self.name)

    def handle_test_intent(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node).get("dbpedia")
        if not result:
            self.speak("Could not get info about " + node + " from dbpedia")
            return
        metadata = {}
        url = result.get("url")
        result = result.get("page_info", {})
        external_links = result.get("external_links", [])
        pics = result.get("pictures", [])
        if url:
            metadata["url"] = url
        if len(external_links):
            metadata["external_links"] = external_links
        if len(pics):
            metadata["pictures"] = pics
            self.display_service.display(pics, utterance=message.data.get["utterance"])

        if result.get("abstract", "") != "":
            self.speak(result["abstract"])

        if len(result.get("related_subjects", [])):
            self.speak("related subjects according to dbpedia")
            for thing in result["related_subjects"]:
                self.speak(thing)

    def handle_ask_dbpedia(self, message):
        self.handle_update_message_context(message)
        node = message.data.get("TargetKeyword")
        self.set_context("TargetKeyword", node)
        result = self.adquire(node)
        #self.speak(str(result))
        self.emitter.emit(Message("dbpedia.result", result, self.message_context))

    def adquire(self, subject):
        logger.info('DBpediaKnowledge_Adquire')
        dict = {}
        if subject is None:
            logger.error("No subject to adquire knowledge about")
        else:

            node_data = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                annotations = spotlight.annotate(self.host, subject)
                for annotation in annotations:
                    node = {}
                    # how sure we are this is about this dbpedia entry
                    score = annotation["similarityScore"]
                    node["score"] = score
                    # entry we are talking about
                    subject = annotation["surfaceForm"]
                    node["subject"] = subject
                    # smaller is closer to be main topic of sentence
                    offset = annotation["offset"]
                    node["offset"] = offset
                    # categorie of this <- linked nodes <- parsing for dbpedia search
                    types = annotation["types"].split(",")
                    node["parents"] = types
                    # dbpedia link
                    url = annotation["URI"]
                    node["url"] = url
                    node["page_info"] = self.scrap_resource_page(url)
                    node_data[subject] = node

                # id info source
                dict["dbpedia"] = node_data
            except Exception as e:
                logger.error(
                    "Could not parse dbpedia for " + str(subject))
        return dict

    def scrap_resource_page(self, link):
        u = link.replace("http://dbpedia.org/resource/",
                         "http://dbpedia.org/data/") + ".json"
        data = urlfetch.fetch(url=u)
        json_data = json.loads(data.content)
        dbpedia = {}
        dbpedia["related_subjects"] = []
        dbpedia["picture"] = []
        dbpedia["external_links"] = []
        dbpedia["abstract"] = ""
        for j in json_data[link]:
            if "#seeAlso" in j:
                # complimentary nodes
                for entry in json_data[link][j]:
                    value = entry["value"].replace(
                        "http://dbpedia.org/resource/", "").replace("_",
                                                                    " ").encode(
                        "utf8")
                    if value not in dbpedia["related_subjects"]:
                        dbpedia["related_subjects"].append(value)
            elif "wikiPageExternalLink" in j:
                # links about this subject
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    dbpedia["external_links"].append(value)
            elif "subject" in j:
                # relevant nodes
                for entry in json_data[link][j]:
                    value = entry["value"].replace(
                        "http://dbpedia.org/resource/Category:", "").replace(
                        "_", " ").encode("utf8")
                    if value not in dbpedia["related_subjects"]:
                        dbpedia["related_subjects"].append(value)
            elif "abstract" in j:
                # english description
                dbpedia["abstract"] = \
                    [abstract['value'] for abstract in json_data[link][j] if
                     abstract['lang'] == 'en'][0].encode("utf8")
            elif "depiction" in j:
                # pictures
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    dbpedia["picture"].append(value)
            elif "isPrimaryTopicOf" in j:
                # usually original wikipedia link
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    # dbpedia["primary"].append(value)
            elif "wasDerivedFrom" in j:
                # usually wikipedia link at scrap date
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    # dbpedia["derived_from"].append(value)
            elif "owl#sameAs" in j:
                # links to dbpedia in other languages
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    if "resource" in value:
                        # dbpedia["same_as"].append(value)
                        pass

        return dbpedia


def create_skill():
    return LILACSDBpediaSkill()