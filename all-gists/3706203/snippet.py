# Minecraft Overviewer dynamic config file for multiple Minecraft worlds 
# managed by MSM (https://github.com/marcuswhybrow/minecraft-server-manager)

import os

# Define where to put the output here.
outputdir = "/storage/www/vhosts/minecraft.example.com"

# Add Javascript to map when rendering
from observer import JSObserver
observer = JSObserver(outputdir, 10)

# Default rendermode for all daylight maps
rendermode = "smooth_lighting"

#POI Filters

def playerIcons(poi):
        if poi['id'] == 'Player':
                poi['icon'] = "http://overviewer.org/avatar/%s" % poi['EntityId']
                return "Last known location for %s" % poi['EntityId']

def signFilter(poi):
        if poi['id'] == 'Sign':
                return "\n".join([poi['Text1'], poi['Text2'], poi['Text3'], poi['Text4']])

def chestFilter(poi):
        if poi['id'] == 'Chest':
                return "Chest with %d items" % len(poi['Items'])

# Where all the MSM servers are stored
servers = os.walk('/opt/msm/servers').next()[1]

# Loop through each server directory
for the_server in servers:
	world_name = the_server.replace("_", " ").title()
	worlds[world_name] = "".join(("/opt/msm/servers/",the_server,"/worldstorage/world"))
	
	# Overworld
	renders["".join((the_server, "")).replace("_"," ").title()] = {
        	'world': world_name,
        	'title': 'Daytime',
        	'dimension': "overworld",
        	'markers': [dict(name="All Signs", filterFunction=signFilter),
			dict(name="Chests",    filterFunction=chestFilter, icon="chest.png", createInfoWindow=False),
			dict(name="Players",   filterFunction=playerIcons)]
	}
	# Overworld Night
	renders["".join((the_server," Night")).replace("_"," ").title()] = {
        	'world': world_name,
		'title': 'Nighttime',
        	'rendermode': 'smooth_night',
        	"dimension": "overworld",
	}
	# Overworld caves
	renders["".join((the_server," Caves")).replace("_"," ").title()] = {
        	'world': world_name,
        	'title': 'Caves',
        	"rendermode": cave,
        	"dimension": "overworld",
        	"overlay" : [world_name, "".join((the_server," Night")).replace("_"," ").title()],
	}

	# Only add The End and Nether if they actually exist
	subregions = os.walk("".join(('/opt/msm/servers/',the_server,"/worldstorage/world/"))).next()[1]
	for subregion in subregions:
		subregion_path = "".join(('/opt/msm/servers/',the_server,"/worldstorage/world/",subregion))
		if ('DIM-1' in subregion) and os.listdir(subregion_path):
			renders["".join((the_server," Nether")).replace("_"," ").title()] = {
        			'world': world_name,
        			'title': 'Nether',
        			"rendermode": nether_smooth_lighting,
        			"dimension": "nether",
			}
		if ('DIM1' in subregion) and os.listdir(subregion_path):
			renders["".join((the_server," The End")).replace("_"," ").title()] = {
        			'world': world_name,
        			'title': 'The End',
        			"rendermode": nether_smooth_lighting,
        			"dimension": "end",

			}