from bs4 import BeautifulSoup
import requests

story_qty = int(raw_input('How many stories do you want to get? '))
page = 1
story_count = 0
stories = []

# Get the data to filter for a given page
def getPageData():
    global page

    if page == 1 or page < 1:
        url = 'http://bimmerpost.com/'
    else:
        url = 'http://bimmerpost.com/page/' + str(page)

    page += 1
    return BeautifulSoup(requests.get(url).text)

# get the stories within this set of data
def parseStories(data):
    global story_count
    global story_qty
    global stories

    for story in data.select('h2 > a'):
        story_count += 1
        stories.append({'title': story.text, 'url': story['href']})

# Get the stories
def getStories():
    global story_count
    global story_qty

    while (story_count < story_qty):
        parseStories(getPageData())

    # Trim the fat
    del stories[story_qty:]

    if len(stories) <= story_qty:
        return True
    else:
        return False

################################################################################

list_of_stories = getStories()

if list_of_stories:
    # Print all of the titles
    for story in stories:
        print story['title'] + ' => ' + story['url']