import os
import time

document = open("My Clippings.txt","r") 
 
data = "".join(document.readlines())
notes = []
try:
    clippings = data.split('==========')
    for clip in clippings:
        clipping = clip.split('Added on ')

        title = clipping[0].split('\r\n- ')[0].replace('\r\n','')
        date = clipping[1].split('\r\n')[0]
        location = clipping[0].split('\r\n- ')[1].replace('\r\n','')
        text = clipping[1].split('\r\n\r\n')[1]
        note = {'title': title, 'date': date, 'location': location, 'text': text}
        notes.append(note)
        #print note
    
except:
    print 'Unable parse clipping'

def MakeEvernoteNote(note):
    cmd = '''
    osascript<<END 
        tell application "Evernote" 
        set clip to create note title "
        '''+ unicode(note['title'], errors="ignore") + '''
        " with text "
        '''+ unicode(note['text'], errors="ignore") + "\n" + unicode(note['location'], errors="ignore") + unicode(note['date'], errors="ignore") + '''
        " 
        if (not (tag named "Kindle" exists)) then 
            make tag with properties {name:"Kindle"} 
        end if 
        assign tag "Kindle" to clip 
    end tell 
    END'''

    os.system(cmd)

for note in notes:
    time.sleep(1)
    MakeEvernoteNote(note)