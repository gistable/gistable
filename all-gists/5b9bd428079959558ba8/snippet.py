#! /usr/bin/env python

from gimpfu import *
import commands
import glob
import os
import string
import subprocess

suffixes = (['diffuse', '_d'], ['specular', '_s'], ['normal', '_n'], ['height', '_h'], \
	['ambient', '_a'], ['highdetail', '_hn'], ['shaperecog', '_sn'], ['lowdetail', '_ln'], \
	['mediumdetail', '_mn'])

def genFilenames(filename):
	(root, ext)=os.path.splitext(filename)
	filenames = {}
	for suffix in suffixes:
		filenames[suffix[0]]  = root + suffix[1] + ext
	return filenames

def saveLastOperation(image, filename):
	layer = pdb.gimp_image_get_active_layer(image)
	pdb.gimp_file_save(image, layer, filename, filename)

def specularEdge(image, filename, level, enhance):
	drawable = pdb.gimp_image_get_active_layer(image)
	newlayer = pdb.gimp_layer_copy (drawable, 1)
	pdb.gimp_image_add_layer(image, newlayer, -1)
	pdb.gimp_image_set_active_layer(image, newlayer)
	pdb.gimp_desaturate(newlayer)

	drawable = pdb.gimp_image_get_active_layer(image)
	newlayer = pdb.gimp_layer_copy (drawable, 1)
	pdb.gimp_image_add_layer(image, newlayer, -1)
	pdb.gimp_image_set_active_layer(image, newlayer)
	pdb.gimp_desaturate(newlayer)

	if enhance:
		pdb.plug_in_dog(image, newlayer, 1.0, 8.0, 1, 0)
	else:
		pdb.plug_in_dog(image, newlayer, 8.0, 1.0, 1, 0)
	#pdb.plug_in_vinvert(image,newlayer)
	
	pdb.gimp_layer_set_mode(newlayer, 7)
	pdb.gimp_image_merge_down(image, newlayer, 0)
	
	drawable = pdb.gimp_image_get_active_layer(image)
	pdb.gimp_brightness_contrast(drawable, 0, 64)
	pdb.gimp_levels(drawable, 0, level, 255, 1, 0, 255)
	if not enhance:
		pdb.gimp_image_raise_layer_to_top(image, drawable)
	pdb.gimp_file_save(image, drawable, filename, filename)
	pdb.gimp_edit_clear(drawable)

def removeShading(image):
	drawable = pdb.gimp_image_get_active_layer(image)
	newlayer = pdb.gimp_layer_copy (drawable, 1)
	pdb.gimp_image_add_layer(image, newlayer, -1)
	pdb.gimp_image_set_active_layer(image, newlayer)
	pdb.plug_in_gauss(image, newlayer, 20.0, 20.0, 0)
	pdb.plug_in_vinvert(image, newlayer)
	pdb.gimp_layer_set_mode(newlayer, 5)
	pdb.gimp_image_merge_visible_layers(image, 0)

def blur(image, diffuse, width, height, passes, normal):
	desatdiffuse = pdb.gimp_layer_copy (diffuse, 1)
	pdb.gimp_image_add_layer(image, desatdiffuse, -1)
	pdb.gimp_image_set_active_layer(image, desatdiffuse)
	if normal == 0:
		pdb.gimp_desaturate(desatdiffuse)

	for i in range(passes):
		drawable = pdb.gimp_image_get_active_layer(image)
		newlayer = pdb.gimp_layer_copy (drawable, 1)
		pdb.gimp_image_add_layer(image, newlayer, -1)
		pdb.gimp_image_set_active_layer(image, newlayer)
		pdb.plug_in_gauss(image, newlayer, width * 0.05, height * 0.05, 0)
		pdb.gimp_layer_set_mode(newlayer, 5)
		pdb.gimp_image_merge_down(image, newlayer, 0)
		drawable = pdb.gimp_image_get_active_layer(image)
	if normal == 1:
		pdb.plug_in_normalmap(image, drawable, 0, 0.0, 1.0, 0, 0, 0, 8, 0, 0, 0, 0, 0.0, drawable)
		pdb.gimp_layer_set_mode(drawable, 5)
		pdb.gimp_image_merge_down(image, drawable, 0)

def sharpen(image, diffuse, depth, filterSize, strength):
	sharpnormal = pdb.gimp_layer_copy (diffuse, 1)
	pdb.gimp_image_add_layer(image, sharpnormal, -1)
	pdb.gimp_image_set_active_layer(image, sharpnormal)
	
	pdb.plug_in_normalmap(image, sharpnormal, 0, 0.0, depth, filterSize, 0, 0, 0, 0, 0, 1, 0, 0.0, sharpnormal)
	#pdb.gimp_levels_stretch(sharpnormal)
	pdb.gimp_image_set_active_layer(image, sharpnormal)
	pdb.gimp_layer_set_mode(sharpnormal, 5)
	pdb.gimp_layer_set_opacity(sharpnormal, strength)
	pdb.gimp_image_raise_layer_to_top(image, sharpnormal)

def shapeRecognise(image, normalmap, strength):
	blurnormal = pdb.gimp_layer_copy (normalmap, 1)
	pdb.gimp_image_add_layer(image, blurnormal, -1)
	pdb.gimp_image_set_active_layer(image, blurnormal)
	pdb.plug_in_gauss(image, blurnormal, 20, 20, 0)
	pdb.plug_in_colors_channel_mixer(image, blurnormal, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, -200.0)
	pdb.plug_in_normalmap(image, blurnormal, 0, 0.0, 1.0, 0, 0, 0, 8, 0, 0, 0, 0, 0.0, blurnormal)
	pdb.plug_in_colors_channel_mixer(image, blurnormal, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, -200.0)
	pdb.gimp_layer_set_mode(blurnormal, 5)
	pdb.gimp_layer_set_opacity(blurnormal, strength)
	
def analyze(layer):
	highlights = pdb.gimp_histogram(layer, 0, 179, 256)
	midtones = pdb.gimp_histogram(layer, 0, 77, 178)
	shadows = pdb.gimp_histogram(layer, 0, 0, 76)
	f = open("/tmp/aidata.txt", "w")
	f.write(str(int(shadows[0])) + " " + str(int(shadows[1])) + " " + str(int(shadows[5] * 100)) + " ")
	f.write(str(int(midtones[0])) + " " + str(int(midtones[1])) + " " + str(int(midtones[5] * 100)) + " ")
	f.write(str(int(highlights[0])) + " " + str(int(highlights[1])) + " " + str(int(highlights[5] * 100)) + " ")

def doBaseMap(image, diffuse, depth, passes):
	for i in range(passes):
		newlayer = pdb.gimp_layer_copy (diffuse, 1)
		pdb.gimp_image_add_layer(image, newlayer, -1)
		pdb.gimp_image_set_active_layer(image, newlayer)
		ok = float(i + 1) * (i + 1)
		pdb.plug_in_gauss(image, newlayer, ok * 3, ok * 3, 0)
		pdb.plug_in_normalmap(image, newlayer, 5, 0.0, depth * ok, 0, 0, 0, 0, 0, 0, 1, 0, 0.0, newlayer)
		
		if i > 0:
			#pdb.gimp_layer_set_opacity(newlayer,50-(i*10))
			pdb.gimp_layer_set_mode(newlayer, 5)
			pdb.gimp_image_merge_down(image, newlayer, 0)
			newlayer = pdb.gimp_image_get_active_layer(image)
			pdb.plug_in_normalmap(image, newlayer, 0, 0.0, 1.0, 0, 0, 0, 8, 0, 0, 0, 0, 0.0, newlayer)
	drawable = pdb.gimp_image_get_active_layer(image)
	#newlayer=pdb.gimp_layer_copy (drawable, 1)
	#pdb.gimp_image_add_layer(image,newlayer,-1)
	#pdb.gimp_image_set_active_layer(image,newlayer)
	#pdb.gimp_levels_stretch(newlayer)
	#pdb.gimp_layer_set_opacity(newlayer,100)
	#pdb.gimp_layer_set_mode(newlayer,5)
	#pdb.gimp_image_merge_down(image,newlayer,0)		 
		


def batchnr(img, layer, rmlight, resize, seamless, rszmult, sedge, slevel,
						depth, hpasses, mdetail, ldetails, shaperecog, smoothstep, invheight):

	filename = pdb.gimp_image_get_filename(img)
	mapnames = genFilenames(filename)
	image = img
	size = pdb.gimp_image_width(image)

	if resize:
		hiresimg = pdb.gimp_image_resize(image, rszmult * size, rszmult * size, 0, 0)
		#hiresimg = pdb.gimp_file_load( getFilename(filename,"_hd"), filename)
		drawable = pdb.gimp_image_get_active_layer(hiresimg)
		noiselayer = pdb.gimp_layer_copy (drawable, 1)
		pdb.gimp_image_add_layer(hiresimg, noiselayer, -1)
		pdb.gimp_image_set_active_layer(hiresimg, noiselayer)
		pdb.plug_in_rgb_noise(hiresimg, noiselayer, 1, 1, 0.20, 0.20, 0.20, 0)
		#pdb.plug_in_blur(hiresimg,noiselayer)
		pdb.gimp_layer_set_mode(noiselayer, 14)
		pdb.gimp_image_merge_down(hiresimg, noiselayer, 0)
		image = hiresimg
		drawable = pdb.gimp_image_get_active_layer(image)
		###########################analyze(drawable)

	if rmlight:
		removeShading(image)

	diffuse = pdb.gimp_image_get_active_layer(image)
	pdb.gimp_levels_stretch(diffuse)
	if(seamless):
		pdb.plug_in_make_seamless(image, diffuse)
	pdb.gimp_file_save(image, diffuse, mapnames['diffuse'], mapnames['diffuse'])
	
	#drawable = pdb.gimp_image_get_active_layer(image)
	#pdb.gimp_levels(drawable,0,64,128,1,0,255)
	wsize = pdb.gimp_image_width(image)
	hsize = pdb.gimp_image_width(image)
	blur(image, diffuse, wsize, hsize, hpasses, 0)

	normalmap = pdb.gimp_image_get_active_layer(image)
	if smoothstep:
		pdb.plug_in_blur(image, normalmap)
	if invheight:
		pdb.plug_in_vinvert(image, normalmap)
		

	pdb.gimp_file_save(image, normalmap, mapnames['height'], mapnames['height'])
	

	#lfnormal=pdb.gimp_layer_copy (diffuse, 1)
	#pdb.gimp_image_add_layer(image,lfnormal,-1)
	#pdb.gimp_image_raise_layer_to_top(image,lfnormal)
	#pdb.plug_in_normalmap(image, lfnormal,8,0.0,depth,0,0,0,0,0,0,0,0,0.0,normalmap)
	#blur(image,lfnormal,hpasses,1)
	#normalmap = pdb.gimp_image_get_active_layer(image)
	doBaseMap(image, diffuse, depth, hpasses)
	normalmap = pdb.gimp_image_get_active_layer(image)
	pdb.gimp_file_save(image, normalmap, mapnames['highdetail'], mapnames['highdetail'])


	shapeRecognise(image, normalmap, shaperecog)
	if smoothstep:
		normalmap = pdb.gimp_image_get_active_layer(image)
		pdb.plug_in_blur(image, normalmap)

	saveLastOperation(image, mapnames['shaperecog'])
	
	sharpen(image, diffuse, depth, 0, ldetails)
	normalmap = pdb.gimp_image_get_active_layer(image)
	pdb.plug_in_sharpen(image, normalmap, 20)
	saveLastOperation(image, mapnames['lowdetail'])
					
	sharpen(image, diffuse, depth, 6, mdetail)
	normalmap = pdb.gimp_image_get_active_layer(image)
	pdb.plug_in_blur(image, normalmap)
	saveLastOperation(image, mapnames['mediumdetail'])
	
	pdb.gimp_drawable_set_visible(diffuse, 0)
	pdb.gimp_image_merge_visible_layers(image, 0)
	
	drawable = pdb.gimp_image_get_active_layer(image)
	pdb.plug_in_normalmap(image, drawable, 0, 0.0, 1.0, 0, 0, 0, 8, 0, 0, 0, 0, 0.0, drawable)
	pdb.gimp_file_save(image, drawable, mapnames['normal'], mapnames['normal'])
	pdb.plug_in_colors_channel_mixer(image, drawable, 0.0, -200.0, 0.0, 0.0, 0.0, -200.0, 0.0, 0.0, 0.0, 1.0)
	pdb.gimp_desaturate(drawable)
	pdb.gimp_levels_stretch(drawable)
	pdb.gimp_file_save(image, drawable, mapnames['ambient'], mapnames['ambient'])
	pdb.gimp_drawable_set_visible(diffuse, 1)
	pdb.gimp_image_set_active_layer(image, diffuse)

	specularEdge(image, mapnames['specular'], slevel, sedge)


register(
        "InsaneBump", "", "", "", "", "",
        "<Image>/Filters/Map/Insane...", "",
        [
        (PF_TOGGLE,  "rmlight",    "Remove Lighting:",         FALSE),
        (PF_TOGGLE,  "resize",     "Resize:",                  FALSE),
        (PF_TOGGLE,  "seamless",   "Make Seamless:",           TRUE),
        (PF_INT32,   "rszmult",    "Resize Multiplier:",       2),
        (PF_TOGGLE,  "sedge",      "Edge Enhance Specular:",   TRUE),
        (PF_SPINNER, "slevel",     "Specular Level:",          64, (0, 255, 1)),
        (PF_FLOAT,   "depth",      "Depth (>0):",              20),
        (PF_INT32,   "hpasses",    "Detail Pass Count:",       3),
        (PF_SPINNER, "mdetail",    "Medium Detail Intensity:", 50, (0, 100, 1)),
        (PF_SPINNER, "ldetails",   "Low Detail Intensity:",    50, (0, 100, 1)),
        (PF_SPINNER, "shaperecog", "Shape Recognition:",       50, (0, 100, 1)),
        (PF_TOGGLE,  "smoothstep", "Smooth Step:",             TRUE),
        (PF_TOGGLE,  "invheight",  "Invert Height Map:",       FALSE),
        ],
        [],
        batchnr
        )

main()