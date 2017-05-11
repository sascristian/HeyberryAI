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

        self.desktop = "jwm"
        self.command = self.processcommand(self.desktop)

        self.USERAGENT = "Jarbas Ai Wallpaper finder"
        self.SUBREDDIT = "ImaginaryBestOf"
        self.IMAGEFOLDERPATH = dirname(__file__) + "/wallpapers"

        if not os.path.exists(self.IMAGEFOLDERPATH):
            os.makedirs(self.IMAGEFOLDERPATH)

        self.MAXPOSTS = 25
        self.TIMEBETWEENIMAGES = 100
        self.FILETYPES = ('.jpg', '.jpeg', '.png')

        try:
            self.ID = self.config_apis["RedditAPI"]
            self.SECRET = self.config_apis["RedditSecret"]
        except:
            self.ID = self.config["RedditAPI"]
            self.SECRET = self.config["RedditSecret"]

        self.cycleflag = False

        self.r = praw.Reddit(client_id=self.ID,
                             client_secret=self.SECRET,
                             user_agent=self.USERAGENT)
        # populate on first run
        self.populate = False
        if self.populate:
            self.removeFiles()
            self.download_images(self.findImages())

        def cyclethread():
            if self.cycleflag:
                for imagePath in cycle(self.list_images()):
                    os.system(self.command.format(save_location=imagePath))
                    time.sleep(self.TIMEBETWEENIMAGES)

        thread.start_new_thread(cyclethread, ())

    def initialize(self):
        self.load_data_files(dirname(__file__))

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

    def handle_empty_folder_intent(self, message):
        ## delete walpaper files to folder
        self.removeFiles()

    def handle_cicle_desktops_intent(self, message):
        ## set flag for changing process
        self.cycleflag = True

    def handle_unset_cicle_desktops_intent(self, message):
        ## unset flag for changing process
        self.cycleflag = False

    def handle_change_desktop_intent(self, message):
        ## pick random file
        paths = []
        ## change wallpaper
        for imagePath in self.list_images():
            paths.append(imagePath)
        os.system(self.command.format(save_location=random.choice(paths)))

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
        for submision in self.r.subreddit(self.SUBREDDIT).hot(limit=50):
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
        elif desktop in ["kde3", "trinity"]:
            # From http://ubuntuforums.org/archive/index.php/t-803417.html
            command = 'dcop kdesktop KBackgroundIface setWallpaper 0 "{save_location}" 6'
        elif desktop == "gnome":
            command = "gsettings set org.gnome.desktop.background picture-uri file://{save_location}"
        elif desktop == "lubuntu":
            command = "pcmanfm -w {save_location} --wallpaper-mode=fit"
        elif desktop == "mate":
            command = "gsettings set org.mate.background picture-filename {save_location}"
        elif desktop in ["fluxbox", "jwm", "openbox", "afterstep"]:
            # http://fluxbox-wiki.org/index.php/Howto_set_the_background
            # used fbsetbg on jwm too since I am too lazy to edit the XML configuration
            # now where fbsetbg does the job excellent anyway.
            # and I have not figured out how else it can be set on Openbox and AfterSTep
            # but fbsetbg works excellent here too.
            command = "fbsetbg {save_location}"
        elif desktop == "icewm":
            # command found at http://urukrama.wordpress.com/2007/12/05/desktop-backgrounds-in-window-managers/
            command = "icewmbg {save_location}"
        elif desktop == "blackbox":
            # command found at http://blackboxwm.sourceforge.net/BlackboxDocumentation/BlackboxBackground
            command = "bsetbg -full {save_location}"
        elif desktop == "lxde":
            command = "pcmanfm --set-wallpaper {save_location} --wallpaper-mode=scaled"
        elif desktop == "windowmaker":
            # From http://www.commandlinefu.com/commands/view/3857/set-wallpaper-on-windowmaker-in-one-line
            command = "wmsetbg -s -u {save_location}"
        else:  # to do, other environments
            print "Command not coded for " + desktop
            command = ""
        return command

    def stop(self):
        pass


def create_skill():
    return WallpaperSkill()
