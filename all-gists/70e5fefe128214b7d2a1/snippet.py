from __future__ import print_function

import sys
from math import sqrt
import argparse
from collections import defaultdict
from random import randint

from pyspark import SparkContext

def parseArguments(args):
    parser = argparse.ArgumentParser(add_help=True,
                                     description='Item similarity - " + \
                                     "naive k-nn approximation')
    parser.add_argument('--debug', action="store_true",
                        dest="debug", default=False,
                        help="Debug flag",
                        required=False)

    parser.add_argument('--num_reco', action="store",
                        dest="num_reco", default=10,
                        help="Number of recommendations per user", type=int,
                        required=False)

    parser.add_argument('--repartition', action="store",
                        dest="repartition", default=10,
                        help="Number of repartition", type=int,
                        required=False)

    parser.add_argument('--repetition', action="store",
                        dest="repetition", default=10,
                        help="Number of repetition", type=int,
                        required=False)

    parser.add_argument('--app', action="store",
                        dest="app",
                        help="App name (spark context)",
                        required=False, default="rec_streaming")

    parser.add_argument('--input', action="store",
                        dest="input",
                        help="Input location",
                        required=True)

    arguments = parser.parse_args()
    return arguments


def load_item(item):
    item_data = item.split(",")
    item_id = item_data[0]
    item_vec = [float(s) for s in item_data[1:]]
    item_len = sqrt(sum([a*a for a in item_vec]))
    return (item_id, (item_vec, item_len))


def distance(item1, item2):
    item1_id, (item1_ftrs, item1_len) = item1
    item2_id, (item2_ftrs, item2_len) = item2
    distance = sum([a * b for a, b in zip(item1_ftrs, item2_ftrs)])
    return distance/(item1_len * item2_len)

def approx_distance_user(user_iter, num_reco):
    users = list(user_iter)
    users_dict = defaultdict(dict)
    for idx1, user1 in enumerate(users):
        for user2 in users[idx1+1:]:
            dist = distance(user1, user2)
            users_dict[user1[0]][user2[0]] = dist
            users_dict[user2[0]][user1[0]] = dist
    users_dict = {k : sorted(v.items(), key = lambda a: -a[1])[:num_reco]
                             for k,v in users_dict.iteritems()}
    return users_dict.items()


def main(args):
    arguments = parseArguments(args)
    if arguments.debug:
        sys.stdout.write("Arguments: %s\n"%arguments)
    sc = SparkContext(appName=arguments.app)
    items = sc.textFile(arguments.input)
    items = items.map(lambda x: load_item(x)).cache()
    distances = sc.emptyRDD()
    for i in xrange(0, arguments.repetition):
        curr_distances = items.repartitionAndSortWithinPartitions(\
                          arguments.repartition, \
                          lambda x: randint(1, arguments.repartition)).\
                          mapPartitions(lambda x:
                          approx_distance_user(x, arguments.num_reco))
        distances = distances.union(curr_distances)
    distances = distances.reduceByKey(lambda a, b : a + b)
    distances = distances.map(lambda x: (x[0],
                              sorted(set(x[1]), key = lambda a: -a[1])))
    distances = distances.collect()
    for item_id, rec in distances:
        print ("%s\t%s"%(item_id, rec))


if __name__ == "__main__":
    main(sys.argv[1:])
