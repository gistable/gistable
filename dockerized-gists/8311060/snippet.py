import requests

uf = False # Unfollow all (currently followed) users?
f  = True  # Follow all (currently unfollowed) users?

def url(path, page=1, auth=""):
	return "https://api.github.com" + path + "?page=" + str(page) + "&access_token=" + auth

def unfollow(user):
	requests.delete(url("/user/following/" + user["login"], 1, auth))
	print "** Now not following " + user["login"]

def follow(user):
	requests.put(url("/user/following/" + user["login"], 1, auth))
	print "** Now following " + user["login"]

def beCreepy(user):
	try:
		if len(requests.get(url("/users/" + uname + "/following/" + user["login"], 1, auth)).text) > 0:
			raise Exception("Not following " + user["login"] + "!")
		else:
			print "Already following " + user["login"]
			if uf:
				unfollow(user)
	except:
		print "Not following " + user["login"]
		if f:
			follow(user)

uname = raw_input("Please input your username\n>> ")
sname = raw_input("Please Enter desired username to stalk\n>> ")
auth = raw_input("Enter Auth Token\n>> ")

if uf:
	print "***** Will unfollow all currently followed users *****"
if f:
	print "***** Will follow all currently unfollowed users *****"

p = 1
while True:
	d = requests.get(url("/users/" + sname + "/following", p, auth)).json()
	if not len(d) > 0:
		break
	else:
		for i in d:
			beCreepy(i)
		p += 1