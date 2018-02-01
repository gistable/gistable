#!/usr/bin/python

'''
This script finds missing string translations in Android applicaitons.

Author: Kostya Vasilyev. License: Creative Commons Attribution.

The output format is, I believe, more suitable to working with external
translators than the output of Lint from the Android SDK.

usage: find_missing_translations.py [-h] [-i LANG] res [res ...]

positional arguments:
  res                   Resource directory to check

optional arguments:
  -h, --help            show this help message and exit
  -i LANG, --ignore LANG
                        Ignore a particular language code
                        
Run it like this from your project's directory:

	> find_missing_translations.py res
	
Or do this to check a library at the same time:

	> find_missing_translations.py res ../MyLibrary/res
	
The output is sorted by language code, so it can be easily collected and sent to your translator(s)
all at once. For example:

	Checking language 2, de

	***** Found 44 missing translations for language de

	<!-- res/values/strings_account_list.xml -->

	<string name=account_list_menu_uilock_now>Lock now</string>

	<!-- res/values/strings_account_options.xml -->

	<string name=account_options_folder_sync_type_spam>Sync as spam</string>
	<string name=account_options_prefs_preload_inlines_mobile>Embedded images, mobile</string>
	<string name=account_options_prefs_preload_inlines_wifi>Embedded images, WiFi</string>
	<string name=account_options_prefs_signature_auto>Add signature automatically</string>

	Checking language 1, uk

	***** Found 47 missing translations for language uk
	
	... all missing translations for Ukrainian are printed here
	
If you have a language whose translation is out of date, and not going to be updated, you can
exclude it from checking by using the "-i" switch:

	> find_missing_translations.py -i zh res
	
This will ignore directories such as "values-zh-rCN", "values-zh-rHK", just "values-zh", and so on,
making the output cleaner for the languages you care about.

Strings marked with translatable="false" or redirecting with "@string" are ignored.

'''

import sys
import argparse
import os
import re
import xml.parsers.expat

'''
SAX parse event handler
'''
class XmlHandler:
	''' 
	Constructor
	'''
	def __init__(self):
		self.insideString = False
		self.insideStringArray = False
		self.tag = None
		self.name = None
		self.data = None
		self.childCount = 0
		self.stringCount = 0
		self.stringArrayCount = 0;
		self.StringCallback = None
		self.StringArrayCallback = None
	'''
	Start XML element
	'''
	def start_element(self, name, attrs):
		self.insideString = False
		trans = attrs.get('translatable')
		if trans == 'false':
			#print u'String not translatable: {0}'.format(attrs['name'])
			self.name = None
		elif name == u'string':
			self.data = None
			self.tag = u'' + name
			self.name = u'' + attrs['name']
			if self.name:
				self.insideString = True
		elif name == u'string-array':
			self.data = None
			self.tag = u'' + name
			self.name = u'' + attrs['name']
			self.childCount = 0
			if self.name:
				self.insideStringArray = True
	'''
	End XML element
	'''
	def end_element(self, name):
		if name == u'string' and self.insideString:
			if self.data and not self.data.startswith('@string/'):
				self.stringCount += 1
				self.StringCallback(self.tag, self.name, self.data)
			self.insideString = False
		elif name == u'item' and self.insideStringArray:
			self.childCount += 1
		elif name == u'string-array' and self.insideStringArray:
			print u'string-array: {0} {1}'.format(self.name, self.childCount)
			self.stringArrayCount += 1
			self.StringArrayCallback(self.tag, self.name, self.data, self.childCount)
			self.insideStringArray = False
	'''
	Character data
	'''
	def char_data(self, data):
		if self.data:
			self.data += data
		else:
			self.data = u'' + data
'''
Check state for one string.

Keeps track of language bits (one bit for each language, except the default),
the string name, the default value, and orignal resource file where declared
'''
class StringState:
	def __init__(self, tag, name, data, resfile, childCount = 0):
		self.langBits = 0;
		self.tag = tag
		self.name = name
		self.data = data
		self.resfile = resfile
		self.childCount = childCount

class StringList:
	'''
	Constructor
	'''
	def __init__(self, langIgnoreList):
		self.stringDict = {}
		self.langIgnoreList = langIgnoreList if langIgnoreList else {}
	'''
	Scans a res directory
	'''
	def scanResDirectory(self, res):
		print 'Scanning:', res
		self.scanValuesDirectory(os.path.join(res, 'values'), 0, 'Default')
		langBit = 0
		langList = {}
		for top, dirs, files in os.walk(res):
			for nm in sorted(dirs):
				if nm != 'values':
					m = re.match('^values-(([a-z]{2})(-r[a-zA-Z]{2})?)$', nm)
					if m != None:
						langFull = m.group(1)
						langShort = m.group(2)
						langName = langFull
						if not langShort in self.langIgnoreList and not langFull in self.langIgnoreList:
							if langBit == 0:
								langBit = 1
							else:
								langBit = langBit << 1
							langList[langBit] = langName
							self.scanValuesDirectory(os.path.join(top, nm), langBit, langName)
		while langBit != 0:
			langName = langList.get(langBit)
			self.findMissingTranslations(langBit, langName)
			langBit = langBit >> 1
	'''
	Scans a res/values{-lang} directory
	'''
	def scanValuesDirectory(self, values, langBit, langName):
		print 'Scanning:', values, 'langBit =', langBit, 'langName =', langName
		for top, dirs, files in os.walk(values):
			for nm in sorted(files):
				if not nm.endswith("non_nls.xml"):
					self.scanValuesFile(os.path.join(top, nm), langBit, langName)
	'''
	Scans a res/values{-lang}/foo.xml resource file
	'''
	def scanValuesFile(self, resfile, langBit, langName):
		print 'File:', resfile,
		with open(resfile, 'r') as f:
			self.dontNeedTranslationString = []
			self.dontNeedTranslationStringArray = []
			def stringCallback(tag, name, data):
				if langBit is 0:
					ss = StringState(tag, name, data, resfile)
					self.stringDict[name] = ss
				else:
					ss = self.stringDict.get(name)
					if ss:
						ss.langBits = ss.langBits | langBit
					else:
						self.dontNeedTranslationString.append(name)
			def stringArrayCallback(tag, name, data, childCount):
				if langBit is 0:
					ss = StringState(tag, name, data, resfile, childCount)
					self.stringDict[name] = ss
				else:
					ss = self.stringDict.get(name)
					if ss:
						if ss.childCount != childCount:
							print(u'*** Fatal error: in {0}, string-array "{1}" size mismatch: {2}, {3}' \
								.format (resfile, name, ss.childCount, childCount))
							sys.exit(1)
						ss.langBits = ss.langBits | langBit
					else:
						self.dontNeedTranslationStringArray.append(name)
						
			h = XmlHandler()
			h.StringCallback = stringCallback
			h.StringArrayCallback = stringArrayCallback
			p = xml.parsers.expat.ParserCreate()
			p.StartElementHandler = h.start_element
			p.EndElementHandler = h.end_element
			p.CharacterDataHandler = h.char_data
			p.ParseFile(f)
			print '{0}, {1}'.format(h.stringCount, h.stringArrayCount)
			
			for name in self.dontNeedTranslationString:
				print '*** string "', name, '" does not need to be translated'
			for name in self.dontNeedTranslationStringArray:
				print '*** string-array "', name, '" does not need to be translated'
	'''
	Looks for missing translations
	'''
	def findMissingTranslations(self, langBit, langName):
		print u'\n***** Checking language {0}, {1}'.format(langBit, langName)
		missing = []
		
		for ss in self.stringDict.values():
			if (ss.langBits & langBit) == 0:
				missing.append(ss)

		if missing:
			print '\n***** Found', len(missing), 'missing translations for language', langName
			resfile = None
			for ss in sorted(missing, key = lambda ss: ss.resfile + ss.name):
				if not resfile or resfile != ss.resfile:
					print '\n<!--', ss.resfile, '-->\n'
					resfile = ss.resfile
				print u'<{0} name="{1}">{2}</{0}>'.format(ss.tag, ss.name, ss.data, ss.tag)

if __name__ == "__main__":
	'''
	Parse command line arguments
	'''
	parser = argparse.ArgumentParser(description='Finds missing string translations in Android applicaitons')
	parser.add_argument('-i', dest='LANG', action='append', help='ignore a particular language code')
	parser.add_argument('res', nargs='+', help='resource directory to check (one or more)')
	args = parser.parse_args()

	sl = StringList(args.LANG)
	for resdir in args.res:
		sl.scanResDirectory(resdir)
