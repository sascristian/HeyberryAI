#from __future__ import unicode_literals
from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

import urllib2
import thread
from itertools import cycle
import random
import os
import praw
import time


__author__ = 'jarbas'

logger = getLogger(__name__)

class WallpaperSkill(MycroftSkill):

    def __init__(self):
        super(WallpaperSkill, self).__init__(name="WallpaperSkill")

        self.desktop = "mate"
        self.add_result("desktop", self.desktop)
        self.command = self.processcommand(self.desktop)

        self.USERAGENT = "Jarbas Ai Wallpaper finder"
        self.SUBREDDIT = "wallpapers"#"ImaginaryBestOf"
        self.IMAGEFOLDERPATH = "/home/user/jarbas-core/mycroft/skills/dreamskill/this"

        if not os.path.exists(self.IMAGEFOLDERPATH):
            os.makedirs(self.IMAGEFOLDERPATH)

        self.MAXPOSTS = 25
        self.TIMEBETWEENIMAGES = 65
        self.FILETYPES = ('.jpg', '.jpeg', '.png')

        self.ID = self.apiconfig.get('RedditAPI')
        self.SECRET = self.apiconfig.get('RedditSecre')

        self.cycleflag = True
        self.r = praw.Reddit(client_id=self.ID,
                             client_secret=self.SECRET,
                             user_agent=self.USERAGENT)
        # populate on first run
        self.populate = False
        #def start_populate():
        if self.populate:
            self.removeFiles()
            self.download_images(self.findImages())

        def cyclethread():
            if self.cycleflag:
                for imagePath in cycle(self.list_images()):
                    os.system(self.command.format(save_location=imagePath))
                    self.add_result("wallpaper", imagePath)
                    self.emit_results()
                    time.sleep(self.TIMEBETWEENIMAGES)
            else:
                time.sleep(5)

        thread.start_new_thread(cyclethread, ())

    def initialize(self):
       # self.load_data_files(dirname(__file__))

        start_cycle_intent = IntentBuilder("CycleWallpaperIntent")\
            .require("startcycle").build()
        self.register_intent(start_cycle_intent,
                             self.handle_cicle_desktops_intent)

        stop_cycle_intent = IntentBuilder("StopCycleWallpaperIntent") \
            .require("stopcycle").build()
        self.register_intent(stop_cycle_intent,
                             self.handle_unset_cicle_desktops_intent)

        change_desktop_intent = IntentBuilder("ChangeWallpaperIntent") \
            .require("change").build()
        self.register_intent(change_desktop_intent,
                             self.handle_change_desktop_intent)

        download_wallpaper_intent = IntentBuilder("DLWallpaperIntent") \
            .require("downloadw").build()
        self.register_intent(download_wallpaper_intent,
                             self.handle_populate_folder_intent)

        purge_wallpaper_intent = IntentBuilder("DeleteWallpaperIntent") \
            .require("purgefolder").build()
        self.register_intent(purge_wallpaper_intent,
                             self.handle_empty_folder_intent)

    def handle_populate_folder_intent(self, message):
        ## add walpaper files to folder
        self.download_images(self.findImages())
        self.emit_results()

    def handle_empty_folder_intent(self, message):
        ## delete walpaper files to folder
        self.removeFiles()
        self.emit_results()

    def handle_cicle_desktops_intent(self, message):
        ## set flag for changing process
        self.cycleflag = True
        self.emit_results()

    def handle_unset_cicle_desktops_intent(self, message):
        ## unset flag for changing process
        self.cycleflag = False
        self.emit_results()

    def handle_change_desktop_intent(self, message):
        ## pick random file
        paths = []
        ## change wallpaper
        for imagePath in self.list_images():
            paths.append(imagePath)
        wallpaper = random.choice(paths)
        os.system(self.command.format(save_location=wallpaper))
        self.add_result("wallpaper",wallpaper)
        self.emit_results()

    #### helper
    def download_images(self, url_list):
        for idx, url in enumerate(url_list):
            ext = os.path.splitext(url)[1]
            local_name = "{:0>4}{}".format(idx, ext)
            local_path = os.path.join(self.IMAGEFOLDERPATH, local_name)
            try:
                req = urllib2.Request(url)
                raw_img = urllib2.urlopen(req).read()
                f = open(local_path, 'wb')
                f.write(raw_img)
                f.close()

            except:  # urllib.error.HTTPError as e:
                print "nop"
                pass

    def findImages(self):
        urls = []
        for submision in self.r.subreddit(self.SUBREDDIT).hot(limit=self.MAXPOSTS):
            sURL = submision.url
            sURL = sURL.rsplit("?", 1)[0]
            sTitle = submision.title
            if sURL.lower().endswith(self.FILETYPES):
                urls.append(sURL)
        return urls

    def list_images(self):
        for file in os.listdir(self.IMAGEFOLDERPATH):
            if file.endswith(self.FILETYPES):
                yield os.path.join(self.IMAGEFOLDERPATH, file)

    def removeFiles(self):
        for file in self.list_images():
            os.remove(file)

    def processcommand(self, desktop):
        if desktop == "kde":
            command = """
                           qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
                               var allDesktops = desktops();
                               print (allDesktops);
                               for (i=0;i<allDesktops.length;i++) {{
                                   d = allDesktops[i];
                                   d.wallpaperPlugin = "org.kde.image";
                                   d.currentConfigGroup = Array("Wallpaper",
                                                          "org.kde.image",
                                                          "General");
                                   d.writeConfig("Image", "file:///{save_location}")
                               }}
                           '
                       """
        elif desktop == "gnome":
            command = "gsettings set org.gnome.desktop.background picture-uri file://{save_location}"
        elif desktop == "lubuntu":
            command = "pcmanfm -w {save_location} --wallpaper-mode=fit"
        elif desktop == "mate":
            command = "gsettings set org.mate.background picture-filename {save_location}"
        else:  # to do, other environments
            print "Command not coded for " + desktop
            command = ""
        return command

    def stop(self):
        pass


def create_skill():
    return WallpaperSkill()
