#!/usr/bin/python3
"""link all mods in <SteamRoot>/SteamApps/workshop/content/<AppID/<ModID> to 
<SteamRoot>/SteamApps/common/<Arma3ModFolder>/@<ModName>
if <SteamRoot>/SteamApps/workshop/content/<AppID>/<ModID>/meta.cpp exists

Author: Nikolai Zimmermann aka Chronophylos


"""

import os
import glob
from subprocess import check_output

if os.name == "nt":
	"""windows doesnt know how to do stuff"""
	def symlink_ms(source, link_name):
		import ctypes
		csl = ctypes.windll.kernel32.CreateSymbolicLinkW
		csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
		csl.restype = ctypes.c_ubyte
		flags = 1 if os.path.isdir(source) else 0
		try:
			if csl(link_name, source.replace('/', '\\'), flags) == 0:
				raise ctypes.WinError()
		except:
			pass
	os.symlink = symlink_ms

#### change stuff here
AppID = "107410"
WorkshopFolder = "E:/Steam/SteamApps/workshop/content/" + AppID
Arma3ModFolder = "ArmA III MODS"
TargetFolder = "E:/Steam/SteamApps/common/" + Arma3ModFolder
####
ModList = list()

# check if variables are really directories
if not os.path.isdir(WorkshopFolder):
	print("[ ERROR ] " + repr(WorkshopFolder) + " is not a directory.")
	quit()
if not os.path.isdir(TargetFolder):
	print("[ ERROR ] " + repr(TargetFolder) + " is not a directory.")
	quit()

"""get all folder in <SteamRoot>/SteamApps/workshop/content/<AppID> with a
<SteamRoot>/SteamApps/workshop/content/<AppID>/<ModID>/meta.cpp file
add <ModID> and <ModName> from meta to ModList"""
# like [["examplemod1","id1"],["examplemod2","id2"]]
for path in glob.iglob(WorkshopFolder + "/*"): # all files in <WorkshopFolder>
	meta = path + "/meta.cpp"
	if os.path.isfile(meta): # if meta exists
		with open(meta, 'r') as metafile:
			ModID = str()
			ModName = str()
			for line in metafile:
				if line.startswith("publishedid"):
					ModID = line[14:-2]
				if line.startswith("name"):
					ModName = line[7:-2].strip("\"")
			# fix missing ids with path
			if ModID == "0":
				print("[ ERROR ] ModID of " + ModName + " is missing.")
				ModID = path.split("\\")[1]
			ModList.append([ModID, ModName])

# link all these files
# if not target is folder or link
for mod in ModList:
	target = TargetFolder + "/@" + mod[1]
	source = WorkshopFolder + "/" + mod[0]
	if os.path.isdir(target):
		print("[ ERROR ] " + target + " is a directory.", mod)
		continue
	if os.path.islink(target):
		print("[ ERROR ] " + target + " is already linked.", mod)
		continue
	# make shure mod really exists
	if not os.path.isdir(source):
		print("[ ERROR ] " + source + " does not exist.", mod)
		continue
	# link mod
	print("[ INFO ]  linking " + target + " -> " + source)
	os.symlink(source, target)