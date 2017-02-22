
from os.path import dirname
import urllib2
import cv2
import numpy as np
import os
import random
from threading import Thread
import json
from bs4 import BeautifulSoup
from PIL import Image
import imutils
import sys
from time import sleep

from mycroft.skills.dreamskill.randomart import makeImage
from mycroft.skills.dreamskill.geopatterns import GeoPattern

import cairosvg



from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message

__author__ = 'jarbas'

logger = getLogger(__name__)
dreamlogger = getLogger('Dream ')

client = None

class DreamSkill(MycroftSkill):

	def __init__(self):
		super(DreamSkill, self).__init__(name="DreamSkill")

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

		#elif model =="hybridCNN_upgraded":
		#    self.layers = ["conv1", "relu1", "pool1", "norm1","conv2","relu2","pool2","norm2","conv3","relu3","conv4","relu4",
		#                   "conv5","relu5","pool5","fc6","relu6","drop6","fc7","relu7","drop7","fc8"]
		#elif model =="bvlc_alexnet":
		#    ,

		# random dreaming mode choice
		self.choice = 3  # guided dream=1 normal = 0 guided with dif layers in source and guide = 3

		# Define the codec and create VideoWriter object
		self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
		# self.out = cv2.VideoWriter("dream_output/output.avi",self.fourcc, 20.0, (200,200))
		# self.out = cv2.VideoWriter("dream_output/dream.avi", fourcc, 20.0, (640, 480))

		# make working directories, TODO refactor into config file
		self.sourcespath = os.path.dirname(__file__) + '/sources.txt'
		self.searchpath ="/home/user/mycroft-core/mycroft/skills/RandomPic/pictures/search"
		self.sourcedir = os.path.dirname(__file__) + "/dream_source"
		self.outputdir = os.path.dirname(__file__) +'/dream_output'
		self.sharedfolder = os.path.dirname(__file__) +"/this"
		self.camfolder = os.path.dirname(__file__) +"/cam"
		self.patternpath = os.path.dirname(__file__) +"/patterns"
		self.psypath = os.path.dirname(__file__) +"/psy"
		# check if folders exist
		if not os.path.exists(self.sourcedir):
			os.makedirs(self.sourcedir)
		if not os.path.exists(self.outputdir):
			os.makedirs(self.outputdir)
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
		self.load_data_files(dirname(__file__))

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
		dreampic = cv2.imread(dream)
		self.speak("look at this dream i had")
		cv2.imshow('dream', dreampic)
		cv2.waitKey(20000)
		cv2.destroyWindow('dream')

	def handle_psy_dream_intent(self, message):
		if not self.dreaming:
			client.emit(Message("entropy_request")) #ask for new strings
			makeImage(self.psypath, 3)

		chosenpic = random.choice(os.listdir(self.psypath))
		imagepah = self.psypath+"/" + str(chosenpic)

		i = self.countdreams()

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.psypath))
			guidepah =self.psypath + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah, i)
		else:
			result = self.dream(imagepah, i)

		if result is not None:
			self.speak("Here is what i dreamed")
			cv2.imshow("Dreaming...", result)
			cv2.waitKey(35000)
			#cv2.destroyWindow("Dreaming...")
			#k = cv2.waitKey(1000)
		   # self.out.release()
			cv2.destroyAllWindows()

	def handle_pure_dream_intent(self, message):

		if not self.dreaming:
			client.emit(Message("entropy_request")) #ask for new strings
			self.generate_pattern(random.choice(self.strings))

		chosenpic = random.choice(os.listdir(self.patternpath))
		imagepah = self.patternpath+"/" + str(chosenpic)

		i = self.countdreams()

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.patternpath))
			guidepah =self.patternpath + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah, i)
		else:
			result = self.dream(imagepah, i)

		if result is not None:
			self.speak("Here is what i dreamed")
			cv2.imshow("Dreaming...", result)
			cv2.waitKey(35000)
			#cv2.destroyWindow("Dreaming...")
			#k = cv2.waitKey(1000)
		   # self.out.release()
			cv2.destroyAllWindows()

	def handle_dream_intent(self, message):
		if not self.dreaming:
			self.collectentropy()

		chosenpic = random.choice(os.listdir(self.sourcedir))
		imagepah = self.sourcedir+"/" + str(chosenpic)

		i = self.countdreams()

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.sourcedir))
			guidepah =self.sourcedir + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah, i)
		else:
			result = self.dream(imagepah, i)

		if result is not None:
			self.speak("Here is what i dreamed")
			cv2.imshow("Dreaming...", result)
			cv2.waitKey(35000)
			#cv2.destroyWindow("Dreaming...")
			#k = cv2.waitKey(1000)
		   # self.out.release()
			cv2.destroyAllWindows()

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

		i = self.countdreams()

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.camfolder))
			guidepah =self.camfolder + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah, i)
		else:
			result = self.dream(imagepah, i)

		if result is not None:
			self.speak("Here is what i dreamed")
			cv2.imshow("Dreaming...", result)
			cv2.waitKey(35000)
			#cv2.destroyWindow("Dreaming...")
			#k = cv2.waitKey(1000)
		   # self.out.release()
			cv2.destroyAllWindows()

	def handle_dream_about_dreams_intent(self, message):

		chosenpic = random.choice(os.listdir(self.outputdir))

		if chosenpic is None:
			self.speak("no source picture")
			return

		imagepah = self.outputdir + "/" + str(chosenpic)

		i = self.countdreams()

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.outputdir))
			guidepah = self.outputdir + "/" + str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah, i)
		else:
			result = self.dream(imagepah, i)

		if result is not None:
			self.speak("Here is what i dreamed")
			cv2.imshow("Dreaming...", result)
			cv2.waitKey(35000)
			#cv2.destroyWindow("Dreaming...")
			#k = cv2.waitKey(1000)
		   # self.out.release()
			cv2.destroyAllWindows()

	def handle_dream_about_this_intent(self, message):
		chosenpic = random.choice(os.listdir(self.sharedfolder))

		if chosenpic is None:
			self.speak("no source picture")
			return

		imagepah = self.sharedfolder+"/" + str(chosenpic)

		i = self.countdreams()

		# choose dream mode
		if self.choice != 0:
			chosenguide = random.choice(os.listdir(self.sharedfolder))
			guidepah =self.sharedfolder + "/"+ str(chosenguide)
			# guided dream experiments
			result = self.guided_dream(imagepah, guidepah, i)
		else:
			result = self.dream(imagepah, i)

		if result is not None:
			self.speak("Here is what i dreamed")
			cv2.imshow("Dreaming...", result)
			cv2.waitKey(35000)
			#cv2.destroyWindow("Dreaming...")
			#k = cv2.waitKey(1000)
		   # self.out.release()
			cv2.destroyAllWindows()

	def handle_dream_about_intent(self, message):
		imagepath = ""
		if not self.dreaming:
			# collect dream entropy
			search = message.data.get("DreamSearch")
			pics = self.search_image(search)
			imagepah = random.choice(pics)

		i = self.countdreams()

		# choose dream mode
		if self.choice != 0:
			# guided dream experiments
			result = self.guided_dream(imagepah, random.choice(pics), i)
		else:
			result = self.dream(imagepah, i)

		if result is not None:
			self.speak("Here is what i dreamed")
			cv2.imshow("Dreaming...", result)
			cv2.waitKey(35000)
			#cv2.destroyWindow("Dreaming...")
			#k = cv2.waitKey(1000)
		   # self.out.release()
			cv2.destroyAllWindows()

	def handle_video_dream_intent(self, message):
		self.speak_dialog("dream")
		self.out = cv2.VideoWriter("dream_output/output.avi", self.fourcc, 20.0, (200, 200))
		# collect dream entropy
		self.store_raw_images()
		self.find_uglies()
		chosenpic = random.choice(os.listdir("dreamskill/dream_source"))
		if self.choice != 0:
			chosenguide = random.choice(os.listdir("dreamskill/dream_source"))
			guidepah = "dreamskill/dream_source/" + str(chosenguide)
			glayer = "inception_4c/output"
		imagepah = "dreamskill/dream_source/" + str(chosenpic)
		# create output paths
		if not os.path.exists('dreamskill/dream_video'):
			os.makedirs('dreamskill/dream_video')
		# start video loop
		result = cv2.imread(imagepah)
		outpath = 'dreamskill/dream_video/' + str(len(os.listdir('dreamskill/dream_video')) +1)
		cv2.imwrite(outpath + "/0.jpg", result)
		# dream until q pressed or 100frames
		i = 1
		maxframes = 100
		size = 200
		result = cv2.resize(result, (size, size))
		while (1):
			self.out.write(result)
			cv2.imshow("Dreaming...", result)
			k = cv2.waitKey(100) & 0xFF
			if k == ord('q') or i >= maxframes:
				self.out.release()
				cv2.destroyAllWindows()
				self.bc.cleanup()
				break

			if self.choice == 0:
				result = self.guided_dream(imagepah, guidepah, i, self.bc, glayer)
			else:
				result = self.dream(imagepah, i, self.bc, self.layer)

			zoom = cv2.resize(result, (i * size /10, i/10 * size))
			result = zoom[0:200, 0:200]

			self.layer = random.choice(self.layers)

			imagepah = outpath + "/" + str(i) + ".jpg"
			i += 1

	def stop(self):
		self.out.release()
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
		# self.find_uglies()
	def countdreams(self):
		i = 1
		for f in os.listdir(self.outputdir):
			if os.path.isfile(os.path.join(self.outputdir, f)):
				i += 1
		return i

	def store_raw_images(self, number=1):

		with open(self.sourcespath) as f:
			urls = f.readlines()
		i = 0
		pic_num = 0
		while i < number:
			try:
				image_urls = urllib2.urlopen(random.choice(urls)).read().decode('utf-8')
				chosenurl = random.choice(image_urls.split('\n'))
				print(chosenurl)
				url_response = urllib2.urlopen(chosenurl)
				img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
				img = cv2.imdecode(img_array, -1)
				print('Saving pic! ')
				# img = cv2.resize(img, (200, 200))
				cv2.imwrite(self.sourcedir+"/" + str(pic_num) + ".jpg", img)
				pic_num += 1
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

	def find_uglies(self):
		match = False
		for file_type in [self.sourcedir]:
			for img in os.listdir(file_type):
				for ugly in os.listdir('dreamskill/uglies'):
					try:
						current_image_path = self.sourcedir +'/' + str(img)
						ugly = cv2.imread('dreamskill/uglies/' + str(ugly))
						question = cv2.imread(current_image_path)
						if ugly.shape == question.shape and not (np.bitwise_xor(ugly, question).any()):
							print('That is one ugly pic! Deleting!')
							print(current_image_path)
							os.remove(current_image_path)
					except Exception as e:
						print(str(e))

	#### dreaming functions
	def dream(self, imagepah, i):
		#dreampic = np.zeros((480, 640, 3), np.uint8)

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
				dreampic = imutils.resize(cv2.imread(imagepah), self.w, self.h)  # cv2.resize(img, (640, 480))
				self.dreaming = True
				image = self.bc.dream(np.float32(dreampic), end=layer)
				# write the output image to file
				result = Image.fromarray(np.uint8(image))
				result.save(self.outputdir+"/" + str(i) + ".jpg")
				dreampic = cv2.imread(self.outputdir+"/" + str(i) + ".jpg")
				# draw the layer name on the image
				#cv2.putText(dreampic, layer, (5, dreampic.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.95, (0, 255, 0), 2)
				cv2.imwrite(self.outputdir+"/" + str(i) + ".jpg", dreampic)
				# apply filters
				#filter = random.choice(range(0, 8))
				#dreampic = self.filterdream(filter, dreampic)
				#cv2.imwrite("dreamskill/dream_output/" + str(i+1) + ".jpg", dreampic)
				#dreampic.save()
				self.dreaming = False
				return dreampic
			except:
				#self.speak("i couldnt dream this time. Retrying")
				print "failed with layer: " +layer + " in model: " + self.model
				fails +=1
		self.dreaming = False
		print "failed 5 times to dream for unknown reason, someone help debug this!!!"
		self.speak("Could not dream this time")
		return None

	def guided_dream(self, sourcepath, guidepath, i):

		#dreampic = np.zeros((480, 640, 3), np.uint8)
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
				if self.choice != 1:
					layer = random.choice(self.layers)  # different layer for guide
				dreampic = imutils.resize(cv2.imread(sourcepath), self.w, self.h)  # cv2.resize(img, (640, 480))
				image = self.bc.dream(np.float32(dreampic), end=layer,
									  iter_n=self.iter, objective_fn=BatCountry.guided_objective,
									  objective_features=features)
				# write the output image to file
				result = Image.fromarray(np.uint8(image))
				result.save(self.outputdir+"/" + str(i) + ".jpg")
				dreampic = cv2.imread(self.outputdir+"/" + str(i) + ".jpg")
				# draw the layer name on the image
				#cv2.putText(dreampic, layer, (5, dreampic.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.95, (0, 255, 0), 2)
				cv2.imwrite(self.outputdir+"/" + str(i) + ".jpg", dreampic)
				# apply filters
				#filter = random.choice(range(0, 8))
				#dreampic = self.filterdream(filter, dreampic)
				#cv2.imwrite("dreamskill/dream_output/" + str(i+1) + ".jpg", dreampic)
				#dreampic.save()
				self.dreaming = False
				return dreampic
			except:
				#self.speak("i couldnt dream this time. Retrying")
				print "failed with layer: " +layer + " in model: " + self.model
				print "with guide: " + guidepath + " \nwith source: " + sourcepath
				fails +=1
		print "failed 5 times to dream for unknown reason, someone help debug this!!!"
		self.dreaming = False
		self.speak("Could not dream this time")
		return None

	### opencv filter functions
	def filterdream(self, filter, dream):
		if filter == 0:
			dream = self.cartoonify(dream)
		elif filter == 4:
			dream = self.cartoonify(dream)
			dream = self.detail_enhance(dream)
		elif filter == 6:
			dream = self.detail_enhance(dream)
		elif filter == 8:
			dream = self.detail_enhance(dream)
			dream = self.cartoonify(dream)
			dream = self.smothify(dream)
		return dream

	def cartoonify(self, pic):
		return cv2.stylization(pic, sigma_s=60, sigma_r=0.07)
		### nightmare

	def nightmarify(self, pic, bw=True):
		nght_gray, nght_color = cv2.pencilSketch(pic, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
		if bw:
			# nght_gray = cv2.cvtColor(nght_gray, cv2.COLOR_GRAY2BGR)
			return nght_gray
		return nght_color
		#### detail enhance

	def detail_enhance(self, pic):
		return cv2.detailEnhance(pic, sigma_s=10, sigma_r=0.15)
		#### smothify

	def smothify(self, pic):
		return cv2.edgePreservingFilter(pic, flags=1, sigma_s=60, sigma_r=0.4)
		#### skeletonize

	def skeletonize(self, pic):
		gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
		skelton = imutils.skeletonize(gray, size=(3, 3))
		return skelton
		###### tresh

	def tresholdify(self, pic):
		pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
		pic = cv2.GaussianBlur(pic, (5, 5), 0)
		pic = cv2.adaptiveThreshold(pic, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
		return pic

def create_skill():
	return DreamSkill()
