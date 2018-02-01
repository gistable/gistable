#~/usr/bin/env python2
import os
import re
import imdb
import pickle
# TODO: use logger

ia = imdb.IMDb()
# TODO: expand ~/
cache_dir = "/home/bijan/.imdbpy/cache"
movies_path = '/run/media/bijan/Storage/Videos/Movies/'
casts_path = '/run/media/bijan/Storage/Videos/MoviesSorted/casts/'
directors_path = '/run/media/bijan/Storage/Videos/MoviesSorted/directors/'
genres_path = '/run/media/bijan/Storage/Videos/MoviesSorted/genres/'

if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
if not os.path.exists(movies_path):
    os.makedirs(movies_path)
if not os.path.exists(casts_path):
    os.makedirs(casts_path)
if not os.path.exists(directors_path):
    os.makedirs(directors_path)
if not os.path.exists(genres_path):
    os.makedirs(genres_path)

# TODO: list only files, not symlinks, better to set criteria for ext (RECURSIVELY).
movies = os.listdir(movies_path)
movies_length = len(movies)
for idx, filename in enumerate(movies):
    idx += 1
    filepath = os.path.join(movies_path, filename)
    matched = re.match("(.*) \((.*)\)\..*", filename)
    if matched:
        if os.path.exists(os.path.join(cache_dir, '%s.cache' % filename)):
            print('[%s/%s] Load from cache: %s' % (idx, movies_length, filename))
            with open(os.path.join(cache_dir, '%s.cache' % filename), 'r') as f:
                movie_pickled = f.read()
            movie = pickle.loads(movie_pickled)
        else:
            title, year = re.match("(.*) \((.*)\)\..*", filename).groups()
            year = int(year)
            print('[%s/%s] Searching %s' % (idx, movies_length, filename))
            s_result = ia.search_movie(title)

            movie = None
            for item in s_result:
                if item.data.get('year'):
                    if item.data['year'] == year:
                        movie = item
                        ia.update(movie)
                        break

        if movie:
            # RECORD CACHE
            movie_pickled = pickle.dumps(movie)
            with open(os.path.join(cache_dir, '%s.cache' % filename), 'w') as f:
                f.write(movie_pickled)

            # movie['full-size cover url'], 'rating', 'genres'
            for cast in movie.data['cast'][1:10]:
                cast_name = dict(cast.items())['name']
                cast_path = os.path.join(casts_path, cast_name)
                if not os.path.exists(cast_path):
                    os.mkdir(cast_path)
                symlink = os.path.join(cast_path, filename.decode('utf-8'))
                if not os.path.exists(symlink):
                    os.symlink(filepath, symlink)

            for director in movie.data['director']:
                director_name = dict(cast.items())['name']
                director_path = os.path.join(directors_path, director_name)
                if not os.path.exists(director_path):
                    os.mkdir(director_path)
                symlink = os.path.join(director_path, filename.decode('utf-8'))
                if not os.path.exists(symlink):
                    os.symlink(filepath, symlink)

            for genre_name in movie.data.get('genres', []):
                genre_path = os.path.join(genres_path, genre_name)
                if not os.path.exists(genre_path):
                    os.mkdir(genre_path)
                if not os.path.exists(genre_path):
                    os.mkdir(genre_path)
                symlink = os.path.join(genre_path, filename.decode('utf-8'))
                if not os.path.exists(symlink):
                    os.symlink(filepath, symlink)
        else:
            print('\tMovie Not Found')
