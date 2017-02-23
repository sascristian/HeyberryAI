
from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import requests
import json
import os
import webbrowser
import bs4
from requests import get
from geopy.geocoders import Nominatim

__author__ = 'jarbas'

logger = getLogger(__name__)


class PhotoSkill(MycroftSkill):

    def __init__(self):
        super(PhotoSkill, self).__init__(name="PhotoSkill")
        self.wikimapia_key = self.config['wikimapia_key']
        self.geolocator = Nominatim()

        self.search_name = "Berlin, Germany" #default location

        location = self.geolocator.geocode(self.search_name)
        self.center_lat = location.latitude
        self.center_long = location.longitude

        self.radius = 2000

        self.lat_min = self.center_lat - self.radius
        self.lat_max = self.center_lat + self.radius
        self.long_min = self.center_long - self.radius
        self.long_max = self.center_long + self.radius

        self.savepath = dirname(__file__)
        self.limit = 50


    def initialize(self):
        self.load_data_files(dirname(__file__))

        prefixes = [
            'photo from',"photolocation","pf"]
        self.__register_prefixed_regex(prefixes, "(?P<Adress>.*)")


        photo_ip_intent = IntentBuilder("PhotoFromIPIntent")\
            .require("photoip").build()
        self.register_intent(photo_ip_intent,
                             self.handle_photo_from_ip_intent)

        photo_location_intent = IntentBuilder("PhotoFromLocationIntent") \
            .require("Adress").build()
        self.register_intent(photo_location_intent,
                             self.handle_photo_from_location_intent)

    def __register_prefixed_regex(self, prefixes, suffix_regex):
        for prefix in prefixes:
            self.register_regex(prefix + ' ' + suffix_regex)

    def handle_photo_from_ip_intent(self, message):

        #### location from ip #####

        ip = get("http://ip-api.com/line").text
        lines = ip.split("\n")
        if "success" in lines[0]:
            self.center_lat = float(lines[7])
            self.center_long = float(lines[8])
            self.search_name = lines[5]
        #print search_name
        else:
            self.speak( "couldnt get location from ip adress")


        self.speak("Searching photos from " + self.search_name)

        self.lat_min = self.center_lat - self.radius
        self.lat_max = self.center_lat + self.radius
        self.long_min = self.center_long - self.radius
        self.long_max = self.center_long + self.radius

        self.getphotos()

        self.add_result("photo_location", self.search_name)

        self.emit_results()

    def handle_photo_from_location_intent(self, message):

        #### location from location #####

        #self.search_name = "auschwitz, poland"
        if message.data.get("Adress") is not None and len(message.data.get("Adress"))>=2:
            self.search_name = message.data.get("Adress")
        else:
            self.speak("invalid search adress")

        self.speak("Searching photos from " + self.search_name)
        location = self.geolocator.geocode(self.search_name)
        self.center_lat = location.latitude
        self.center_long = location.longitude

        self.lat_min = self.center_lat - self.radius
        self.lat_max = self.center_lat + self.radius
        self.long_min = self.center_long - self.radius
        self.long_max = self.center_long + self.radius

        self.getphotos()

        self.add_result("photo_location", self.search_name)

        self.emit_results()

    def getphotos(self):
        full_list = []

        # grab Wikimapia photos
        photo_list = self.get_all_wikimapia_photos()
        full_list.extend(photo_list)

        # grab Panoramio photos
        photo_list = self.get_all_panoramio_pictures()
        if photo_list is not None:
            full_list.extend(photo_list)

        self.speak( " Total of %d pictures retrieved." % len(full_list))
        path = self.write_photo_list(full_list)
        if len(full_list):
            webbrowser.open(path)
        else:
            self.speak( "no pics found, consider contributing to wikimedia")
    #
    # Helper function to grab photos from Wikimapia results
    #
    def get_photos_from_result(self, search_results):
        photo_list = []

        for result in search_results['places']:

            # are there photos in this result?
            if len(result['photos']):

                for photo in result['photos']:
                    photo_record = {}
                    photo_record['latitude'] = result['polygon'][0]['y']
                    photo_record['longitude'] = result['polygon'][0]['x']
                    photo_record['photo_file_url'] = photo['big_url']

                    # now we parse out the HTML
                    link_html_object = bs4.BeautifulSoup(result['urlhtml'])
                    link_location = link_html_object.a['href']

                    photo_record['photo_link'] = link_location

                    photo_list.append(photo_record)

        return photo_list

    #
    # Function responsible for sending requests to Wikimapia API
    #
    def send_wikimapia_request(self, page):
        api_url = "http://api.wikimapia.org/?key=%s&function=place.search&q=&" % self.wikimapia_key
        api_url += "lat=%s&lon=%s&" % (self.center_lat, self.center_long)
        api_url += "page=%d&count=100&" % page
        api_url += "category=&categories_or=&categories_and=&distance=%s&" % self.radius
        api_url += "format=json&pack=&language=en"

        response = requests.get(api_url)

        if response.status_code == 200:
            search_results = json.loads(response.content)

            return search_results

        return None

    #
    # Grab all photos from a Wikimapia area
    #
    def get_all_wikimapia_photos(self):
        photo_list = []
        page = 1

        # send the intial request
        search_results = self.send_wikimapia_request(page)

        # if there was an error return nothing
        if search_results is None:
            print "[*] Error retrieving photos from Wikimapia"
            return

        # use our helper function to grab the photos
        photo_list.extend(self.get_photos_from_result(search_results))

        print "[*] Retrieved %d photos..." % (len(photo_list))

        # find the total number of pages
        total_pages = (int(search_results['found']) / 100) + 1

        # keep polling for new records
        while page <= total_pages:

            # increase our page count
            page += 1

            search_results = self.send_wikimapia_request(page)

            if search_results is not None:
                photo_list.extend(self.get_photos_from_result(search_results))

                print "[*] Retrieved %d photos...(Wikimapia)" % (len(photo_list))

            if len(photo_list)>= self.limit:
                print "more photos than allowed limit"
                return photo_list
        # return all of our photos
        return photo_list

    #
    # Function responsible for sending requests to Panoramio API
    #
    def send_panoramio_request(self, start, end):
        api_url = "http://www.panoramio.com/map/get_panoramas.php?set=full&"
        api_url += "from=%d&to=%d&" % (start, end)
        api_url += "minx=%s&miny=%s&maxx=%s&maxy=%s&" % (self.long_min, self.lat_min, self.long_max, self.lat_max)
        api_url += "size=medium&mapfilter=false"

        response = requests.get(api_url)

        if response.status_code == 200:
            # convert to a dictionary
            search_results = json.loads(response.content)

            return search_results

        # there was a problem
        return None

    #
    # Use the Panaramio API to get all pictures
    #
    def get_all_panoramio_pictures(self):
        photo_list = []
        search_start = 0

        # send the intial request
        search_results = self.send_panoramio_request(search_start, search_start + 50)

        # if there was an error return nothing
        if search_results is None:
            print "[*] Error retrieving photos from panoramio."
            return

        # add the current results to our list
        photo_list.extend(search_results['photos'])

        print "[*] Retrieved %d photos..." % (len(photo_list))

        # while there are more photos to retrieve
        while search_results['has_more'] is True:

            # we increase the search count by 50
            search_start += 50

            search_results = self.send_panoramio_request(search_start, search_start + 50)

            if search_results is not None:
                photo_list.extend(search_results['photos'])

                print "[*] Retrieved %d photos...(Panoramio)" % (len(photo_list))

        # return all of our photos
        return photo_list

    #
    # Write out the list of photos
    #
    def write_photo_list(self, photo_list):
        path = str(self.savepath)
        path += "/%s" % self.search_name
        if not os.path.exists(path):
            os.mkdir(path)
        path += "/%s.html" % ( self.search_name)
        fd = open(path, "wb")
        fd.write("<html><head></head><body>")

        # walk through the list of photos and add them to our log file
        for photo in photo_list:

            # we have created a custom link so use it
            if photo.has_key("photo_link"):
                fd.write("<a href='%s' target='_blank'><img src='%s' border='0'></a><br/>\r\n" %
                         (photo['photo_link'], photo['photo_file_url']))

            else:

                # no custom link so create a Google Maps link
                fd.write(
                    "<a target='_blank' href='https://maps.google.com/?q=%f,%f'><img src='%s' border='0'></a><br/>\r\n" %
                    (photo['latitude'], photo['longitude'], photo['photo_file_url']))

                # close the html file
        fd.write("</body></html>")
        fd.close()

        return path

    def stop(self):
        pass


def create_skill():
    return PhotoSkill()


