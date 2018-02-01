from bs4 import BeautifulSoup
import requests
import pynotify
import time

def sendmessage(title, message):
	pynotify.init("Test")
	notice = pynotify.Notification(title, message)
	notice.show()
	return

names = ["Dhirubhai Ambani Institute of Information and Communication Technology, Gandhinagar",
		"Indian Institute of Technology - Indore",
		"Indian Institute of Technology - Kanpur",
		"Indian Institute of Technology - Bombay",
		"International Institute of Information Technology - Hyderabad",
		"International Institute of Information Technology - Bangalore",
		"Chennai Mathematical Institute",
		"National Institute of Technology, Karnataka"]

solved = [0, 0, 0, 0, 0, 0, 0, 0]

r = requests.get('https://icpc.baylor.edu/scoreboard/')

soup = BeautifulSoup(r.text, 'html.parser')

rows = soup.find_all('tr')

print "Initialising!"

i = 0

for row in rows:
	for name in names:
		if name in str(row):
			print name + ": " + row.find_all('td')[0].string
			solved[i] = int(row.find_all('td')[3].string)
			i = i+1

print solved

while True:
	r = requests.get('https://icpc.baylor.edu/scoreboard/')

	soup = BeautifulSoup(r.text, 'html.parser')

	rows = soup.find_all('tr')

	i = 0
	for row in rows:
		for name in names:
			if name in str(row):
				print name + ": " + row.find_all('td')[0].string
				new_solved = int(row.find_all('td')[3].string)
				if new_solved != solved[i]:
					solved[i] = new_solved
					sendmessage(name + " solved another problem!", "Their new rank is " + row.find_all('td')[0].string)
				i = i+1

	time.sleep(60)
