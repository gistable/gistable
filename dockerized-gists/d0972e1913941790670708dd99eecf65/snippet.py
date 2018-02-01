# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
#
#                 Plex movie ratings script by /u/SwiftPanda16
#
#                         *** Use at your own risk! ***
#   *** I am not responsible for damages to your Plex server or libraries. ***
#
#------------------------------------------------------------------------------

# Requires: plexapi, imdbpie, rotten_tomatoes_client

import re
import sqlite3
from plexapi.server import PlexServer
from imdbpie import Imdb
from rotten_tomatoes_client import RottenTomatoesClient


### EDIT SETTINGS ###

PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'xxxxxxxxxx'
MOVIE_LIBRARY_NAME = 'Movies'
PLEX_DATABASE_FILE = r"C:\Users\John Doe\AppData\Local\Plex Media Server\Plug-in Support\Databases\com.plexapp.plugins.library.db"

RATING_SOURCE = 'imdb'  # imdb or rt (Note: RottenTomato ratings are critic ratings, not audience ratings)
RT_MATCH_YEAR = True  # Match the movie by year on Rotten Tomatoes (True or False)

DRY_RUN = True  # Dry run without modifying the database (True or False)

### Optional: The Movie Database details ###
# Enter your TMDb API key if your movie library is using "The Movie Database" agent.
# This will be used to convert the TMDb IDs to IMDB IDs.
# You can leave this blank '' if your movie library is using the "Plex Movie" agent.
TMDB_API_KEY = ''


##### CODE BELOW #####

TMDB_REQUEST_COUNT = 0  # DO NOT CHANGE


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


def main():
    # Connect to the Plex server
    print("Connecting to the Plex server at '{base_url}'...".format(base_url=PLEX_URL))
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except:
        print("No Plex server found at: {base_url}".format(base_url=PLEX_URL))
        print("Exiting script.")
        return

    # Get list of movies from the Plex server
    print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=MOVIE_LIBRARY_NAME))
    try:
        movie_library = plex.library.section(MOVIE_LIBRARY_NAME)
    except:
        print("The '{library}' library does not exist in Plex.".format(library=MOVIE_LIBRARY_NAME))
        print("Exiting script.")
        return
        
    imdb = Imdb()
    conn_db = sqlite3.connect(PLEX_DATABASE_FILE)
    db = conn_db.cursor()
    
    if RATING_SOURCE == 'imdb':
        print("Using IDMB ratings.")
    elif RATING_SOURCE == 'rt':
        print("Using Rotten Tomatoes critic ratings.")
    else:
        print("Invalid rating source. Must be 'imdb' or 'rt'.")
        print("Exiting script.")
        return
        
    for plex_movie in movie_library.all():
        if 'imdb://' in plex_movie.guid:
            imdb_id = plex_movie.guid.split('imdb://')[1].split('?')[0]
        elif 'themoviedb://' in plex_movie.guid:
            tmdb_id = plex_movie.guid.split('themoviedb://')[1].split('?')[0]
            imdb_id = get_imdb_id_from_tmdb(tmdb_id)
        else:
            imdb_id = None
            
        if not imdb_id:
            print("Missing IMDB ID. Skipping movie '{pm.title}'.".format(pm=plex_movie))
            continue
        
        if RATING_SOURCE == 'imdb':
            if imdb.title_exists(imdb_id):
                imdb_movie = imdb.get_title_by_id(imdb_id)
            else:
                print("Movie not found on IMDB. Skipping movie '{pm.title} ({imdb_id})'.".format(pm=plex_movie, imdb_id=imdb_id))
                continue
                            
            print("{im.rating}\t{pm.title}".format(pm=plex_movie, im=imdb_movie))
        
            if not DRY_RUN:
                db_execute(db, "UPDATE metadata_items SET rating = ? WHERE id = ? AND user_fields NOT LIKE ?",
                           [imdb_movie.rating, plex_movie.ratingKey, '%lockedFields=5%'])
                           
                extra_data = db_execute(db, "SELECT extra_data FROM metadata_items WHERE id = ?", [plex_movie.ratingKey]).fetchone()[0]
                if extra_data:
                    extra_data = re.sub(r"at%3AratingImage=.+?&|at%3AaudienceRatingImage=.+?&", '', extra_data)
                    
                    db_execute(db, "UPDATE metadata_items SET extra_data = ? WHERE id = ?",
                               [extra_data, plex_movie.ratingKey])
                
                db_execute(db, "UPDATE metadata_items SET extra_data = ? || extra_data WHERE id = ?",
                           ['at%3AratingImage=imdb%3A%2F%2Fimage%2Erating&', plex_movie.ratingKey])
            
        elif RATING_SOURCE == 'rt':
            rt_client_result = RottenTomatoesClient.search(term=plex_movie.title, limit=5)
            if RT_MATCH_YEAR:
                rt_movie = next((m for m in rt_client_result['movies'] if m['year'] == plex_movie.year), None)
            else:
                rt_movie = next((m for m in rt_client_result['movies']), None)
            
            if rt_movie is None:
                print("Movie not found on RottenTomatoes. Skipping movie '{pm.title} ({imdb_id})'.".format(pm=plex_movie, imdb_id=imdb_id))
                continue
                
            rt_rating = rt_movie['meterScore'] / 10.0
            tomato = 'ripe' if rt_rating >= 6 else 'rotten'
           
            print("{rt_rating}\t{pm.title}".format(pm=plex_movie, rt_rating=rt_rating))
        
            if not DRY_RUN:
                db_execute(db, "UPDATE metadata_items SET audience_rating = ? WHERE id = ?",
                           [rt_rating, plex_movie.ratingKey])
                           
                extra_data = db_execute(db, "SELECT extra_data FROM metadata_items WHERE id = ?", [plex_movie.ratingKey]).fetchone()[0]
                if extra_data:
                    extra_data = re.sub(r"at%3AratingImage=.+?&|at%3AaudienceRatingImage=.+?&", '', extra_data)
                    
                    db_execute(db, "UPDATE metadata_items SET extra_data = ? WHERE id = ?",
                               [extra_data, plex_movie.ratingKey])
                
                db_execute(db, "UPDATE metadata_items SET extra_data = ? || extra_data WHERE id = ?",
                           ['at%3AaudienceRatingImage=rottentomatoes%3A%2F%2Fimage%2Erating%2E{}&'.format(tomato), plex_movie.ratingKey])
                
    conn_db.commit()
    db.close()

    
def db_execute(db, query, args):
    try:
        db.execute(query, args)
    except sqlite3.OperationalError as e:
        print("Database Error: {}".format(e))
    except sqlite3.DatabaseError as e:
        print("Database Error: {}".format(e))

    return result
            
if __name__ == "__main__":
    main()
    print("Done.")
