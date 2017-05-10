
import os
import random
import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))
from service_display.displayservice import DisplayService
from skill_art.art_utils import makeImage as psy_art
from skill_art.art_utils.geopatterns import GeoPattern

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill

__author__ = 'jarbas'


class ArtSkill(MycroftSkill):

	def __init__(self):
		super(ArtSkill, self).__init__(name="ArtSkill")
		self.reload_skill = False

		try:
			self.patternpath = self.config_core["database_path"] + "/pictures/patterns"
			self.psypath = self.config_core["database_path"] + "/pictures/psy"
		except:
			self.patternpath = dirname(__file__) + "/patterns"
			self.psypath = dirname(__file__) + "/psy"

		# check if folders exist
		if not os.path.exists(self.patternpath):
			os.makedirs(self.patternpath)
		if not os.path.exists(self.psypath):
			os.makedirs(self.psypath)

	def initialize(self):
		psy_intent = IntentBuilder("PsyArtIntent").require("psyart").build()
		self.register_intent(psy_intent, self.handle_psy_pic_intent)

		pattern_intent = IntentBuilder("PatternsIntent").require("pattern").build()
		self.register_intent(pattern_intent, self.handle_pattern_intent)

		self.screen_service = DisplayService(self.emitter)

	def handle_psy_pic_intent(self, message):
		pic = psy_art(self.psypath, 1)[0]
		self.screen_service.show(pic, message.data["utterance"])
		self.speak_dialog("psy")

	def handle_pattern_intent(self, message):
		s = "cool that you are reading this, suggest changes to this code in issues :)"
		for i in range(0,random.randint(100, 9999)):
			s += random.choice("afawegawsgSATENawsghgvfcqwertyuioplkjhjhgfdsazxcvbnm<>SETKSAEK6de3456789EVILoijhbgvfcdjfhgjhjlink hjghfhghnmk!#$%&/(&%")

		pic = self.generate_pattern(s)
		self.screen_service.show(pic, message.data["utterance"])
		self.speak_dialog("pattern")

	def stop(self):
		pass

	def generate_pattern(self, string, num=1):
		generators = ["hexagons", "overlapping_circles", "overlapping_rings", "plaid", "plus_signs", "rings", "sinewaves", "squares", "xes"]
		i=0
		savepath = ""
		while i<num:
			try:
				pattern = GeoPattern(string, random.choice(generators))
				svg = pattern.svg_string
				savepath = self.patternpath + "/" + str(i) + ".svg"
				fout = open(savepath, "wb")
				fout.write(svg)
				fout.close()
			except:
				i -= 1
			i += 1
		return savepath


def create_skill():
	return ArtSkill()
