import re

"""
di.fm allows you to download a playlist of all your favorite channels. For some
reason when you open this playlist with iTunes only one of the channels is
added. This script splits the playlist file into many playlist files so you can
easily load all of your favorites into iTunes and enjoy di.fm streaming without
running Flash in your browser.
"""
items = open("di.pls").read().split("File")
for item in items:
	title_ = re.compile("Title\d+=(.+)").findall(item)
	if len(title_) != 1:
		continue
	filename = title_[0].strip() + ".pls"
	body = "[playlist]\nNumberOfEntries=1\nFile" + item
	open(filename, mode="w").write(body)