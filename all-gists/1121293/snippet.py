from plistlib import *
import re, os

print "type the name of the TexturePacker plist"
path = os.path.realpath(os.path.expanduser(raw_input()))
base_name = re.sub(".plist", "", os.path.basename(path))
dir_name = os.path.dirname(path) + "/"

# read TexturePacker info
tp_plist = readPlist( base_name + ".plist" )
metadata = tp_plist["metadata"]
frames = tp_plist["frames"]
tp_plist_hd = readPlist( base_name + "-hd.plist" )
metadata_hd = tp_plist_hd["metadata"]
frames_hd = tp_plist_hd["frames"]

size_strings = re.sub("[{}]", "", metadata["size"]).split(",")
size_floats = [float(size_strings[0]), 
			   float(size_strings[1])]

# write SpriteHelper info (TODO: add physics)
sprites_info = []
for image in frames.keys():

	frame = frames[image]["frame"]
	frame_hd = frames_hd[image]["frame"]

	frame_strings = re.sub("[{}]", "", frame).split(",")
	frame_strings_hd = re.sub("[{}]", "", frame_hd).split(",")

	# rearrange the frame for sprite helper if it's rotated
	if (frames[image]["rotated"]):
		frame_strings = [frame_strings[0],
						 frame_strings[1],
						 frame_strings[3],
						 frame_strings[2]]
		frame = "{{" + frame_strings[0] + "," + \
					   frame_strings[1] + "},{" + \
					   frame_strings[2] + "," + \
					   frame_strings[3] + "}}"

		frame_strings_hd = [frame_strings_hd[0],
						 	frame_strings_hd[1],
							frame_strings_hd[3],
							frame_strings_hd[2]]
		frame_hd = "{{" + frame_strings_hd[0] + "," + \
						  frame_strings_hd[1] + "},{" + \
						  frame_strings_hd[2] + "," + \
						  frame_strings_hd[3] + "}}"

	# calculate the frame's uv mapping
	frame_floats = [float(frame_strings[0]), 
					float(frame_strings[1]), 
					float(frame_strings[2]), 
					float(frame_strings[3])]
	frame_uv = "{{" + str(frame_floats[0] / size_floats[0]) + "," + \
			   str(frame_floats[1] / size_floats[1]) + "},{" + \
			   str(frame_floats[2] / size_floats[0]) + "," + \
			   str(frame_floats[3] / size_floats[1]) + "}}"

	sprite = dict(
		PhysicProperties = dict(
			Category = 1,
			Density = 0.20000000298023224,
			Fixtures = [],
			Friction = 0.20000000298023224,
			Group = 0,
			IsCircle = False,
			IsFixedRot = False,
			IsSensor = False,
			Mask = 65535,
			PhysicType = 0,
			Restitution = 0.20000000298023224,
			SHHolesPoints = [],
			SHShapePoints = [],
			ShapeBorderH = 0,
			ShapeBorderW = 0,
		),
		TextureProperties = dict(
			Color = "{{1, 1}, {1, 0}}",
			Frame = frame,
			Frame_HD = frame_hd,
			FrameUV = frame_uv,
			Image = base_name + ".png",
			Image_HD = base_name + "-hd.png",
			ImageURL = dir_name + base_name + ".png",
			ImageURL_HD = dir_name + base_name + "-hd.png",
			Name = image,
			Opacity = 1,
			Scale = "{1, 1}",
			ZOrder = 0,
		),
	)
	sprites_info.append(sprite)

# add sprite_info to the SpriteHelper plist
spritehelper_plist = dict(
    Author = "Bogdan Vladu", # Really? This seems unnecessary.
    CreatedWith = "SpriteHelper", # ...TexturePacker
    ImportedImages = [dir_name + base_name + ".png"],
    ImportedImages_HD = [dir_name + base_name + "-hd.png"],
	SPRITES_INFO = sprites_info,
	ScenePreference = dict(
		BackgroundColor = "{{0.8, 0.8}, {0.8, 1}}",
		GridSize = 32,
	),
	Version = "1.6.7",
)

# write out the awesomeness
writePlist(spritehelper_plist, base_name + ".pshs")

# now let's replace _HD with -HD
f = open(base_name + ".pshs", "r")
string = f.read()
f.close()

new_string = re.sub("_HD", "-HD", string)
f = open(base_name + ".pshs", "w")
f.write(new_string)
f.close()