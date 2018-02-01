import os
import urllib2
import datetime
import cStringIO
import ntpath
from bs4 import BeautifulSoup as bs
from anki import Collection as aopen
from operator import itemgetter
from PIL import Image
from random import randint

### Test URLs
url = 'http://quizlet.com/24760403/anatomy-and-physiology-ii-the-endocrine-system-flash-cards/'
#url = 'http://quizlet.com/2621787/histology-lab-photo-quiz-flash-cards/'

tags      = ['tag1', 'tag2']
card_type = 'Basic'

### OS X
coll_path = "/Users/YOUR_NAME_HERE/Documents/Anki/DrLulz/collection.anki2"
temp_file = "/tmp/file_%s.jpg"
 
### WIN
#coll_path  = os.path.abspath("C:\\Users\\YOUR_NAME_HERE\\Documents\\Anki\\User 1\\collection.anki2")
#temp_file  = "C:/tmp/file_%s_.jpg"



def make_cards(deck_title, front, back):
    
    a_coll = aopen(coll_path)

    deck_name = 'Quizlet' + '::' + deck_title
    deck_id = a_coll.decks.id(deck_name)
    a_coll.decks.select(deck_id)
    
    model = a_coll.models.byName(card_type)
    model['did'] = deck_id
    a_coll.models.save(model)
    a_coll.models.setCurrent(model)
    
    card = a_coll.newNote()
    
    
    if 'http' not in front:
        card['Front'] = front
    else:
        img_path   = get_img(front)
        a_coll.media.addFile(img_path.decode('utf-8'))
        card['Front'] = u'<img src="%s">' % ntpath.basename(img_path)
        os.remove(img_path)
        
    card['Back'] = back
    card.tags = tags
    
    a_coll.addNote(card)
    a_coll.save()
    a_coll.close()
    

        
def get_cards(source):
    soup  = bs(source)
    title = soup.find('h1', class_='SetTitle-title').text
    qas   = soup.select('div.term')
    
    for qa in qas:
        img = qa.find('img')
        if img is None:
            # may need to reverse question / answer
            question = qa.find('span', class_='qDef').get_text()
            answer   = qa.find('span', class_='qWord').get_text()
            make_cards(title, question, answer)
        else:
            # may need to reverse image / answer
            question    = qa.find('img')['data-srcset']
            answer   = qa.find('span', class_='qWord').get_text()
            make_cards(title, question, answer)
    


def get_img(image_url):
    ran_int = randint(100, 999)
    file = cStringIO.StringIO(urllib2.urlopen(image_url).read())
    filename = temp_file % (datetime.datetime.now().strftime("%s") + str(ran_int))
    image_info = Image.open(file)
    image_info.save(filename)
    file.close()
    
    return filename
    


def html_source(url):
    try:         
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        html_source = response.read().decode('utf-8')
        get_cards(html_source)
    except Exception, detail: 
        print "Err ", detail
        



html_source(url)