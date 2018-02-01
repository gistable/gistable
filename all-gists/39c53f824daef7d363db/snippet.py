import requests as req
import sys
from dateutil.parser import parse
from PIL import Image
from StringIO import StringIO

# hi8-fetch.py <date> <zoom level> <output>
# E.g.: hi8-fetch.py 2016-01-13T22:10:00 8 2016-01-13T221000-z8.png
# Fetch Himawari-8 full disks at a given zoom level.
# Valid zoom levels seem to be powers of 2, 1..16, and 20.
#
# To do:
# - Better errors (e.g., catch the "No Image" image).
# - Don't ignore seconds, and/or:
# - option to snap to nearest valid time.
# - Librarify.


# Tile size for this dataset:
width = 550
height = 550


time = parse(sys.argv[1])
scale = int(sys.argv[2])
out = sys.argv[3]


base = 'http://himawari8.nict.go.jp/img/D531106/%sd/550' % (scale)

tiles = [[None] * scale] * scale


def pathfor(t, x, y):
  return "%s/%s/%02d/%02d/%02d%02d00_%s_%s.png" \
  % (base, t.year, t.month, t.day, t.hour, t.minute, x, y)

def fetch(session, path, retries=1, verbose=False, failure='error'):
  # FIXME: this is kinda messy:
  if retries < 0:
    if failure == 'warning':
      raise Warning('Could not download %s (filling with black)')
      return np.zeros((width, height, 3))
    elif failure == 'silent':
      return np.zeros((width, height, 3))
    else: # presumed failure == 'error':
      raise IOError('Could not download %s')

  try:
    tiledata = session.get(path).content
    tile = Image.open(StringIO(tiledata))
    return tile
  except:
    if verbose:
      print('Retrying %s (%s retries left)' % (path, retries))
    return fetch(
      session,
      path,
      retries=(retries - 1),
      verbose=verbose,
      failure=failure
    )
  

sess = req.Session() # so requests will reuse the connection
png = Image.new('RGB', (width*scale, height*scale))

for x in range(scale):
  for y in range(scale):
    
    path = pathfor(time, x, y)
    tile = fetch(sess, path, retries=4, verbose=True, failure='error')
    png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))

png.save(out, 'PNG')