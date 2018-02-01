#! python3
"""
feedingtube.py: Fetch hella images for training image classifiers
Usage: python3 feedingtube.py <flavor>
        - downloads photos tagged w/<flavor>
"""
import flickrapi
import json
import os
import urllib

# Return authorized flickrapi access object
def initialize_feedingtube(key, secret):
    return flickrapi.FlickrAPI(key, secret, format="parsed-json")

# Change working directory to slopbucket for flavor
# Create one if it does not exist
def find_slopbucket(path):
    if not os.path.exists(path):
        print("Creating fresh slopbucket", path)
        os.mkdir(path)
    os.chdir(path)

# Return Flickr photos w/tag=flavor as JSON
def fetch_slops(flavor, page=1):
    print("Fetching page %s of %s slops..." % (page, flavor))
    silo = FLICKR.photos.search(tags=flavor, per_page=500, page=page)
    slops = silo['photos']['photo']
    return slops

# Loop through Flickr photos, find best sourceURL, download to slopbucket
def fill_slopbucket(slops):
    print("Filling slopbucket...")
    for slop in slops:
        options = FLICKR.photos.getSizes(photo_id=slop['id'])
        best_option = None
        for option in options['sizes']['size']:
            best_option = option['source']
            if option['label'] == 'Original':
                break
        if best_option:
            name = ''.join(e for e in slop['title'] if e.isalnum()) + slop['id'] + '.jpg'
            if os.path.exists(os.path.join(PATH, name)):
                print("No overfeeding, skipping duplicate slop", name)
            print("Scraping slop", name)
            urllib.request.urlretrieve(best_option, os.path.join(PATH, name))
            print("Finished scraping slop", name)
        else:
            print("Skipping phantom slops...")

# All the slops
def scoop_and_scrape(flavor, bucketnum=1):
    print("Scooping and scraping bucket %s of %s" % (bucketnum, flavor))
    slops = fetch_slops(flavor, bucketnum)
    fill_slopbucket(slops)

# How many buckets of slop are we going through?
def get_num_buckets(flavor):
    silo = FLICKR.photos.search(tags=flavor, per_page=500, page=1)
    num_buckets = silo['photos']['pages']
    print("%s buckets of %s to go through" % (num_buckets, flavor))
    return num_buckets


# Main
if __name__ == "__main__":
    import sys
    FLAVOR = sys.argv[1]
    API_KEY = os.environ['FLICKR_API_KEY']
    API_SECRET = os.environ['FLICKR_API_SECRET']
    FLICKR = initialize_feedingtube(API_KEY, API_SECRET)
    PATH = os.path.join(os.path.expanduser("~"),
        "Development",
        "Python",
        "Farm",
        "slopbuckets",
        FLAVOR)
    i = 1
    find_slopbucket(PATH)
    num_buckets = get_num_buckets(FLAVOR)
    while i <= num_buckets:
        scoop_and_scrape(FLAVOR, i)
        i += 1
    print("Success! Slops ready.")
