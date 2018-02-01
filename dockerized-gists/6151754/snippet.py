# MCEdit Filter by CrushedPixel
# http://youtube.com/CrushedPixel
# source: http://www.mediafire.com/view/o6af3cuo45pj9pn/CPTerraformingClay.py

displayName = "Natural Blocks to Clay"

inputs = ()

blocks = [
  ['35:0', 80],  # white stained clay
  ['35:1'],       # orange
  ['35:2'],        # magenta
  ['35:3'],         # light blue
  ['35:4', 12, 24, 5], # yellow
  ['35:5', 2],      # lime
  ['35:6'],         # pink
  ['35:7', 17, 88], # gray
  ['35:8'],         # light gray
  ['35:9', 1],     # cyan
  ['35:10'],      # purple
  ['35:11', 49], # blue
  ['35:12', 3],  # brown
  ['35:13', 18], # green
  ['35:14', 87], # red
  ['35:15'],     # black
  [4]           # normal clay
]

blocks = enumerate(blocks)

def perform(level, box, options):

  for color, id_list in blocks:
    for x in xrange(box.minx, box.maxx):
      for y in xrange(box.miny, box.maxy):
        for z in xrange(box.minz, box.maxz):
          # finds for the id OR the string with the data value, in the array
          block_id = level.blockAt(x, y, z)
          block_data = level.blockDataAt(x, y, z)
          if block_id in id_list or str(block_id) + ':' + str(block_data) in id_list:
            if color == 16:
              level.setBlockAt(x, y, z, 82)
              level.setBlockDataAt(x, y, z, 0)
            else:
              level.setBlockAt(x, y, z, 159)
              level.setBlockDataAt(x, y, z, color)
              
  level.markDirtyBox(box)