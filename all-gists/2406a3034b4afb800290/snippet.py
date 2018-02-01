from gmusicapi import Webclient
from gmusicapi import Mobileclient
import vlc
import urllib

# Use Google account credintials. If two factor is enabled, use application specific password.
email = 'user@gmail.com'
password = 'password'

# Device ID for API queries. Leave blank if unknown.
device_id = ''

if email == '':
    email = raw_input("Email: ")

if password == '':
    password = raw_input("Password: ")

web_client = Webclient()
mobile_client = Mobileclient()

p = vlc.MediaPlayer()

print "Logging in..."

logged_in = web_client.login(email, password)
logged_in = mobile_client.login(email, password)

# logged_in is True if login was successful
if logged_in == True:
    print "Successfully logged in"
    
    if device_id == '':
        devices = web_client.get_registered_devices()
        valid = [device['id'][2:] + " (" + device['model'] + ")" for device in devices if device['type'] == 'PHONE']
        print valid
        id_index = int(raw_input("Device ID: "))
        device_id = valid[id_index].split(' ', 1)[0]
    
    while True:
        song_name = raw_input("Song title: ")

        results = mobile_client.search_all_access(song_name, 1)
        song = results['song_hits'][0]
        song_id = song['track']['nid']
        song_name = song['track']['title']
        song_artist = song['track']['artist']
        stream_url = mobile_client.get_stream_url(song_id, device_id)
        
        # Uncomment to save most recent song
        # urllib.urlretrieve (stream_url, "mp3.mp3")

        print "Now Playing " + song_name + " by " + song_artist
        p.set_mrl(stream_url)
        p.play()
else:
    print "Invalid login credintials"