#!/bin/python
from lxml import html
import requests
import sys
import json
import os
from colorama import init
init()
from colorama import Fore, Back, Style


# HOWTO
# ===============================================
# BEGINNER
#   -> Follow the steps
# INTERMEDIATE
# /search ENTER search>>>[your search term]
 
# TIP - When on an episode list page for a show you can save your place for later
# /save [custom slug name] [episode to bookmark]
# Load it later with the load command 
# /load ENTER
# then when prompted load>>>[custom slug or slug partial]
# /ls <ENTER> - to view saved anime and saved episode

# Were we have permission to r/w and where bookmarked shows are saved
SAVE_FILE = os.environ['HOME'] + '/.wanime'

# Class for requesting resources from animejoy
class WAnime:
    base_url    = 'http://animejoy.tv/'
    loaded      = {}
    shows       = {}
    episode     = 1

    #return output lines and selector dictionary
    def searchShows(self,term=''):
        lines = []
        success = False
        print('Searching...')
        try:
            page = requests.get(self.base_url + 'search.php?term=' + term)
            results = json.loads(page.text)
            if len(results):
                success = True
                self.shows = {}
                i = 0
                for r in results:
                    self.shows[str(i)] = {"id": r['id'], "nicename": r['value']}
                    lines.append(Back.BLUE + '[' + str(i) + ']  ' + r['value'])
                    i += 1
        except:
            pass
        return [lines,success]

    #return output lines and loaded dictionary
    def loadShow(self,index=None,show_id=None):
        lines = []
        success = False
        try:
            if index is not None:
                self.loaded = self.shows[index]
                #if show id exists self loaded should have the saved data
            print('Loading '+ self.loaded["nicename"])
            page = requests.get(self.base_url + 'watch/' + self.loaded["id"])
            tree = html.fromstring(page.text)
            episodes = tree.xpath('//div[@class="episodes"]/div[@class="ep"]')
            if len(episodes):
                success = True
                self.loaded["real_nicename"] = episodes[0].xpath('a/text()')[0].split("Episode")[0].strip()
                self.loaded["real_id"] = self.loaded["real_nicename"].replace(" ","-").replace("(TV)","TV").replace("(OVA)","OVA")
                self.loaded["last_updated"] = None
                for i,ep in enumerate(episodes):
                    href = ep.xpath('a/@href')[0]
                    epname = ep.xpath('a/text()')[0]
                    try:
                        epdate = ep.xpath('span/text()')[0].strip()
                    except:
                        epdate = "N/A"
                    if i is 0:
                        self.loaded["last_updated"] = epdate
                    epnum = href.split('/')[5].strip()
                    lines.append(Back.BLUE + '['+epnum+']  ' + epname + ' (' + Fore.BLACK + epdate + Fore.RESET + ')' + Back.RESET)
        except:
            pass
        return [lines,success]

    #load episode in mpv
    def loadEpisode(self,ui=1):
        try:
            ui = int(ui)
            if isinstance(ui,int):
                self.episode = str(ui).zfill(3)
                print(Back.GREEN + 'Loading '+ self.loaded["real_nicename"] +' '+ self.episode + '.MP4')
                err = os.system('mpv "http://animejoy.tv/video/' + self.loaded["id"] + '/'+ self.episode +'.mp4"')
                if err is not 0:
                    err = os.system('mpv "http://animejoy.tv/video/' + self.loaded["real_id"] + '/'+ self.episode +'.mp4"')
        except:
            print(Fore.RED + 'ERROR Episode # is string' + Fore.RESET)

    #get bookmarks
    def loadBookmarks(self):
        with open(SAVE_FILE,'r') as f:
            f = f.read()
            if f is None or f is '':
                f = '[]'
            data = json.loads(f)
            if isinstance(data,list):
                return data
            else: return []

    #get bookmarks
    def listBookmarks(self):
        with open(SAVE_FILE,'r') as f:
            f = f.read()
            if f is None or f is '':
                f = '[]'
            data = json.loads(f)
            if isinstance(data,list):
                print(Fore.YELLOW + "=== BOOKMARKED ANIME ===" + Fore.RESET)
                for i,d in enumerate(data):
                    print(Fore.BLUE + '[' + d["slug"] + '] :: ' + d["show"]["real_nicename"] + ' :: Episode '+str(d["episode"])+' :: ' + d["id"])
                print(Fore.RESET)

    #bookmark for later
    def bookmark(self,slug=None,episode=None,showdata=None):
        success = False
        if showdata is not None:
            with open(SAVE_FILE,'r+') as ff:
                filedata = ff.read()
                if filedata is None or filedata is '':
                    filedata = '[]'
                data = json.loads(filedata)
                fail = False
                if isinstance(data,list):
                    for d in data:
                        if showdata["id"] is d["id"]:
                            fail = True
                            print(Fore.RED + 'Bookmark already exists for ' + showdata["id"])
                    if fail is False:
                        with open(SAVE_FILE,'w+') as f:
                            data.append({"id": showdata["id"], "slug": slug, "episode": episode, "show": showdata})
                            f.write(json.dumps(data))
        return success

def main():
    # Script startup
    os.system('clear')
    err = os.system('figlet -c "KISSANIME IS BACK"')

    # Anime scraping agent
    anime = WAnime()

    # User input
    ui = None
    ui_prev = None

    # Lines list, to print to stdout
    lines = []
    step = 0

    while True:
        #print('DEBUG>> ',anime.loaded)
        if ui is None:
            print(Fore.BLUE + 'Search for anime' + Fore.RESET)
        else:
            if '/' in ui:
                if ui == '/s' or '/s ' in ui:
                    step = 0
                    ui = input('search>>>')
                    continue
                elif '/b' in ui:
                    step = step - 1
                    if step < 1:
                        step = 0
                        ui = None
                        print('Going back')
                        continue
                elif '/clear' in ui:
                    os.system('clear')
                    if step < 1:
                        ui = None
                elif ('/q' in ui or '\\q' in ui):
                    exit()
                elif '/ls' in ui:
                    anime.listBookmarks()
                elif '/load' in ui:
                    props = ui.split('/load')[1]
                    segs = props.split(' ')
                    if len(segs) > 1:
                        slug = segs[1]
                        print(slug)
                    else:
                        bookmarks = anime.loadBookmarks()
                        anime.listBookmarks()
                        slug = input('load>>>')
                        selection = -1
                        for i,b in enumerate(bookmarks):
                            if slug in b["slug"]:
                                selection = i
                        print(selection)
                        anime.loaded = bookmarks[selection]["show"]
                        print(anime.loaded)
                        res = anime.loadShow(None, None)
                        if res[1]:
                            lines = res[0]
                            print(Back.BLUE)
                            [print(x) for x in res[0]]
                            print(Back.RESET)
                            step = 2
                            ui = ''
                            continue
                elif '/save' in ui:
                    if anime.loaded is not {}:
                        if "id" in anime.loaded:
                            props = ui.split('/save')[1]
                            segs = props.split(' ')
                            if len(segs) > 2:
                                segs[2] = int(segs[2])
                                print(segs[2])
                                #saving a slug and an episode
                                print(segs[1],segs[2],anime.loaded)
                                if anime.bookmark(segs[1],segs[2],anime.loaded):
                                    print(Fore.BLUE + 'SAVED BOOKMARK')
                            else:
                                print(Fore.RED + 'Needs two arguments [slug-name] [episode #] ' + Fore.RESET)
                        else:
                            print(Fore.RED + 'Anime episode list must be loaded before you can set a bookmark' + Fore.RESET)
                    else:
                        print(Fore.RED + 'Anime episode list must be loaded before you can set a bookmark' + Fore.RESET)
                ui = ''
                continue
            elif ui is '':
                pass
            else:
                if step is 0:
                    res = anime.searchShows(ui)
                    if res[1]:
                        lines = res[0]
                        print(Back.BLUE)
                        [print(x) for x in res[0]]
                        print(Back.RESET)
                        print(Fore.BLUE + 'Select a result [id]:' + Fore.RESET)
                        step = 1
                    else:
                        print(Fore.RED + 'ERROR Searching '+ ui + Fore.RESET)
                        step = step - 1
                        if step < 0:
                            step = 0
                        ui = ''
                        continue
                elif step is 1:
                    res = anime.loadShow(ui)
                    if res[1]:
                        lines = res[0]
                        print(Back.BLUE)
                        [print(x) for x in res[0]]
                        print(Back.RESET)
                        step = 2
                    else:
                        preview = ''
                        print(Fore.RED + 'ERROR Opening '+ preview + Fore.RESET)
                        step = step - 1
                        if step < 0:
                            step = 0
                        ui = ''
                        continue
                elif step is 2:
                    anime.loadEpisode(ui)
                    [print(x) for x in lines]
        ui = input('>>')
        ui_prev = ui

if __name__ == '__main__':
    main()

