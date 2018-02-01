#!/usr/bin/env python
# coding: utf8

import sys, urllib2, json

def width():
	def ioctl_GWINSZ(fd):
		try:
			import fcntl, termios, struct, os
			cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
		except:
			return
		return cr
	cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
	if not cr:
		try:
			fd = os.open(os.ctermid(), os.O_RDONLY)
			cr = ioctl_GWINSZ(fd)
			os.close(fd)
		except:
			pass
	return int(cr[1]) or 80

def next_link(response):
	link = response.headers.getheader('link')
	if link == None:
		return
	for val in link.split(","):
		url, params = val.split(";", 1)
		for param in params.split(";"):
			key, value = param.split("=")
			extra = " '\""
			key = key.strip(extra)
			value = value.strip(extra)
			if key == "rel" and value == "next":
				return url.strip("<> '\"")

def stars(user, url = None):
	url = 'https://api.github.com/users/' + urllib2.quote(user) + '/repos?type=owner' if url == None else url
	response = urllib2.urlopen(url)
	next = next_link(response)
	repos = json.loads(response.read())
	count = sum([repo['stargazers_count'] for repo in repos])
	return count + stars(user, next) if next else count

def display(counts):
	counts = sorted(counts, key=lambda x: x[1])
	counts.reverse()
	margin = 2
	most_stars = counts[0][1]
	username_length = max([len(username) for (username, count) in counts])
	count_length = max([len(str(count)) for (username, count) in counts])
	bar_length = width() - username_length - count_length - (3 * margin)
	margin *= ' '
	for (username, count) in counts:
		bar = '★ ' * max(1,int((float(count) / most_stars) * bar_length)/2)
		print '\n' + username.ljust(username_length) + margin + bar + margin + str(count)
	print

def main(users):
	if len(users) == 0:
		return
	counts = []
	for user in users:
		counts.append((user, stars(user)))
	display(counts)

if __name__ == '__main__':
	main(sys.argv[1:])
