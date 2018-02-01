"""
You can download the flickr API by running
    pip install flickrapi

Info here:

http://stuvel.eu/media/flickrapi-docs/documentation/2-calling.html


You'll need to create a Flickr API app here:

https://www.flickr.com/services/apps/create/

There's zero guarantee this is reliable. Use at your own risk. The quality of this script is subpar
at best, but it was also written in about five mintues. Please don't judge me. It worked to download
the 8000+ image that NASA had in their account.

"""
import flickrapi
import urllib
import os

API_SECRET = ""
API_KEY = ""

SAVE_LOCATION = os.path.join(os.path.expanduser('~'), 'Dropbox', 'NASA')

flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')

flickr_accounts = {
    'NASA HQ': '35067687@N04',
    'Apollo Archive': '136485307@N06',
}


def download_image(base_path, image):
    full_image_path = os.path.join(base_path, image['title'] + '.jpg')
    if os.path.exists(full_image_path):
        print image['title'], "already exists. Skipping..."
        return
    print "downloading %s..." % image['title']
    sizes = flickr.photos.getSizes(photo_id=image['id'])
    original = None
    for size in sizes['sizes']['size']:
        if size['label'] == 'Original':
            original = size['source']
    if original:
        urllib.URLopener().retrieve(original, full_image_path)
    else:
        print "skipping", image


def download_images(base_path, images):
    for image in images:
        download_image(base_path, image)


def create_folder(filepath):
    if not os.path.exists(filepath):
        print "created folder", filepath
        os.mkdir(filepath)
    return filepath


def get_all_photos(photoset_id, page=1):
    to_ret = []
    list_photos = flickr.photosets.getPhotos(photoset_id=photoset_id, per_page=500, page=page)
    to_ret.extend(list_photos['photoset']['photo'])
    num_pages = int(list_photos['photoset']['pages'])
    page = int(list_photos['photoset']['page']) + 1
    while page <= num_pages:
        print "Getting page", page
        return to_ret + get_all_photos(photoset_id, page)
    return to_ret


def main():
    for account_name, account_id in flickr_accounts.iteritems():
        create_folder(os.path.join(SAVE_LOCATION, account_name))
        print "Grabbing photos for %s" % account_name
        photo_sets = flickr.photosets.getList(user_id=account_id, per_page=500)
        for photoset in photo_sets['photosets']['photoset']:
            photoset_title = photoset['title'].get('_content').replace('/', '.')
            base_path = create_folder(os.path.join(SAVE_LOCATION, account_name, photoset_title))
            list_photos = get_all_photos(photoset['id'])
            download_images(base_path, list_photos)


if __name__ == '__main__':
    main()
