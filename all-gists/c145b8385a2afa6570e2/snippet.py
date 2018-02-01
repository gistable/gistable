"""
Code to write data read from a URL to a file

Based on an answer on SO:
http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python/22721
"""

import urllib2

mp3file = urllib2.urlopen("http://www.example.com/songs/mp3.mp3")
with open('test.mp3', 'wb') as output:
    while True:
        data = mp3file.read(4096)
        if data:
            output.write(data)
        else:
            break
