
import urllib2
import cv2
import numpy as np
import os
import time
import random
import json
from bs4 import BeautifulSoup
from PIL import Image
import imutils
import sys
from os.path import dirname
from time import sleep
sys.path.append(dirname(dirname(__file__)))
from service_display.displayservice import DisplayService
sys.path.append(dirname(__file__))
from util.randomart import makeImage
from util.geopatterns import GeoPattern

import cairosvg

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)
dreamlogger = getLogger('Dream ')

class DreamSkill(MycroftSkill):
	def __init__(self):
		super(DreamSkill, self).__init__(name="DreamSkill")
		self.reload_skill = False
		caffepath = self.config["caffe_path"]

		sys.path.append(caffepath)
		from batcountry import BatCountry

		path = os.path.dirname(__file__)
		self.model = "bvlc_googlenet"
		path += '/caffe/models/' + self.model

		# start batcountry instance (self, base_path, deploy_path=None, model_path=None,
		self.bc = BatCountry(path)#path,model_path=path)
		#if model == "bvlc_googlenet":
		self.iter = self.config["iter"] #dreaming iterations
		self.layers = [ "inception_5b/output", "inception_5b/pool_proj",
						"inception_5b/pool", "inception_5b/5x5",
						"inception_5b/5x5_reduce", "inception_5b/3x3",
						"inception_5b/3x3_reduce", "inception_5b/1x1",
						"inception_5a/output", "inception_5a/pool_proj",
						"inception_5a/pool", "inception_5a/5x5",
						"inception_5a/5x5_reduce", "inception_5a/3x3",
						"inception_5a/3x3_reduce", "inception_5a/1x1",
						"pool4/3x3_s2", "inception_4e/output", "inception_4e/pool_proj",
						"inception_4e/pool", "inception_4e/5x5",
						"inception_4e/5x5_reduce", "inception_4e/3x3",
						"inception_4e/3x3_reduce", "inception_4e/1x1",
						"inception_4d/output", "inception_4d/pool_proj",
						"inception_4d/pool", "inception_4d/5x5",
						"inception_4d/5x5_reduce", "inception_4d/3x3",
						"inception_4d/3x3_reduce", "inception_4d/1x1",
						"inception_4c/output", "inception_4c/pool_proj",
						"inception_4c/pool", "inception_4c/5x5",
						"inception_4c/5x5_reduce", "inception_4c/3x3",
						"inception_4c/3x3_reduce", "inception_4c/1x1",
						"inception_4b/output", "inception_4b/pool_proj",
						"inception_4b/pool", "inception_4b/5x5",
						"inception_4b/5x5_reduce", "inception_4b/3x3",
						"inception_4b/3x3_reduce", "inception_4b/1x1",
						"inception_4a/output", "inception_4a/pool_proj",
						"inception_4a/pool", "inception_4a/5x5",
						"inception_4a/5x5_reduce", "inception_4a/3x3",
						"inception_4a/3x3_reduce", "inception_4a/1x1",
						"inception_3b/output", "inception_3b/pool_proj",
						"inception_3b/pool", "inception_3b/5x5",
						"inception_3b/5x5_reduce", "inception_3b/3x3",
						"inception_3b/3x3_reduce", "inception_3b/1x1",
						"inception_3a/output", "inception_3a/pool_proj",
						"inception_3a/pool", "inception_3a/5x5",
						"inception_3a/5x5_reduce", "inception_3a/3x3",
						"inception_3a/3x3_reduce", "inception_3a/1x1",
						"pool2/3x3_s2","conv2/norm2","conv2/3x3",
						"conv2/3x3_reduce", "pool1/norm1"] #"pool1/3x3_s2" , "conv17x7_s2"

		# random dreaming mode choice
		self.choice = 0#self.config["mode"]  # guided dream=1 normal = 0

		# Define the codec and create VideoWriter object
		# self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
		# self.out = cv2.VideoWriter("dream_output/output.avi",self.fourcc, 20.0, (200,200))
		# self.out = cv2.VideoWriter("dream_output/dream.avi", fourcc, 20.0, (640, 480))

		# make working directories
		self.sourcespath = os.path.dirname(__file__) + '/sources.txt'
		self.searchpath = self.config_core["database_path"] + "/pictures/search"
		self.sourcedir = self.config_core["database_path"] + "/pictures/random"
		self.outputdir = self.config_core["database_path"] + "/dreams"
		self.sharedfolder = self.config_core["database_path"] + "/pictures/this"
		self.camfolder = self.config_core["database_path"] + "/pictures/cam"
		self.patternpath = self.config_core["database_path"] + "/pictures/patterns"
		self.psypath = self.config_core["database_path"] + "/pictures/psy"
		# check if folders exist
		if not os.path.exists(self.sourcedir):
			os.makedirs(self.sourcedir)
		if not os.path.exists(self.outputdir):
			os.makedirs(self.outputdir)
		if not os.path.exists(self.outputdir+"/about"):
			os.makedirs(self.outputdir+"/about")
		if not os.path.exists(self.outputdir+"/this"):
			os.makedirs(self.outputdir+"/this")
		if not os.path.exists(self.outputdir+"/psy"):
			os.makedirs(self.outputdir+"/psy")
		if not os.path.exists(self.outputdir+"/pure"):
			os.makedirs(self.outputdir+"/pure")
		if not os.path.exists(self.outputdir+"/random"):
			os.makedirs(self.outputdir+"/random")
		if not os.path.exists(self.outputdir+"/recursive"):
			os.makedirs(self.outputdir+"/recursive")
		if not os.path.exists(self.outputdir+"/webcam"):
			os.makedirs(self.outputdir+"/webcam")
		if not os.path.exists(self.searchpath):
			os.makedirs(self.searchpath)
		if not os.path.exists(self.sharedfolder):
			os.makedirs(self.sharedfolder)
		if not os.path.exists(self.camfolder):
			os.makedirs(self.camfolder)
		if not os.path.exists(self.patternpath):
			os.makedirs(self.patternpath)
		if not os.path.exists(self.psypath):
			os.makedirs(self.psypath)
		###imagine dimensions
		self.w = 640
		self.h = 480

		### flag to avoid dreaming multiple times at once (computer crash guaranteed)
		self.dreaming = False

		### entropy to form patterns from
		# initially populate with noise from file
		self.strings = []
		path = os.path.dirname(__file__) + '/noise.txt'
		with open(path) as f:
			noise = f.readlines()
		for line in noise:
			for word in line.split("\n"):
				if word is not None:
					self.strings.append(word)

	def initialize(self):

		prefixes = [
			'dream about', 'dream with', 'dream of', 'dream off', 'da']
		self.__register_prefixed_regex(prefixes, "(?P<DreamSearch>.*)")

		psy_dream_intent = IntentBuilder("PsyDreamIntent") \
			.require("psydream").build()
		self.register_intent(psy_dream_intent,
							 self.handle_psy_dream_intent)

		pure_dream_intent = IntentBuilder("PureDreamIntent") \
			.require("puredream").build()
		self.register_intent(pure_dream_intent,
							 self.handle_pure_dream_intent)

		dream_about_intent = IntentBuilder("DreamAboutIntent") \
			.require("DreamSearch").build()
		self.register_intent(dream_about_intent,
							 self.handle_dream_about_intent)

		dream_about_webcam_intent = IntentBuilder("WebcamDreamingIntent") \
			.require("camdream").build()
		self.register_intent(dream_about_webcam_intent,
							 self.handle_dream_about_webcam_intent)

		dream_about_this_intent = IntentBuilder("TargetedDreamingIntent") \
			.require("this").build()
		self.register_intent(dream_about_this_intent,
							 self.handle_dream_about_this_intent)

		dream_about_dreams_intent = IntentBuilder("DreamAboutDreamsIntent") \
			.require("Dreamdreams").build()
		self.register_intent(dream_about_dreams_intent,
							 self.handle_dream_about_dreams_intent)

		dream_intent = IntentBuilder("DreamIntent")\
			.require("dream").build()
		self.register_intent(dream_intent,
							 self.handle_dream_intent)

		show_dream_intent = IntentBuilder("ShowDreamIntent")\
			.require("showdream").build()
		self.register_intent(show_dream_intent,
							 self.handle_show_dream_intent)

		self.screen_service = DisplayService(self.emitter)

	def __register_prefixed_regex(self, prefixes, suffix_regex):
		for prefix in prefixes:
			self.register_regex(prefix + ' ' + suffix_regex)

	#### intent handling ####
	def handle_show_dream_intent(self, message):
		dreams = []
		for f in os.listdir(self.outputdir):
			if os.path.isfile(os.path.join(self.outputdir, f)):
				dreams.append(os.path.join(self.outputdir, f))
		dream = random.choice(dreams)

		self.speak("look at this dream i had")
		self.screen_service.show(dream, message.data["utterance"])

	def handle_psy_dream_intent(self, message):
		if not self.dreaming:
			makeImage(self.psypath, 3)

		chosenpic = random.choice(os.listdir(self.psypath))
		imagepah = self.psypath+"/" + str(chosenpic)
		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.psypath))
			guidepah =self.psypath + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah)
		else:
			result = self.dream(imagepah)

		if result is not None:
			name = time.asctime()
			save_path = self.outputdir + "/dream/psy/" + name + ".jpg"
			cv2.imwrite(save_path, result)
			self.speak("Here is what i dreamed")
			self.screen_service.show(save_path, message.data["utterance"])

	def handle_pure_dream_intent(self, message):

		if not self.dreaming:
			self.generate_pattern(random.choice(self.strings))

		chosenpic = random.choice(os.listdir(self.patternpath))
		imagepah = self.patternpath+"/" + str(chosenpic)

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.patternpath))
			guidepah =self.patternpath + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah)
		else:
			result = self.dream(imagepah)

		if result is not None:
			name = time.asctime()
			save_path = self.outputdir + "/pure/" + name + ".jpg"
			cv2.imwrite(save_path, result)
			self.speak("Here is what i dreamed")
			self.screen_service.show(save_path, message.data["utterance"])

	def handle_dream_intent(self, message):
		if not self.dreaming:
			self.collectentropy()

		chosenpic = random.choice(os.listdir(self.sourcedir))
		imagepah = self.sourcedir+"/" + str(chosenpic)

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.sourcedir))
			guidepah =self.sourcedir + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah)
		else:
			result = self.dream(imagepah)

		if result is not None:
			name = time.asctime()
			save_path = self.outputdir + "/dream/random/" + name + ".jpg"
			cv2.imwrite(save_path, result)
			self.speak("Here is what i dreamed")
			self.screen_service.show(save_path, message.data["utterance"])

	def handle_dream_about_webcam_intent(self, message):

		if not self.dreaming:
			cap = cv2.VideoCapture(0)
			ret, frame = cap.read()
			cv2.imwrite(self.camfolder + "/feed.jpg", frame)
			sleep(1)
			ret, frame = cap.read()
			cv2.imwrite(self.camfolder + "/feed2.jpg", frame)
			cap.release()

		imagepah = self.camfolder + "/feed.jpg"

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.camfolder))
			guidepah =self.camfolder + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah)
		else:
			result = self.dream(imagepah)

		if result is not None:
			name = time.asctime()
			save_path = self.outputdir + "/webcam/" + name + ".jpg"
			cv2.imwrite(save_path, result)
			self.speak("Here is what i dreamed")
			self.screen_service.show(save_path, message.data["utterance"])

	def handle_dream_about_dreams_intent(self, message):

		chosenpic = random.choice(os.listdir(self.outputdir))
		if chosenpic is None:
			self.speak("no source picture")
			return
		imagepah = self.outputdir + "/" + str(chosenpic)

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.outputdir))
			guidepah = self.outputdir + "/" + str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah)
		else:
			result = self.dream(imagepah)

		if result is not None:
			name = time.asctime()
			save_path = self.outputdir + "/recursive/" + name + ".jpg"
			cv2.imwrite(save_path, result)
			self.speak("Here is what i dreamed")
			self.screen_service.show(save_path, message.data["utterance"])

	def handle_dream_about_this_intent(self, message):
		chosenpic = random.choice(os.listdir(self.sharedfolder))

		if chosenpic is None:
			self.speak("no source picture")
			return

		imagepah = self.sharedfolder+"/" + str(chosenpic)

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.sharedfolder))
			guidepah =self.sharedfolder + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah)
		else:
			result = self.dream(imagepah)

		if result is not None:
			name = time.asctime()
			save_path = self.outputdir + "/this/" + name + ".jpg"
			cv2.imwrite(save_path, result)
			self.speak("Here is what i dreamed")
			self.screen_service.show(save_path, message.data["utterance"])

	def handle_dream_about_intent(self, message):
		imagepath = ""
		search = message.data.get("DreamSearch")
		if not self.dreaming:
			# collect dream entropy
			pics = self.search_image(search)
			imagepah = random.choice(pics)

		# choose dream mode
		if self.choice != 0:
			# guided dream experiments
			result = self.guided_dream(imagepah, random.choice(pics))
		else:
			result = self.dream(imagepah)

		if result is not None:
			name = search + "_" + time.asctime()
			save_path = self.outputdir + "/about/" + name + ".jpg"
			cv2.imwrite(save_path, result)
			self.speak("Here is what i dreamed")
			self.screen_service.show(save_path, message.data["utterance"])

	def stop(self):
		cv2.destroyAllWindows()
		self.bc.cleanup()

	##### image / entropy collection functions ####

	def generate_pattern(self, string):
		generators = ["hexagons", "overlapping_circles", "overlapping_rings", "plaid", "plus_signs", "rings",
					  "sinewaves", "squares", "xes"]
		i=0
		while i<8:
			try:
				pattern = GeoPattern(string, random.choice(generators))
				svg = pattern.svg_string
				savepath = self.patternpath + "/" + str(i) + ".png"
				fout = open(savepath, "wb")
				cairosvg.svg2png(bytestring=svg, write_to=fout)
				fout.close()
				pic = cv2.imread(savepath)
				pic = imutils.resize(pic, self.w, self.h)
				pic = self.filterdream(random.choice(range(0,13)),pic) #randomly filter or not the generated pattern, since its ugly in final dreams i can use it for something else
				cv2.imwrite(savepath, pic)
			except:
				pass
			i += 1

	def collectentropy(self):
		# collect dream entropy
		self.store_raw_images(3)

	def countdreams(self, dir = None):
		if dir is None:
			dir = self.outputdir
		i = 1
		for f in os.listdir(dir):
			if os.path.isfile(os.path.join(dir, f)):
				i += 1
		return i

	def store_raw_images(self, number=1):

		with open(self.sourcespath) as f:
			urls = f.readlines()
		i = 0
		while i < number:
			try:
				image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
				chosenurl = random.choice(image_urls.split('\n'))
				print(chosenurl)

				img = urllib2.Request(chosenurl)
				raw_img = urllib2.urlopen(img).read()
				save_path = self.sourcedir+"/" + time.asctime() + ".jpg"
				f = open(save_path, 'wb')
				f.write(raw_img)
				f.close()
				i += 1

			except Exception as e:
				print(str(e))

	def search_image(self, search):
		self.speak("dreaming about " + search)
		self.searchanddl(search)
		pics = []
		search = search.replace(' ', '+')
		path = self.searchpath + "/" + search
		for f in os.listdir(path):
			if os.path.isfile(os.path.join(path, f)):
				pics.append(os.path.join(path, f))
		return pics

	def get_soup(self, url, header):
		return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')

	def searchanddl(self, searchkey, dlnum=5):
		query = searchkey  # raw_input("query image")# you can change the query for the image  here
		image_type = "ActiOn"
		query = query.split()
		query = '+'.join(query)
		url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
		print url
		# add the directory for your image here
		DIR = self.searchpath
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
				#print cntr
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

	#### dreaming functions
	def dream(self, imagepah):
		fails = 0
		if self.dreaming:
			self.speak("i am dreaming")
			return None
		else:
			self.speak_dialog("dream")
			self.speak("please wait while the dream is processed")

		while fails <=5:
			layer = random.choice(self.layers)
			try:
				dreampic = imutils.resize(cv2.imread(imagepah), self.w, self.h)
				self.dreaming = True
				image = self.bc.dream(np.float32(dreampic),end=layer,iter_n=int(self.iter))
				self.dreaming = False
				return image
			except:
				#self.speak("i couldnt dream this time. Retrying")
				print "failed with layer: " +layer + " in model: " + self.model
				fails +=1
		self.dreaming = False
		print "failed 5 times to dream for unknown reason, someone help debug this!!!"
		self.speak("Could not dream this time")
		return None

	def guided_dream(self, sourcepath, guidepath):

		if self.dreaming:
			self.speak("i am dreaming")
			return None
		else:
			self.speak_dialog("dream")
			self.speak("please wait while the dream is processed")
		fails = 0
		while fails <=5:
			self.dreaming = True
			layer = random.choice(self.layers)
			try:
				features = self.bc.prepare_guide(Image.open(guidepath), end=layer)
				dreampic = imutils.resize(cv2.imread(sourcepath), self.w, self.h)  # cv2.resize(img, (640, 480))
				image = self.bc.dream(np.float32(dreampic), end=layer,
									  iter_n=int(self.iter), objective_fn=self.bc.guided_objective,
									  objective_features=features)

				self.dreaming = False
				return image
			except:
				#self.speak("i couldnt dream this time. Retrying")
				print "failed with layer: " +layer + " in model: " + self.model
				print "with guide: " + guidepath + " \nwith source: " + sourcepath
				fails +=1
		print "failed 5 times to dream for unknown reason, someone help debug this!!! something to do with guided dreaming"
		self.dreaming = False
		self.speak("Could not dream this time")
		return None


def create_skill():
	return DreamSkill()
