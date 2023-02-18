#!/usr/bin/env python

#made by insomniac_lemon

from gimpfu import *
import os
import errno

def makedirectory(path):
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

home = os.path.expanduser("~")




def refresh():
	global images 
	global image
	global layer
	images = gimp.image_list() 
	image = images[0]
	layer = image.layers[0]

refresh()

layer_name = pdb.gimp_layer_get_name(layer)

if ('clock' in layer_name) :
	animation = 'clock'
	frame_type = 'time'

if ('compass' in layer_name) :
	animation = 'compass'
	frame_type = 'angle'

file_path_base = home + '/convert_clock_compass/'
file_path_base_textures = file_path_base + 'assets/minecraft/textures/items/'
file_path_base_models = file_path_base + 'assets/minecraft/models/item/'

if (animation == 'clock'):
	filefolder = 'clock/clock'

if (animation == 'compass'):
	filefolder = 'compass/compass'

deleted = False

if ((os.path.exists(file_path_base_models + animation + '/')) and file_path_base != home):
	deleted = True
	for root, dirs, files in os.walk(file_path_base, topdown=False):
    		for name in files:
        		os.remove(os.path.join(root, name))
    		for name in dirs:
        		os.rmdir(os.path.join(root, name))

makedirectory(file_path_base_textures + animation + '/')
makedirectory(file_path_base_models + animation + '/')

w = pdb.gimp_image_width(image)
h = pdb.gimp_image_height(image)
tile_number = h/w
current_tile = 0
animation_frame = 0
half_increment = 1.000000 / (tile_number * 2)
increment = 1.000000 / tile_number
frame = 0.000000


if (tile_number <= 10):
	max_zeros = 1
elif (tile_number <= 100):
	max_zeros = 2
elif (tile_number <= 1000):
	max_zeros = 3
else:
	max_zeros = 4

def find_zeros():
	global padding
	if (max_zeros == 1):
		padding = '0'
	if (max_zeros == 2):
		padding = '00'
	if (max_zeros == 3):
		padding = '000'
	if (max_zeros == 4):
		padding = '0000'

find_zeros()
original_max_zeros = str(pow(10,max_zeros))

def find_compass_zeros():
	global compass_padding
	if (animation_frame <= 9):
		compass_padding = original_max_zeros[1:]
	elif (animation_frame <= 99):
		compass_padding = original_max_zeros[2:]
	elif (animation_frame <= 999):
		compass_padding = original_max_zeros[3:]
	else:
		compass_padding = original_max_zeros[4:]


pdb.gimp_image_resize(image, w, w, 0, 0)

frame = frame + half_increment
if (animation == 'compass'):
	animation_frame = tile_number / 2
	find_compass_zeros()

def save_image():
	new_image = pdb.gimp_image_duplicate(image)
	new_layer = new_image.layers[0]
	pdb.gimp_image_crop(new_image, w, w, 0, 0)
	filepath = file_path_base_textures + filefolder + '_' + padding + str(current_tile) + '.png'
	pdb.file_png_save2(new_image, new_layer, filepath, filepath, 0, 9, 0, 0, 0,0,0,0,0)
	gimp.delete(new_image)
	refresh()
	if (current_tile != tile_number-1):
		pdb.gimp_layer_translate(layer, 0, -w)
	else:
		pdb.gimp_image_resize_to_layers(image)

def save_model():
	global frame
	modelname = file_path_base_models + filefolder + '_' + padding + str(current_tile) + '.json' 
	file = open(modelname,'a')
	contents = '{"parent": "item/generated","textures": {"layer0": "items/' + filefolder + '_' + padding + str(current_tile) + '"}}'
	file.write(contents)
	file.close()

def save_main():
	global animation_frame	
	global current_tile
	global padding
	padding_images = padding
	if (animation == 'compass'):
		if (animation_frame == 10 or animation_frame == 100 or animation_frame == 1000) :
			find_compass_zeros()
		padding = compass_padding
	with open(main_file, "a") as myfile:
		myfile.write('{"predicate":{"' + frame_type + '":' + str(frame) + '},"model":"item/' + filefolder + '_' + padding + str(animation_frame) +'"},\n\t')
	padding = padding_images
	current_tile += 1
	animation_frame += 1
	if (animation == 'compass' and animation_frame == tile_number):
		animation_frame = 0
		find_compass_zeros()	


main_file = file_path_base_models + animation + '.json'
padding_images = padding
if (animation == 'compass'):
	padding = compass_padding

file = open(main_file, "a")
contents = '{"parent": "item/generated","textures": {"layer0": "items/' + filefolder + '_' + padding + str(animation_frame) + '"' '},"overrides": [ \n\t{"predicate":{' + '"'
save_image()
save_model()
current_tile += 1
animation_frame += 1
contents = contents + frame_type + '":0.0000000},"model":"item/' + animation + '"},\n\t{"predicate":{"' + frame_type + '":' + str(frame) + '},"model":"item/' + filefolder + '_' + padding + str(animation_frame) + '"},\n\t'
file.write(contents)
file.close()
padding = padding_images
save_image()
save_model()
current_tile += 1
animation_frame += 1



while (current_tile < tile_number):
	if (current_tile == 10 or current_tile == 100 or current_tile == 1000) :
		max_zeros -= 1
		find_zeros()
	save_image()
	save_model()
	frame = frame + increment
	save_main()
	if (animation == 'compass' and animation_frame == tile_number / 2):
		break

frame = frame + increment
with open(main_file, "a") as myfile:
	myfile.write('{"predicate":{"' + frame_type + '":' + str(frame)  + '},"model":"item/' + animation + '"}]}')

mcmeta = file_path_base + 'pack.mcmeta'
if not (os.path.exists(mcmeta)):
	file = open(mcmeta,'a')
	contents = '{"pack":{"pack_format":2,"description":"Converted clock and/or compass animations for 1.9"}}'
	file.write(contents)
	file.close()
	print('An mcmeta file was created')

if (deleted == True):
	print('Files were deleted')

print('Your animation has ' + str(tile_number) + ' tiles')
print(str(current_tile) + ' tiles should have been created')
print('Look for your files in ' + file_path_base)
print('Your original image was NOT modified... but if you run the script where the files it needs to create exist already, the ALL previously outputted files WILL be deleted!')
print('So be warned(!): Keep your 1.8 animations backed up. Once you run this script ONCE for a clock and ONCE for a compass, get the files where they need to go, otherwise you may lose them')
print('done')

pass
