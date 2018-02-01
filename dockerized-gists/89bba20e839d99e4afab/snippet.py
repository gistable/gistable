import pytumblr
import os
import code
import oauth2 as oauth
from pprint import pprint
import json
import urllib
import codecs

# Number of likes to fetch in one request
limit = 20

# Directory where to save the images
directory = "tumblr-likes"

# List of ident downloaded
downloaded = []

try:

  # Authenticate via OAuth
  client = pytumblr.TumblrRestClient(
  'CONSUMER_KEY',
  'CONSUMER_SECRET',
  'OAUTH_TOKEN',
  'OAUTH_TOKEN_SECRET'
  )

  # Get the info on the user
  info = client.info()

  # Get the content
  name = info["user"]["name"]
  number = int(info["user"]["likes"])

  # Currently the Tumblr API returns no more than 1000 likes
  pages = min(number // limit, 50)

  # Display the number of likes and pages of 20
  print "Tumblr user {0} has {1} likes".format(name, number)
  print "{0} pages will be fetched".format(pages)

  posts = 0
  total = 0
  for page in xrange(0, pages):

    # For testing
    #if page == 1:
    #  break

    # Get the likes
    offset = page * limit
    likes = client.likes(offset=offset, limit=limit)["liked_posts"]

    # Parse the likes
    for liked in likes:

      # Only the photos
      if "photos" in liked:

        downloaded.append([liked["id"], liked["reblog_key"]])
        photos = liked["photos"]
        count = 0

        # Parse photos
        for photo in photos:

          # Get the original size
          url = photo["original_size"]["url"]
          imgname = url.split('/')[-1]

          # Store in a directory based on blog name
          blog_dir = directory + "/" + liked["blog_name"]
          if not os.path.isdir(blog_dir):
            os.mkdir(blog_dir)

          # Create a unique name
          filename = blog_dir + "/" + str(liked["id"]) + "-"

          # Add numbers if more than one image
          if count > 0:
            filename += str(count) + "-"
          filename += imgname

          # Check if image is already on local disk
          if (os.path.isfile(filename)):
            print "File already exists : " + imgname
          else:
            print "Downloading " + imgname + " from " + liked["blog_name"]
            urllib.urlretrieve(url, filename)
            count += 1
        posts += 1
        total += count
      elif "video_url" in liked:

        # Get the video name
        url = liked["video_url"]
        vidname = url.split('/')[-1]
        count = 0

        # Create a unique name
        filename = directory + "/" + liked["blog_name"] + "-" + str(liked["id"]) + "-" + vidname

        # Check if video is already on local disk
        if (os.path.isfile(filename)):
          print "File already exists : " + vidname
        else:
          print "Downloading " + vidname + " from " + liked["blog_name"]
          urllib.urlretrieve(url, filename)
          count += 1
        posts += 1
        total += count

      elif "body" in liked:

        # Create a unique name
        filename = directory + "/" + liked["blog_name"] + "-" + str(liked["id"]) + ".htm"

        with codecs.open(filename, "w", "utf-8") as ds:
          ds.write('<!doctype html><html><head><meta http-equiv="content-type" content="text/html; charset=utf-8"><title></title></head><body>')
          ds.write(liked["body"])
          ds.write('</body></html>')

      else:

        # If not a photo or a video, dump the JSON
        with open(str(liked["id"]) + "-" + str(liked["blog_name"]) + ".json", "w") as f:
          json.dump(liked, f)

  with open("downloaded.json", "w") as f:
    json.dump(downloaded, f)

  # Display some stats
  print "Total posts parsed : " + str(posts)
  print "Total images or videos downloaded : " + str(total)

except:
  print "Unexpected error:", sys.exc_info()[0]
  raw_input("Press Enter to close window...")

