#!/usr/bin/env python3
"""speak: A best TTS (pico2wav) wrapper for Linux."""

import os, bs4, re, math, argparse, requests

DEFAULT_BATCH_SIZE = 10


def shellQuote(text):
	"""Symbol escaping for shell."""
	return "'" + text.replace("'", "'\\''") + "'"


def toAscii(text):
	"""Clean the text of crap for reading."""
	asciiText = ''.join([ch if ord(ch) < 128 else ' ' for ch in text])
	return asciiText.replace('\r', '')


def __speak__(text):
	"""Bare text feed to TTS (pico2wav)."""
	text = shellQuote(text)
	waveFile = '/dev/shm/pico2wave_speak.wav'
	waveCmd = 'pico2wave -l=en-US -w=%s %s' % (waveFile, text)
	playCmd = 'aplay %s' % waveFile
	try:
		os.system(waveCmd)
		os.system(playCmd)
		os.remove(waveFile)
	except Exception as ex:
		print('Exception type:' + str(type(ex)))
		print(ex)


def speak(text, echo = False, batchSize = DEFAULT_BATCH_SIZE):
	"""Reading, ain't nobody got time for that."""
	text = toAscii(text)
	if batchSize == 0:
		if echo:
			print(text)
		__speak__(text)
		return
	lines = text.splitlines()
	totalBatches = int(math.ceil(1.0 * len(lines) / batchSize))
	accumulator = []
	for line in lines:
		accumulator.append(line)
		if len(accumulator) == batchSize:
			textBatch = ''.join(accumulator)
			if echo:
				print(textBatch)
			__speak__(textBatch)
			accumulator = []
			cont = raw_input('\ncontinue reading? ([YES,Y,y,yes]|anything else):')
			if not re.match('(YES|Y|y|yes)', cont):
				return
	textBatch = ''.join(accumulator)
	if echo:
		print(textBatch)
	__speak__(textBatch)


def speakFile(textFile, echo = True, batchSize = DEFAULT_BATCH_SIZE):
	"""Read a plain text file."""
	with open(textFile, 'rt') as fin:
		speak(fin.read(), echo, batchSize)


def speakPdf(pdfFile, pageNumber = 0, echo = True):
	"""Read a pdf."""
	pdf = pypdf.PdfFileReader(open(pdfFile, 'rb'))
	currentPage = 0
	for page in pdf.pages:
		currentPage += 1
		if pageNumber == 0 or pageNumber == currentPage:
			speak(page.extractText(), echo, batchSize = 0)
			cont = raw_input('\ncontinue reading? ([YES,Y,y,yes]|anything else):')
			if not re.match('(YES|Y|y|yes)', cont):
				break


def speakUrl(url, echo = True, batchSize = DEFAULT_BATCH_SIZE):
	"""Read a webpage."""
	txt = url2text(url)
	speak(txt, echo, batchSize)


def cleanHtml(htmlElement):
	"""Purify HTML."""
	htmlText = toAscii(htmlElement).strip()
	htmlText = re.sub(r'\s\s*', ' ', htmlText)
	htmlText = htmlText.replace('&nbsp;', '')
	return htmlText


def url2text(url, parts = False):
	"""Extracts visible text from a webpage."""
	if not url.lower().startswith('http'):
		url = 'http://' + url
	htmlSrc = requests.get(url).text
	htmlSoup = bs4.BeautifulSoup(htmlSrc, 'lxml')
	htmlTexts = htmlSoup.findAll(text = True)
	visibleTexts = filter(isVisible, htmlTexts)
	if parts:
		return visibleTexts
	htmlText = ''.join(visibleTexts)
	return cleanHtml(htmlText)


def isVisible(htmlElement):
	"""HTML visibility filter."""
	elementFilter = ['style', 'script', '[document]', 'head', 'style', 'title']
	elementText = cleanHtml(htmlElement)
	if htmlElement.parent.name in elementFilter:
		return False
	elif re.match('<!--.*-->', elementText):
		return False
	elif re.match('^\s+$', elementText):
		return False
	elif re.match('^<.+>$', elementText):
		return False
	return True


if __name__ == '__main__':
	speakDescription = """
	speak - A best TTS (pico2wav) wrapper for Linux.

	e.g.
	$ speak --help
	$ speak text "reading, ain't nobody got time for that!"
	$ speak file tldr.txt
	$ speak --echo pdf tldf.pdf
	War And Peace...
	$ speak url http://tldr.com
	
	#Debian+ Install:
	sudo mv speak /usr/local/bin/speak
	sudo chmod +x /usr/local/bin/speak
	sudo apt-get -y install pico2wav
	sudo pip install -U bs4, pypdf
	"""
	parser = argparse.ArgumentParser(description = speakDescription,
		formatter_class = argparse.RawTextHelpFormatter)
	cmdHelp = """command options: text, file, pdf, url"""
	argHelp = """cmdarg options:
		text : "A quoted text string. Read me."
		file : Path to a text file.
		pdf  : Path to a pdf file.
		url  : A url, including http[s] protocol specifier."""
	echoHelp = """Echo the text to stdout."""
	batchSizeHelp = """Provide a reading batch size. (0 = all) (default = 10)"""
	parser.add_argument('command', type=str, help = cmdHelp)
	parser.add_argument('cmdarg', type=str, help = argHelp)
	parser.add_argument('-e', '--echo', action = 'store_true', help = echoHelp)
	parser.add_argument('-b', '--batchsize', type = int, help = batchSizeHelp)
	args = parser.parse_args()
	batchSize = DEFAULT_BATCH_SIZE
	if args.batchsize:
		batchSize = args.batchsize
	if args.command == 'text':
		speak(args.cmdarg, args.echo, batchSize)
	elif args.command == 'file':
		speakFile(args.cmdarg, args.echo, batchSize)
	elif args.command == 'pdf':
		speakPdf(args.cmdarg, pageNumber = 0, echo = args.echo)
	elif args.command == 'url':
		speakUrl(args.cmdarg, args.echo, batchSize)
	else:
		print('speak -h # For help.')
