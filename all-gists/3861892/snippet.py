from os import path, environ
import datetime
import json
import sys

appdata = environ['APPDATA']
sublime_path  = 'Sublime Text 2'
settings_path = 'Packages\User\Preferences.sublime-settings'
day_profile   = 'Packages/Color Scheme - Default/Solarized (Light).tmTheme'
night_profile = 'Packages/Color Scheme - Default/Solarized (Dark).tmTheme'
daylight_hours = range(7,19) # hours in 24 hour time, note endpoint is reduced by 1
 
def switch_profile(profile):
	""" 
	Opens Preferences.sublime-settings file, reads the JSON, replaces the
	JSON and writes the new JSON, all without closing, to avoid race 
	conditions. 
	"""
	print profile
	f = open(file_path, 'r+')
	settings_json = json.loads(f.read())
	print settings_json['color_scheme']
	if settings_json['color_scheme'] != profile:
		settings_json['color_scheme'] = profile
		f.seek(0)
		print settings_json['color_scheme']
		json.dump(settings_json, f, indent=4) # pretty print and write to file
		f.truncate()
	f.close()

now = datetime.datetime.now()
file_path = path.join(appdata, sublime_path, settings_path)

if now.hour in daylight_hours:
	switch_profile(day_profile)
else:
	switch_profile(night_profile)
sys.exit()