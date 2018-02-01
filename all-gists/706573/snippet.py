from struct import unpack
import Image

tag_types = { 0 : 'End',
			  1 : 'Byte',
			  2 : 'Short',
			  3 : 'Int',
			  4 : 'Long',
			  5 : 'Float',
			  6 : 'Double',
			  7 : 'Byte array',
			  8 : 'String',
			  9 : 'List',
			  10 : 'Compound'}

# Read number and type of list items and print them
def read_list_payload(chunk):
	list_item_type = ord(chunk.read(1))
	list_length = unpack('>l', chunk.read(4))[0]

	print "%d items of type %s" % (list_length, tag_types[list_item_type])
	
def read_byte(chunk):
	return ord(chunk.read(1))

def read_short(chunk):
	return unpack('>h', chunk.read(2))[0]
	
def read_int(chunk):
	return unpack('>l', chunk.read(4))[0]
			
def read_long(chunk):
	return unpack('>q', chunk.read(8))[0]
			
def read_byte_array(chunk):
	length = read_int(chunk)
	print "Array length: %d" % length
	payload = chunk.read(length)
	return payload
	
def read_compound(chunk):
	payload = []
	tag = read_tag(chunk)
	payload.append(tag)
	tag_type = tag[0]
	while (tag_type > 0):
		tag = read_tag(chunk)
		payload.append(tag)
		tag_type = tag[0]
	
	print "Read %d elements in compound" % len(payload)

	return payload
	
def read_string(chunk):
	str_length = unpack('>h', chunk.read(2))[0]
	if (str_length > 0):
		str = chunk.read(str_length)
		#print "Name: %s" % name
	else:
		str = None
	return str
	
# Read entire tag
def read_tag(chunk):
	type = ord(chunk.read(1)) # Chunk starts with "10" byte
	print "Found tag type: %s" % (tag_types[type], )
	if (type > 0):
		name = read_string(chunk)
		if (name != None):
			print "Name: %s" % name
	else:
		name = ''
		
	payload = None
	# Read payload of each tag. "0" tag has no payload
	if (type == 1):
		payload = read_byte(chunk)
	elif (type == 2):
		payload = read_short(chunk)
	elif (type == 3):
		payload = read_int(chunk)
	elif (type == 4):
		payload = read_long(chunk)
	elif (type == 5): # no separate float for now
		payload = read_long(chunk)
	elif (type == 6): # no separate double for now
		payload = read_long(chunk)
	elif (type == 7):
		payload = read_byte_array(chunk)
	elif (type == 8):
		payload = read_string(chunk)
	elif (type == 9):
		payload = read_list_payload(chunk)
	elif (type == 10):
		payload = read_compound(chunk)
		
	return (type, name, payload)

chunk = open('c.-d.18', 'r')

output = read_tag(chunk)

print output[0]

for level in output[2]:
	# skip end tags
	if (level[0] == 0): 
		continue
		
	for tag in level[2]:
		if (tag[0] == 0):
			continue
		print tag[1]
		if tag[1] == "Blocks":
			blocks = tag[2]
			
print "Blocks retrieved"
print "Blocks count: %d" % len(blocks)

y = 16

# Print map by block ID
for z in range(0, 16):
  for x in range (0, 16):
    print ord(blocks[ y + ( z * 128 + (x * 128 * 16)) ]),
  print 
  
def get_cropbox(x, y):
	return (x*16, y*16, x*16 + 16, y*16 + 16)

terrain = Image.open("terrain.png")

stone = terrain.crop(get_cropbox(0,0))
dirt = terrain.crop(get_cropbox(2,0))
gravel = terrain.crop(get_cropbox(3,1))
sand = terrain.crop(get_cropbox(2,1))
coal = terrain.crop(get_cropbox(2,2))
iron = terrain.crop(get_cropbox(1,2))
gold = terrain.crop(get_cropbox(0,2))
redstone = terrain.crop(get_cropbox(3,3))
diamond = terrain.crop(get_cropbox(2,3))

map = Image.new("RGB", (256, 256))

# Draw map
for x in range(0, 16):
  for z in range (0, 16):
	block_id = ord(blocks[ y + ( z * 128 + (x * 128 * 16)) ])
	if block_id == 1:
		map.paste(stone, get_cropbox(x, z))
	elif block_id == 3:
		map.paste(dirt, get_cropbox(x, z))
	elif block_id == 13:
		map.paste(gravel, get_cropbox(x, z))
	elif block_id == 12:
		map.paste(sand, get_cropbox(x, z))
	elif block_id == 16:
		map.paste(coal, get_cropbox(x, z))
	elif block_id == 15:
		map.paste(iron, get_cropbox(x, z))
	elif block_id == 14:
		map.paste(gold, get_cropbox(x, z))
	elif block_id == 73:
		map.paste(redstone, get_cropbox(x, z))
	elif block_id == 56:
		map.paste(diamond, get_cropbox(x, z))
	
try:
	map.save('.\map.png', 'PNG')
except:
	print "Something went wrong on save"