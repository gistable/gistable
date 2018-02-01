#!/usr/bin/env python
# encoding: utf-8
"""
movie_recommender.py

Created by Thomas Cabrol on 2012-04-06.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import csv
import operator
from math import sqrt, pow
from operator import itemgetter
from itertools import combinations
from collections import namedtuple, defaultdict


def movie_name():
	lookup = defaultdict()
	for line in open('/Users/thomas/Documents/data/datasets/movielens/ml-100k/u.item'):
	    record = line.strip().split('|')
	    movie_id, movie_name = record[0], record[1]
	    lookup[movie_id] = movie_name
	return lookup
	
def ratings():
    '''
    Iterate the source file using a generator
    '''
    MovieRating = namedtuple('MovieRating', 'user_id, movie_id, rating, timestamp')
    for record in map(MovieRating._make, csv.reader(open('/Users/thomas/Documents/data/datasets/movielens/ml-100k/u.data', 'rb'), delimiter='\t')):
        yield record
        # MovieRating(user_id='196', movie_id='242', rating='3', timestamp='881250949')
        
def users_ratings():
    '''
    Grouping the ratings per user, used as an input
    before generating the corated movie pairs
    '''
    u = defaultdict(dict)
    for line in ratings():
        u[line.user_id][line.movie_id] = int(line.rating)
    
    users = defaultdict(dict)
    for k, v in u.iteritems():
        users[k] = sorted(v.items())
    return users
    # {941: {1: 5, 258: 4, 7: 4, 15: 4, 273: 3, 147: 4, 919: 5, 408: 5, 294: 4, 298: 5, ...}}
    
def coratings():
    '''
    For each user, create the pair of corated movies using combination,
    then accumulate the base data used for the correlation coeff. by
    pair
    Returns a dict with each pair and its data
    '''
    coratings = defaultdict(dict)
    for user, ratings in users_ratings().iteritems():
        for pair in [zip(*corating) for corating in combinations(ratings, 2)]:
            #941 [[(1, 258), (5, 4)], [(1, 7), (5, 4)], [(1, 15), (5, 4)], [(1, 273), (5, 3)], ....
            movie_pair = pair[0]
            rating_pair = pair[1]
            if movie_pair not in coratings:
                coratings[movie_pair] = defaultdict(float)
            coratings[movie_pair]['N'] += 1.0
            coratings[movie_pair]['ratingSum'] += rating_pair[0]
            coratings[movie_pair]['rating2Sum'] += rating_pair[1]
            coratings[movie_pair]['ratingSqSum'] += pow(rating_pair[0], 2)
            coratings[movie_pair]['rating2SqSum'] += pow(rating_pair[1], 2)
            coratings[movie_pair]['dotProductSum'] += rating_pair[0] * rating_pair[1]       
    return coratings
    
def recommendations(minimum_coratings=30):
    '''
    Actually builds the dict with the correlation coeff. for each pair of movies, 
    given that there is a sufficient number of coratings
    '''
    rec = defaultdict(dict)
    for corating, data in coratings().iteritems():
        movie_1 = corating[0]
        movie_2 = corating[1]
        if data['N'] >= minimum_coratings:
            num = data['N'] * data['dotProductSum'] - data['ratingSum'] * data['rating2Sum']
            den = sqrt(data['N'] * data['ratingSqSum'] - data['ratingSum'] * data['ratingSum']) * sqrt(data['N'] * data['rating2SqSum'] - data['rating2Sum'] * data['rating2Sum'])
            rec[movie_1][movie_2] = num/den
            rec[movie_2][movie_1] = num/den
    return rec
    
def show_recommendations(top_n=10):
    '''
    Print the top n recommendations for each movie
    '''
    lu = movie_name()
    for movie, correlations in recommendations().iteritems():
        #print movie, [e for i, e in enumerate(sorted(correlations.items(), key=itemgetter(1), reverse=True)) if i <= top_n-1]
        for i, related_movies in enumerate(sorted(correlations.items(), key=itemgetter(1), reverse=True)):
            if i == top_n:
                print
                break
            print movie, lu[movie], i+1, related_movies[0], lu[related_movies[0]], related_movies[1]
            

if __name__ == '__main__':
    show_recommendations()