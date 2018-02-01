#!/usr/bin/env python

"""
Modified from

http://macscripter.net/viewtopic.php?id=26675
http://apple.stackexchange.com/questions/90040/look-up-a-word-in-dictionary-app-in-terminal

HowTo

chmod 755 define.py # make file executable
alias define="'/Users/me/Script/define.py'" # => add to .emacs_profile

# then (from command line)
define recursive # or any other word

# .. definition follows ..

"""



import sys

try:
	from DictionaryServices import *
except:
	print "WARNING: The pyobjc Python library was not found. You can install it by typing: 'pip install -U pyobjc'"
	print "..................\n"
	

try:
	from colorama import Fore, Back, Style
except:
	print "WARNING: The colorama Python library was not found. You can install it by typing: 'pip install colorama'"
	print "..................\n"




	
def main():
	"""
	define.py
	
	Access the default OSX dictionary
	
	2015-11-27
	-added colors via colorama
	
	"""
	try:
		searchword = sys.argv[1].decode('utf-8')
	except IndexError:
		errmsg = 'You did not enter any terms to look up in the Dictionary.'
		print errmsg
		sys.exit()
	wordrange = (0, len(searchword))
	dictresult = DCSCopyTextDefinition(None, searchword, wordrange)
	if not dictresult:
		errmsg = "'%s' not found in Dictionary." % (searchword)
		print errmsg.encode('utf-8')
	else:
		s = dictresult.encode("utf-8")	
		arrow = doColor("\n\n\xe2\x96\xb6 ", "red")			
		s = s.replace('\xe2\x96\xb6', arrow)  # arrow
		
		bullet = doColor("\n\xe2\x80\xa2 ", "red")	
		s = s.replace('\xe2\x80\xa2', bullet)	# bullet
		
		phrases_header = doColor("\n\nPHRASES\n", "important")
		s = s.replace('PHRASES', phrases_header)
		
		derivatives_header = doColor("\n\nDERIVATIVES\n", "important")
		s = s.replace('DERIVATIVES', derivatives_header)
		
		origin_header = doColor("\n\nORIGIN\n", "important")
		s = s.replace('ORIGIN', origin_header)
		
		print doColor("Dictionary entry for:\n", "red")
		print s
		print "\n---------------------------------"




def doColor(s, style=None):
	"""
	util for returning a colored string
	if colorama is not installed, FAIL SILENTLY
	"""
	try:
		if style == "comment":
			s = Style.DIM + s + Style.RESET_ALL
		elif style == "important":
			s = Style.BRIGHT + s + Style.RESET_ALL
		elif style == "normal":
			s = Style.RESET_ALL + s + Style.RESET_ALL	
		elif style == "red":
			s = Fore.RED + s + Style.RESET_ALL	
		elif style == "green":
			s = Fore.GREEN + s + Style.RESET_ALL			
	except: 
		pass
	return s



if __name__ == '__main__':
	main()