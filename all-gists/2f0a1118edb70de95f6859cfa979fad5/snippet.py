##################################################################
#usage: generate_mosaic.py <original image> <tiles image library>
#################################################################
from PIL import Image, ImageOps
from math import floor
import glob, os,sys

#define parameters
OUTFILE = "mosaic.jpg" #Out file name
tiles_numbers_width = 50 # tile numbers in width direction, tile numbers in height direction will be determined by original image
size1 =128 #The pixel numbers of square tile images, 
size = size1, size1

def average(im): #function to calculate average RGB values of individual Image objective
	width, height = im.size
	r = 0
	g =0
	b = 0
	for x in range (width):
		for y in range (height):
			tr, tg, tb = im.getpixel((x,y))
			r +=tr
			g += tg
			b += tb
	r = r/(height*width)
	g = g/(height*width)
	b = b/(height*width)
	return (r,g,b)

class Tiles:

	def __init__(self, tiles_path):
		self.tiles_src_path = tiles_path

	def process_tiles(self): #generate smaller image files for easy operation
		tiles_rgb_lib = [] #list,use [index] to access individual component
		name = 1
		print("Start to process tiles images")
		thumbnail_path = self.tiles_src_path + "/thumbnail"
		if not os.path.exists(thumbnail_path):
			os.makedirs(thumbnail_path)
		for file in os.listdir(self.tiles_src_path):
				infile = os.path.join(self.tiles_src_path, file)
				if os.path.isdir(infile):
					continue
				origi_im = Image.open(infile)
				im = ImageOps.fit(origi_im, size, Image.ANTIALIAS)
				tiles_rgb_lib.append(average(im)) #average rgb values
				im.save(thumbnail_path+"/"+str(name) + ".thumbnail", "JPEG")
				name+=1
		print("Tiles image process completed")
		return tiles_rgb_lib

class Original_Image:
	
	def __init__(self, image_path, tiles_rgb_lib):
		self.original_image_path = image_path
		self.rgb_lib = tiles_rgb_lib
	
	def _find_tile_index_(self, target_rgb):
		diff = sys.float_info.max
		index = 1
		answer = 1
		for (x,y,z) in self.rgb_lib:
			temp_diff = (2+(target_rgb[0]+x)/2/256)*(target_rgb[0]-x)*(target_rgb[0]-x) + 4*(target_rgb[1]-y)*(target_rgb[1]-y) + (2+(255-(target_rgb[0]+x)/2)/256)*(target_rgb[2]-z)*(target_rgb[2]-z) 
			#color comparison method refered to WIKIPEDIA page "color difference"
			if temp_diff < diff:
				diff = temp_diff
				answer = index
			index += 1
		return answer

	def generate_index_matrix(self):
		print("start to process orginal picture")
		org_im = Image.open(self.original_image_path)
		org_w = org_im.size[0]
		org_h = org_im.size[1]
		org_tile_size = floor(org_w/tiles_numbers_width)
		tiles_numbers_height = floor (org_h/org_tile_size)
		act_w = tiles_numbers_width*org_tile_size
		act_h = tiles_numbers_height*org_tile_size
		w_crop = (org_w - act_w)/2
		h_crop = (org_h - act_h)/2
		croped_org_im = org_im.crop((w_crop, h_crop, org_w-w_crop, org_h - h_crop))
		index_table = []
		for x in range(tiles_numbers_width):
			print(x)
			temp_array = []
			for y in range(tiles_numbers_height):
				temp_img = croped_org_im.crop((x*org_tile_size, y*org_tile_size,(x+1)*org_tile_size, (y+1)*org_tile_size))
				temp_rgb = average(temp_img)
				temp_array.append(self._find_tile_index_(temp_rgb))
			index_table.append(temp_array)
		return index_table

def compose_image(index_table, src_path): #index_table, [[per_row], per_column]
	if len(index_table) != tiles_numbers_width or len(index_table[0]) <= 0:
		print("Issue with the index_table")
		return
	print("start to make mosaic picture")
	img = Image.new("RGB", (size1*len(index_table), size1*len(index_table[0])))
	for x in range(len(index_table)):
		for y in range(len(index_table[0])):
			temp_index = index_table[x][y]
			temp_image = Image.open(src_path+"/thumbnail/"+str(temp_index)+".thumbnail")
			img.paste(temp_image, (x*size1, y*size1))
	img.save(OUTFILE,"JPEG")

if __name__ == '__main__':
	if len(sys.argv) <3:
		print ('Usage: %s <image> <tiles directory>\r' % (sys.argv[0],))
	else: #sys.argv[1] for image, sys.argv[2] for tiles source
		compose_image(Original_Image(sys.argv[1],Tiles(sys.argv[2]).process_tiles()).generate_index_matrix(), sys.argv[2])
		