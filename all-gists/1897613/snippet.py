from BeautifulSoup import BeautifulSoup
import requests
import os


album_url = "http://imgur.com/a/TYfWa/all/hot/day/page/%d?scrolled"
pages = 3
directory = "heroes"

posts_list = []

for page in range(0, pages):
	r = requests.get(album_url%page)
	soup = BeautifulSoup(r.content)
	posts_list.append([d["href"] for d in soup.find("div", attrs={'class': 'posts'}).findAll("a")])

image_urls = [item for sublist in posts_list for item in sublist]
print "Found %d images."%len(image_urls)
if not os.path.exists(directory):
    os.makedirs(directory)

for url in image_urls:
	filename = url.split("/")[-1]
	print "%s"%filename
	fout = open(os.path.join(directory, filename), "wb")
	fout.write(requests.get(url).raw.read())
	fout.close()