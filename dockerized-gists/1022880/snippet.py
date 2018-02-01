#!/usr/local/bin/python3.2
# -*- coding: UTF-8 -*-

import sys
import re
import subprocess

COMMAND  = "./extract.sh"

class ETL:
	def __init__(self, cv_file):
		self.__entreprises    = []
		self.__periodes       = []
		self.__responsabilite = []
		self.__fonctions      = []
		self.__projets        = []
		self.__envtech        = []
		self.__cv             = {}
		
		# import pdb; pdb.set_trace()
		
		raw_cv = subprocess.Popen([COMMAND, cv_file], stdout = subprocess.PIPE).communicate()[0]
		texte = str(raw_cv.decode())
		print(texte)
		self.__cv = self.to_json(texte)
	
	def to_array(self, raw_cv):
		ary = []
		cpt = 0
		for line in raw_cv.split("\n"):
			line = line.split(":", 2)
			ary.append(line)
		for item in ary:
			if len(item) == 2:
				value = item[1]
				switch_value = item[0]
				if switch_value == "Historique":
					if cpt % 2 == 1:
						self.__periodes.append(value.strip)
					else:
						self.__entreprises.append(value.strip)
					cpt += 1
				elif switch_value == "Projet":
					self.__projets.append(value.strip)
				elif switch_value == "Fonction":
					self.__fonctions.append(value.strip)
				elif switch_value == "Environnement technique":
					self.__envtech.append(value.strip)
				elif switch_value == "Responsabilité":
					responsabilite = self.cleanup(value)
					self.__responsabilite.append(responsabilite.strip)
		self.__experiences = int(cpt / 2)
	
	def to_json(self, raw_cv):
		self.to_array(raw_cv)
		for line in raw_cv.split("\n"):
			if line != "":
				line = line.split(":", 2)
				key = line[0]
				self.__cv[key] = line[1]
		self.reformat()
		return self.__cv
	
	def reformat(self):
		for value in self.__cv:
			# value = item[1]
			if value != None and value != "":
				value = self.cleanup(value)
		
		categories = ["Expérience sectorielle","Compétences fonctionnelles","Diplômes et certifications","Compétences techniques","Domaines de compétences"]
		for cat in categories:
			self.format_category(cat)
		self.format_career_history()
		self.format_langues()
		if self.__cv["Formations"] != None:
			self.format_formations()
	
	def format_career_history(self):
		historique = {}
		for i in range(self.__experiences):
			exp = "experience_" + str(i)
			historique[exp] = {}
			historique[exp]["entreprise"]     = self.__entreprises[i]
			historique[exp]["periode"]        = self.__periodes[i]
			historique[exp]["projet"]         = self.__projets[i]
			historique[exp]["fonction"]       = self.__fonctions[i]
			# historique[exp]["responsabilite"] = self.__responsabilite[i]
			# historique[exp]["envtech"]        = self.__envtech[i]
		self.__cv["Historique de carrière"] = historique
		
		# categories = ["Historique","Projet","Fonction","Responsabilité","Environnement technique"]
		# for cat in categories:
		# 	self.__cv.delete(cat)
	
	def cleanup(self, text):
		if text != "":
			text = re.sub("&amp;", '&', text)
			text = re.sub("\s*\|\s*", '|', text)
			text = re.sub("^\s*\|\s*", '', text) # clean up at beginning of line
			text = re.sub("\s*\|\s*$", '', text) # clean up at end of line
		return text
	
	def format_formations(self):
		form = self.__cv["Formations"]
		form = self.cleanup(form)
		ary = []
		for element in form.split("|"):
			ary.append(element)
		self.__cv["Formations"] = ary
	
	def format_langues(self):
		langues = {}
		
		print(self.__cv)
		for lang in self.__cv["Langues"].split("|"):
			lang = lang.split(":")
			langues[lang[0]] = lang[1]
		self.__cv["Langues"] = langues
	
	def format_category(self, cv_category):
		content = self.cleanup(self.__cv[cv_category])
		ary = []
		for element in content.split("|"):
			ary.append(element)
		self.__cv[cv_category] = ary
	
	def out(self):
		print(self.__cv)


#Runs all the functions
def main():
	a = ETL(sys.argv[1])
	a.out

#This idiom means the below code only runs when executed from command line
if __name__ == '__main__':
	main()
