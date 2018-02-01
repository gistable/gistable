#!/usr/bin/python

import spynner
import pyquery
import urllib
import os

# author: Nate Schultz
# contact: github.com/beefy
# created: 10/22/16

# This script downloads all live game PGNs from chess.com and concatinates the resulting files
# Please note you need your chess.com login credentials in the file path below
# Please note this may be broken in the future due to chess.com UI changes

# first line username
# second line password
LOGIN_CRED_FILE_PATH = './chesslogin.txt'

# path to output directory
# autocreated if it doesn't exist
OUTPUT_PATH = './my_chess_games'

if not os.path.exists(OUTPUT_PATH):
	os.makedirs(OUTPUT_PATH)

url_old_game_archive = "https://www.chess.com/home/my_archive"
url_old_game_archive_all_live = "https://www.chess.com/home/my_archive?sortby=&show=live&color=all&result=all"
url_new_game_archive = "https://www.chess.com/games/archive"

next_page = lambda page_num: url_old_game_archive_all_live+"&page="+str(page_num)

# initialize browser
def init_browser():
	b = spynner.Browser(debug_level=spynner.INFO)
	b.load("https://www.chess.com/login")
	b.load_jquery(True)
	return b

# login from new chess.com
def login_new(b):
	b.click_link('a[href="//www.chess.com/switch?request_uri=%2Flogin"]')
	credentials = [line.strip() for line in open(LOGIN_CRED_FILE_PATH,'rb')]
	b.wk_fill('input[id="username"]',credentials[0])
	b.wk_fill('input[id="password"]',credentials[1])
	b.click_link('button[id="login"]')

# login from old chess.com
def login_old(b):
	credentials = [line.strip() for line in open(LOGIN_CRED_FILE_PATH,'rb')]
	b.wk_fill('input[name="c1"]',credentials[0])
	b.wk_fill('input[name="loginpassword"]',credentials[1])
	b.click_link('button[name="btnLogin"]')

# load ajax
def load_ajax(b):
	js_str = 'var script = document.createElement("script");script.src = "http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js";document.getElementsByTagName("head")[0].appendChild(script);'
	b.runjs(js_str)
	b.wait(5) # let ajax finish

# "depricated"
def check_checkboxes(b):
	# first attempt: I tried to do the typical checkboxes + download button on the new chess.com
	# but the download button proved too difficult, so I had to use the old chess.com
	# this code checks the first 10 checkboxes, as a test

	# index checkboxes
	js_str = "i = 0; $('input[game-checkbox]').each( function() { $(this).attr('id','game-checkbox'+i); i++; });"
	b.runjs(js_str)

	# iterate checkboxes
	for i in range(10):
		b.click('input[id="game-checkbox'+str(i)+'"]')

	b.click('.pull-right.download-all')

def scrape(b):

	links_per_page = 50		
	chess_game_extension = '.chessgame'
	chess_page_extension = '.chesspage'
	game_delimiter = '\nwww.thenateschultz.com\ngithub.com/beefy\n'

	# page iteration
	page_i = 1;
	while True:

		# index view links
		js_str = "i = 0; jQuery('.games.right-4').each( function() { jQuery(this).attr('id','game-view'+i); i++; });"
		b.runjs(js_str)

		# game iteration (same # every page)
		for i in range(links_per_page):
			b.click_link('#game-view'+str(i)) # click 'view' link
			# download PGN
			d = pyquery.PyQuery(b.html)
			raw_href = d('a[class="bpgn"]').attr("href") # get download link
			href = urllib.unquote(raw_href)
			b.download(href, open(OUTPUT_PATH+'/PGN_'+str(i)+chess_game_extension,'w')) # write PGN to file
			b.load(url_old_game_archive_all_live) # redirect to game archive
		
			# re-index view links
			js_str = "i = 0; jQuery('.games.right-4').each( function() { jQuery(this).attr('id','game-view'+i); i++; });"
			b.runjs(js_str)

		# merge PGNs
		PGNs = [open(os.path.join(OUTPUT_PATH, file),'rb') for file in os.listdir(OUTPUT_PATH) if file.endswith(chess_game_extension)]
		PGN_data = [file.read() for file in PGNs]
		PGN_page_str = game_delimiter.join(PGN_data)
		PGN_page_out = open(OUTPUT_PATH+'/page'+str(page_i)+chess_page_extension,'w')
		PGN_page_out.write(PGN_page_str)
		PGN_page_out.close()
		for file in PGNs:
			os.remove(file.name) # delete merged files

		try:
			# redirect to next page!
			page_i += 1
			b.load(next_page(page_i))
		except:
			# I guess there's no more pages
			# merge pages
			PGNs = [open(os.path.join(OUTPUT_PATH, file),'rb') for file in os.listdir(OUTPUT_PATH) if file.endswith(chess_page_extension)]
			PGN_data = [file.read() for file in PGNs]
			PGN_page_str = game_delimiter.join(PGN_data)
			PGN_page_out = open(OUTPUT_PATH+'/PGNs.txt','w')
			PGN_page_out.write(PGN_page_str)
			PGN_page_out.close()
			for file in PGNs:
				os.remove(file.name) # delete merged files

			return

if __name__ == "__main__":
	b = init_browser()
	login_old(b)
	b.load(url_old_game_archive_all_live) # redirect to game archive
	load_ajax(b)
	scrape(b)
	# b.browse() # activate GUI