# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
#
#       Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16
#
#                         *** Use at your own risk! ***
#   *** I am not responsible for damages to your Plex server or libraries. ***
#
#------------------------------------------------------------------------------

import json
import requests
import time
from lxml import html
from plexapi.server import PlexServer

### Plex server details ###
PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'xxxxxxxxxx'

### Existing movie library details ###
MOVIE_LIBRARY_NAME = 'Movies'

### New IMDB Top 250 library details ###
IMDB_CHART_URL = 'http://www.imdb.com/chart/top'
IMDB_COLLECTION_NAME = 'IMDB Top 250'

### The Movie Database details ###
# Enter your TMDb API key if your movie library is using "The Movie Database" agent.
# This will be used to convert the TMDb IDs to IMDB IDs.
# You can leave this blank '' if your movie library is using the "Plex Movie" agent.
TMDB_API_KEY = ''


##### CODE BELOW #####

TMDB_REQUEST_COUNT = 0  # DO NOT CHANGE

def add_collection(library_key, rating_key):
    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {"type": 1,
              "id": rating_key,
              "collection[0].tag.tag": IMDB_COLLECTION_NAME,
              "collection.locked": 1
              }

    url = "{base_url}/library/sections/{library}/all".format(base_url=PLEX_URL, library=library_key)
    r = requests.put(url, headers=headers, params=params)

    
def get_imdb_id_from_tmdb(tmdb_id):
    global TMDB_REQUEST_COUNT
    
    if not TMDB_API_KEY:
        return None
    
    # Wait 10 seconds for the TMDb rate limit
    if TMDB_REQUEST_COUNT >= 40:
        time.sleep(10)
        TMDB_REQUEST_COUNT = 0
    
    params = {"api_key": TMDB_API_KEY}
    
    url = "https://api.themoviedb.org/3/movie/{tmdb_id}".format(tmdb_id=tmdb_id)
    r = requests.get(url, params=params)
    
    TMDB_REQUEST_COUNT += 1
    
    if r.status_code == 200:
        movie = json.loads(r.text)
        return movie['imdb_id']
    else:
        return None
    
    
def run_imdb_top_250():
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except:
        print("No Plex server found at: {base_url}".format(base_url=PLEX_URL))
        print("Exiting script.")
        return [], 0

    # Get list of movies from the Plex server
    print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=MOVIE_LIBRARY_NAME))
    try:
        movie_library = plex.library.section(MOVIE_LIBRARY_NAME)
        movie_library_key = movie_library.key
        library_language = movie_library.language
        all_movies = movie_library.all()
    except:
        print("The '{library}' library does not exist in Plex.".format(library=MOVIE_LIBRARY_NAME))
        print("Exiting script.")
        return [], 0

    # Get the IMDB Top 250 list
    print("Retrieving the IMDB Top 250 list...")
    r = requests.get(IMDB_CHART_URL, headers={'Accept-Language': library_language})
    tree = html.fromstring(r.content)
    
    # http://stackoverflow.com/questions/35101944/empty-list-is-returned-from-imdb-using-python-lxml
    top_250_titles = tree.xpath("//table[contains(@class, 'chart')]//td[@class='titleColumn']/a/text()")
    top_250_years = tree.xpath("//table[contains(@class, 'chart')]//td[@class='titleColumn']/span/text()")
    top_250_ids = tree.xpath("//table[contains(@class, 'chart')]//td[@class='ratingColumn']/div//@data-titleid")

    # Create a dictionary of {imdb_id: movie}
    imdb_map = {}
    for m in all_movies:
        if 'imdb://' in m.guid:
            imdb_id = m.guid.split('imdb://')[1].split('?')[0]
        elif 'themoviedb://' in m.guid:
            tmdb_id = m.guid.split('themoviedb://')[1].split('?')[0]
            imdb_id = get_imdb_id_from_tmdb(tmdb_id)
        else:
            imdb_id = None
            
        if imdb_id and imdb_id in top_250_ids:
            imdb_map[imdb_id] = m
        else:
            imdb_map[m.ratingKey] = m

    # Modify the sort title to match the IMDB Top 250 order
    print("Setting the collection for the '{}' library...".format(MOVIE_LIBRARY_NAME))
    in_library_idx = []
    for i, imdb_id in enumerate(top_250_ids):
        movie = imdb_map.pop(imdb_id, None)
        if movie:
            add_collection(movie_library_key, movie.ratingKey)
            in_library_idx.append(i)
            
    # Get list of missing IMDB Top 250 movies
    missing_imdb_250 = [(idx, imdb) for idx, imdb in enumerate(zip(top_250_ids, top_250_titles, top_250_years))
                        if idx not in in_library_idx]

    return missing_imdb_250, len(top_250_ids)
    
        
if __name__ == "__main__":
    print("===================================================================")
    print(" Automated IMDB Top 250 Plex collection script by /u/SwiftPanda16  ")
    print("===================================================================\n")

    missing_imdb_250, list_count = run_imdb_top_250()
    
    print("\n===================================================================\n")
    print("Number of IMDB Top 250 movies in the library: {count}".format(count=list_count-len(missing_imdb_250)))
    print("Number of missing IMDB Top 250 movies: {count}".format(count=len(missing_imdb_250)))
    print("\nList of missing IMDB Top 250 movies:\n")
    
    for idx, (imdb_id, title, year) in missing_imdb_250:
        print("{idx}\t{imdb_id}\t{title} {year}".format(idx=idx+1, imdb_id=imdb_id, title=title.encode('UTF-8'), year=year))
    
    print("\n===================================================================")
    print("                               Done!                               ")
    print("===================================================================\n")
    
    raw_input("Press Enter to finish...")