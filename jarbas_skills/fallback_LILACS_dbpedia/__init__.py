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


from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)

### imports for this LILACS fallback

import spotlight
import urlfetch
import json
from mycroft.skills.displayservice import DisplayService
from jarbas_utils.LILACS.LILACS_fallback import LILACSFallback


class LILACSdbpediaSkill(LILACSFallback):
    def __init__(self):
        super(LILACSdbpediaSkill, self).__init__(
            name="dbpedia")
        self.host = "http://model.dbpedia-spotlight.org/en/annotate"

    def start_up(self):
        ''' Use instead of initialize method '''
        self.display_service = DisplayService(self.emitter, self.name)

    def handle_fallback(self, message):
        ''' this is activated by LILACS core, should answer the question
        asked, LILACS parsed data is available in message data '''
        return False

    def handle_test_intent(self, message):
        ''' test this fallback intent  '''
        ### get subject for test and update context###
        node = message.data.get("TargetKeyword",
                                message.data.get("LastConcept", "god"))
        self.set_context("LastConcept", node)

        ### adquire result with internal method for testing ###
        result = self._adquire(node).get(self.name, {}).get("node_dict")
        if not result:
            self.speak("Could not get info about " + node + " from " +
                       self.name)
            return
        ## update node in memory ##
        self.update_node(node,
                         node_data=result.get("data", {}),
                         node_connections=result.get("connections", {}))

        ### speak results back ###
        result = result.get("data", {})
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
            metadata["picture"] = pics[0]
            self.display_service.display(pics, utterance=message.data.get[
                "utterance"])

        if result.get("abstract", "") != "":
            self.speak(result["abstract"], metadata=metadata)

        if len(result.get("related_subjects", [])):
            self.speak("related subjects according to dbpedia")
            for thing in result["related_subjects"]:
                self.speak(thing, metadata=metadata)

    def get_connections(self, subject):
        ''' implement getting a dict of parsed connections here '''
        node_cons = {"parents": {}, "cousins": {}, "synonims": []}
        # get knowledge about
        try:
            annotations = spotlight.annotate(self.host, subject)
            for annotation in annotations:
                # categorie of this <- linked nodes <- parsing for dbpedia search
                types = annotation["types"].split(",")
                for parent in types:
                    node_cons["parents"][parent] = 5
                url = annotation["URI"]
                page_info = self.scrap_resource_page(url)
                for node in page_info["related_subjects"]:
                    node_cons["cousins"][node] = 5
                for node in page_info["same_as"]:
                    node_cons["synonims"].append(node)
        except:
            self.log.error("Failed to retrieve connections from " + self.name)
        return node_cons

    def get_data(self, subject):
        ''' implement parsing of data here '''
        node_data = {}
        # get knowledge about
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
                node_data["url"] = url
                node["page_info"] = self.scrap_resource_page(url)
                for field in node["page_info"]:
                    node_data[field] = node["page_info"][field]
        except:
            self.log.error("Failed to retrieve data from " + self.name)
        return node_data

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
                    dbpedia["primary"].append(value)
            elif "wasDerivedFrom" in j:
                # usually wikipedia link at scrap date
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    dbpedia["derived_from"].append(value)
            elif "owl#sameAs" in j:
                # links to dbpedia in other languages
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    if "resource" in value:
                        dbpedia["same_as"].append(value)

        return dbpedia


def create_skill():
    return LILACSdbpediaSkill()
