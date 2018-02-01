# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
#
#         Automated IMDB Top 250 Plex library script by /u/SwiftPanda16
#
#                         *** Use at your own risk! ***
#   *** I am not responsible for damages to your Plex server or libraries. ***
#
#------------------------------------------------------------------------------

import json
import os
import requests
import subprocess
import time
from lxml import html
from plexapi.server import PlexServer

### Plex server details ###
PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'xxxxxxxxxx'

### Existing movie library details ###
MOVIE_LIBRARY_NAME = 'Movies'
MOVIE_LIBRARY_FOLDERS = ['/media/Movies']  # List of movie folders in library

### New IMDB Top 250 library details ###
IMDB_CHART_URL = 'http://www.imdb.com/chart/top'
IMDB_LIBRARY_NAME = 'IMDB Top 250'
IMDB_FOLDER = '/media/IMDB Top 250'  # New folder to symlink existing movies to
SORT_TITLE_FORMAT = "{number}. {title}"

### The Movie Database details ###
# Enter your TMDb API key if your movie library is using "The Movie Database" agent.
# This will be used to convert the TMDb IDs to IMDB IDs.
# You can leave this blank '' if your movie library is using the "Plex Movie" agent.
TMDB_API_KEY = ''

##### CODE BELOW #####

TMDB_REQUEST_COUNT = 0  # DO NOT CHANGE

def create_imdb_library():
    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {"name": IMDB_LIBRARY_NAME,
              "type": 'movie',
              "agent": 'com.plexapp.agents.imdb',
              "scanner": 'Plex Movie Scanner',
              "language": 'en',
              "location": IMDB_FOLDER
              }

    url = "{base_url}/library/sections".format(base_url=PLEX_URL)
    r = requests.post(url, headers=headers, params=params)

        
def add_sort_title(library_key, rating_key, number, title):
    headers = {"X-Plex-Token": PLEX_TOKEN}
    params = {"type": 1,
              "id": rating_key,
              "title.value": SORT_TITLE_FORMAT.format(number=number, title=title),
              "title.locked": 1,
              "titleSort.value": SORT_TITLE_FORMAT.format(number=str(number).zfill(3), title=title),
              "titleSort.locked": 1
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

    # Create a list of matching movies
    matching_movies = []
    for m in all_movies:
        if 'imdb://' in m.guid:
            imdb_id = m.guid.split('imdb://')[1].split('?')[0]
        elif 'themoviedb://' in m.guid:
            tmdb_id = m.guid.split('themoviedb://')[1].split('?')[0]
            imdb_id = get_imdb_id_from_tmdb(tmdb_id)
        else:
            imdb_id = None
            
        if imdb_id and imdb_id in top_250_ids:
            matching_movies.append(m)

    # Create symlinks for all movies in your library on the IMDB Top 250
    print("Creating symlinks for matching movies in the library...")

    try:
        if not os.path.exists(IMDB_FOLDER):
            os.mkdir(IMDB_FOLDER)
    except:
        print("Unable to create the IMDB folder '{folder}'.".format(folder=IMDB_FOLDER))
        print("Exiting script.")
        return [], 0

    count = 0
    for movie in matching_movies:
        for part in movie.iterParts():
            old_path_file = part.file.encode('UTF-8')
            old_path, file_name = os.path.split(old_path_file)

            folder_name = ''
            for f in MOVIE_LIBRARY_FOLDERS:
                if old_path.lower().startswith(f.lower()):
                    folder_name = os.path.relpath(old_path, f)
            
            if folder_name == '.':
                new_path = os.path.join(IMDB_FOLDER, file_name)
                dir = False
            else:
                new_path = os.path.join(IMDB_FOLDER, folder_name)
                dir = True
            
            if (dir and not os.path.exists(new_path)) or (not dir and not os.path.isfile(new_path)):
                try:
                    if os.name == 'nt':
                        if dir:
                            subprocess.call(['mklink', '/D', new_path, old_path], shell=True)
                        else:
                            subprocess.call(['mklink', new_path, old_path_file], shell=True)
                    else:
                        if dir:
                            os.symlink(old_path, new_path)
                        else:
                            os.symlink(old_path_file, new_path)
                    count += 1
                except Exception as e:
                    print("Symlink failed for {path}: {e}".format(path=new_path, e=e))
                    
    print("Created symlinks for {count} movies.".format(count=count))
                    
    # Check if the IMDB Top 250 library exists in Plex
    print("Creating the '{}' library in Plex...".format(IMDB_LIBRARY_NAME))
    try:
        imdb_library = plex.library.section(IMDB_LIBRARY_NAME)
        imdb_library_key = imdb_library.key
        print("Library already exists in Plex. Refreshing the library...")
        
        imdb_library.refresh()
    except:
        create_imdb_library()
        imdb_library = plex.library.section(IMDB_LIBRARY_NAME)
        imdb_library_key = imdb_library.key

    # Wait for metadata to finish downloading before continuing
    raw_input("\n**Please wait until all metadata has finished downloading "
          "before continuing!**\nPress Enter to continue...\n")

    # Retrieve a list of movies from the IMDB Top 250 library
    print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=IMDB_LIBRARY_NAME))
    all_imdb_movies = imdb_library.all()

    # Create a dictionary of {imdb_id: movie}
    imdb_map = {}
    for m in all_imdb_movies:
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
    print("Setting the sort titles for the '{}' library...".format(IMDB_LIBRARY_NAME))
    in_library_idx = []
    for i, (imdb_id, imdb_title) in enumerate(zip(top_250_ids, top_250_titles)):
        movie = imdb_map.pop(imdb_id, None)
        if movie:
            add_sort_title(imdb_library_key, movie.ratingKey, i+1, imdb_title.encode('UTF-8'))
            in_library_idx.append(i)
            
    # Remove movies from library with are no longer on the IMDB Top 250 list
    print("Removing symlinks for movies which are not on the IMDB Top 250 list...".format(library=IMDB_LIBRARY_NAME))
    count = 0
    for movie in imdb_map.values():
        for part in movie.iterParts():
            old_path_file = part.file.encode('UTF-8')
            old_path, file_name = os.path.split(old_path_file)
    
            folder_name = os.path.relpath(old_path, IMDB_FOLDER)
            
            if folder_name == '.':
                new_path = os.path.join(IMDB_FOLDER, file_name)
                dir = False
            else:
                new_path = os.path.join(IMDB_FOLDER, folder_name)
                dir = True

            if (dir and os.path.exists(new_path)) or (not dir and os.path.isfile(new_path)):
                try:
                    if os.name == 'nt':
                        if dir:
                            os.rmdir(new_path)
                        else:
                            os.remove(new_path)
                    else:
                        os.unlink(new_path)
                    count += 1
                except Exception as e:
                    print("Remove symlink failed for {path}: {e}".format(path=new_path, e=e))
                    
    print("Removed symlinks for {count} movies.".format(count=count))
                    
    # Refresh the library to remove the movies
    print("Refreshing the '{library}' library...".format(library=IMDB_LIBRARY_NAME))
    imdb_library.refresh()
    
    # Get list of missing IMDB Top 250 movies
    missing_imdb_250 = [(idx, imdb) for idx, imdb in enumerate(zip(top_250_ids, top_250_titles, top_250_years))
                        if idx not in in_library_idx]

    return missing_imdb_250, len(top_250_ids)
    
        
if __name__ == "__main__":
    print("===================================================================")
    print("   Automated IMDB Top 250 Plex library script by /u/SwiftPanda16   ")
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