""" 
Lays down the law for your phone, telling it what to do and when
Inspired by docblades' silent_night.py
"""
import android, string, time, math, datetime
from datetime import time, datetime, timedelta
from time import sleep
from threading import Timer
droid = android.Android()
interval_secs = 480
location = []
a_day = timedelta(days=1)
""" where am I, what time is it """
def get_location(): 
  droid.startLocating("coarse")
  """apparently you need to wait for the sensor to come up"""
  droid.sleep(5)
  location = droid.readLocation()

"""available actions"""
def go_silent():
  droid.setRingerSilent(True)

def stop_silent():
  droid.setRingerSilent(False)
def cow():
  droid.makeToast("moo")
  droid.speak("moo")


""" given a time and a place, what should I do"""
def follow_rules():
  d_now = datetime.now()
  for rule in rules:
    """todo: change this to account for rules that cross midnight"""
    if rule["time_begin"] < d_now < rule["time_end"]:
      """well then it is time to check the position"""
      if rule["radius_in_km"] < distance_between(rule["location"],location["result"]):
	rule["action"]()

def distance(location_1, location_2):
  """using the spherical law of cosines from 
  http://www.movable-type.co.uk/scripts/latlong.html """
  R = 6371
  lat1 = math.radians(location_1['latitude'])
  lat2 = math.radians(location_2['latitude'])
  lon1 = math.radians(location_1['longitude'])
  lon2 = math.radians(location_2['longitude'])
  return math.acos( math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2) * math.cos(lon2-lon1)) * R


  
""" How long should I wait for? """
def till(time_in):
  d_now = datetime.now()
  time_today = datetime.combine(datetime.today(), time_in)
  if d_now < time_today:
    return time_today - d_now 
  return (time_today + a_day) - d_now

def secs(time_delta):
  return time_delta.seconds + ( time_delta.days * 24 * 60 * 60)

""" let's store these rules and events in an easy to edit way"""
""" 
Rules are things that we need to check based on
a date or time (or other stuff - go nuts).
"""
rules = []
"""put the phone on vibrate when I am near where I work"""
"""let's pretend I get to work in the chrysler building"""
rules.append({"time_begin":time(23,55), "time_end":time(06,00),"location":{"latitude":40.752190, "longitude":-73.974618} ,"radius_in_km":1,"action":go_silent})



"""
Events happen at a specific time.  I don't want to have my phone set BACK
to silent every few minutes if I set it to be noisy.  So I just want these things to happen one time per day.
"""
events = []
"""no wakey at night"""
events.append({"time_at":time(23,55), "action":go_silent})
"""turn the ringer back on"""
events.append({"time_at":time(06,55), "action":stop_silent})
events.append({"time_at":time(21,19), "action":cow})

def setup_events():
  for event in events:
    setup(event)

def setup(event):
  """we'll set a timer to go off and run a function at time_at"""
  seconds = secs(till(event["time_at"]))
  Timer(seconds, process, event).start()

def process(event):
  event["action"]()
  setup(event)

""" run forever"""
def main_loop():
  while True:
    sleep(interval_secs)
    droid.makeToast("woke up")
    get_location()
    follow_rules(location)
droid.makeToast("setting up events")
setup_events()
droid.makeToast("done setting up events")
main_loop()

"""
I'd like to have my phone go silent at my bedtime
I'd like my ringer to come back to normal when I awake
I'd like my phone to ring if I am out past my bedtime and someone calls me.

I'd like my phone to be quiet when I turn the phone facedown.  That's not working - yet!

I'd like my phone to go to vibrate when I am near where I work.
Judge Droid is licensed for your pleasure under the WTFPL.
"""