#!/usr/bin/python3

# Import all the things (we need)

from datetime   import timedelta
from datetime   import date

from requests   import Session
from wand.image import Image

import time
import os.path

# Initialize the downloader session

r = Session()

# Define all the functions (again, those we need)

def get_single_strip(strip_date):

	# This function downloads a single strip for the given date, and saves it to a file.
	# We'll begin by setting the filename in which to save our file. We'll follow the
	# format "Dilbert-YYYY-MM-DD.png"

	save_as = "Dilbert-%04d-%02d-%02d.png" % (strip_date.year, strip_date.month, strip_date.day)
	save_as = os.path.join(str(strip_date.year), save_as)

	# At this point, we might as well go ahead and check if we have the file, and if we do,
	# not waste time in downloading it again

	if os.path.isfile(save_as):
		print("%s - Already Have" % save_as)
		return 2

	# Create the directory for the year if it does not exist

	if not os.path.exists(str(strip_date.year)):
		os.makedirs(str(strip_date.year))

	# The URL to access the webpage which holds the strip for the required date is
	# http://dilbert.com/fast/YYYY-MM-DD, so we'll also build that into a variable

	source_page_url = "http://dilbert.com/fast/%04d-%02d-%02d" % (strip_date.year, strip_date.month, strip_date.day)

	# Let's start by actually downloading that page.

	source_page = r.get(source_page_url)
	if not source_page.ok:
		return 0

	# Now we have to do a bit of text processing. It appears that the URL to the actual image is in a
	# string that starts with the letters "dyn/". It also appears that the URL generally starts around
	# the 1000th character or so in the page. Armed with that information, we can try to find the URL
	# to the image, extract it, and download it

	start_pos = source_page.text.find("dyn/", 1000)
	if (start_pos == -1):
		return 0
	end_pos = source_page.text.find("gif", start_pos)

	# It turns out that sometimes, we might get a placeholder image instead of a real strip.
	# The URL to the placeholder is always "dyn/str_strip/default_th.gif". Our text processing
	# has only grabbed the "dyn/str_strip/default_th." part, whose length is 25 characters. We
	# can check our URL length, and if it's 25 characters, give up. This will never turn up a
	# false positive, because URLs to real strips are really long

	if source_page.text[start_pos:end_pos].__len__() == 25:
		return 0

	# Now we'll construct the URL string

	strip_url = "".join(("http://dilbert.com/", source_page.text[start_pos:end_pos], "gif"))

	# Now that we have the URL, why not download it? We'll download it, but not save it. We'll
	# keep it in memory until we convert it to a PNG, and we'll dump the converted PNG to disk

	gif_image = r.get(strip_url)
	if not gif_image.ok:
		return 0

	# We'll now do the conversion to PNG and write to disk in one step

	with Image(blob = gif_image.content, format = "gif") as img:
		img.format = "png"
		img.save(filename = save_as)

	# This was successful, so return True

	print("%s - Downloaded" % save_as)
	return 1

def sync_strips():

	# The first Dilbert comic was released on 17th April 1989. Ah, those innocent days...

	start_date = date(1989, 4, 17)

	# We want all the Dilbert, so the end date is today

	end_date = date.today()

	# And how many days is that?

	total_days = int((end_date - start_date).days)

	# We're ready to start downloading all the Dilbert, so...

	failed_files_log = open("failed.txt", "w")

	for single_date in ((start_date + timedelta(n)) for n in range(total_days + 1)):
		ret = get_single_strip(single_date)
		if not ret:
			failed_files_log.write("".join((str(single_date), "\n")))
			failed_files_log.flush()
		elif ret == 1:
			time.sleep(0.75)

	failed_files_log.close()

	# Yeah, we're sleeping for 0.75 seconds before downloading the next strip to stop being
	# blocked by the server. Anyway, we're done

if __name__ == "__main__":
	sync_strips()
