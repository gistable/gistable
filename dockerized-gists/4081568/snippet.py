import os
import markdown
import requests
import webbrowser

pinToken = 'Put your Pinboard API token here'
pinAPI = 'api.pinboard.in/v1/'
pinGet = 'posts/all'
pinURL = 'https://' + pinAPI + pinGet + '?auth_token=' + pinToken + '&toread=yes&format=json'

def main():
	j = requests.get(pinURL).json

	s = ""

	for article in j:
		outstring = "* [%s](%s)\n" % (article['description'], article['href'])
		s += outstring

	md = markdown.Markdown()
	contents = md.convert(s)

	with open('reading_list.html', 'w') as f:
		f.write(contents)

	pth = "file:///" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "reading_list.html")
	webbrowser.open(pth)
	
if __name__ == '__main__':
	main()
