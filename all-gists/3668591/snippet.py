'''
Texture atlas generator / Kalio.net
klibs commit: 709551bcf617976a19e6105165eda9524007fc08
Copyright 2012 Kalio Ltda. 

Requirements: 
 - PIL: http://www.pythonware.com/products/pil/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

'''

import sys
from stat import *
import os
import re
from PIL import Image
import math
import json
import getopt
from multiprocessing import Pool
import pprint
import logging
log = logging.getLogger('texture_atlas')

# ----------------------------------------------------------------------

PVR_CMD = "/Developer/Platforms/iPhoneOS.platform/Developer/usr/bin/texturetool -m -e PVRTC -f PVR --channel-weighting-perceptual --bits-per-pixel-4 -o "

RESAMPLE_FILTER = Image.ANTIALIAS   # NEAREST, BILINEAR, BICUBIC, ANTIALIAS   (in order of quality)

F_COMPRESS_PVR = '_COMPRESS_PVR'
F_NO_COMPRESS  = '_NO_COMPRESS'
F_NO_ATLAS     = '_NO_ATLAS'
F_NO_RESIZE    = '_NO_RESIZE'   
F_NO_TRIM      = '_NO_TRIM'
F_NO_MARGIN    = '_NO_MARGIN'

SUBFOLDER_FLAGS = [
    F_COMPRESS_PVR,
    F_NO_COMPRESS,
    F_NO_ATLAS,
    F_NO_RESIZE,
    F_NO_TRIM,
    F_NO_MARGIN,
    ]

ALLOWED_IMAGE_EXTENSIONS = [
    '.png',
]

IGNORED_FOLDERS = [
    '_tmp', 
    'tmp',
    'temp',
    '_temp',
]

COMPRESS_PVR = 'pvr'

# ----------------------------------------------------------------------

def prepare_batch(folder_path, folder_name, env):
    files = []
    flags = []
    folder = folder_path + '/' + folder_name
    for f in os.listdir(folder): 
        full = os.path.join(folder, f)
        ext = os.path.splitext(f)[1].lower()
        mode = os.stat(full)[ST_MODE]
        if S_ISDIR(mode) and f in SUBFOLDER_FLAGS:
            flags.append(f)
        elif S_ISREG(mode) and ext in ALLOWED_IMAGE_EXTENSIONS:
            files.append(folder_name + '/' + f)
    log.info(' adding %s: %i frames, (%s)', folder_name, len(files), str(flags))
    return (folder_name, folder_path, flags, env, files) 

def prepare_batches(folder, env): 
    batches = []
    folder_path = os.path.dirname(folder)
    folder_name = os.path.basename(folder)
    # make a batch for the folder
    batches.append(prepare_batch(folder_path, folder_name, env))
    # and also for each subdir
    for f in os.listdir(folder): 
        full = os.path.join(folder, f)
        mode = os.stat(full)[ST_MODE]
        if S_ISDIR(mode) and f not in SUBFOLDER_FLAGS and f not in IGNORED_FOLDERS:
            batches.append(prepare_batch(folder_path, folder_name + '/' + f, env))        
    return batches

# ----------------------------------------------------------------------

def bt_insert(node, image, w, h, trim, atlas_size, margin_size): 
    # [left, right, (x,y,w,h), trim, image]
    #   0      1        2        3     4
    if node[0] and node[1]: 
        return (bt_insert(node[0], image, w, h, trim, atlas_size, margin_size) 
                or bt_insert(node[1], image, w, h, trim, atlas_size, margin_size))
    else: 
        # occupied
        if node[4]: 
            return False
        nx,ny,nw,nh = node[2]  # node available space
        cw = w
        ch = h
        if trim: 
            tl, tt, tr, tb = trim
            cw -= ( tl + tr )
            ch -= ( tt + tb )
        # too small
        if nw < cw or nh < ch: 
            return False
        # fits perfectly
        if nw == cw and nh == ch: 
            node[3] = trim
            node[4] = image
            return True
        # create children and split space
        node[0] = bt_new(atlas_size, margin_size)
        node[1] = bt_new(atlas_size, margin_size)
        dw = nw - cw
        dh = nh - ch
        if dw > dh: 
            # vertical split
            node[0][2] = (nx + margin_size,      ny, cw,                       nh)
            node[1][2] = (nx + margin_size + cw, ny, nw - (cw + margin_size) , nh)
        else: 
            # horizontal split
            node[0][2] = (nx, ny + margin_size,      nw, ch)
            node[1][2] = (nx, ny + ch + margin_size, nw, nh - ( ch + margin_size ))
        return bt_insert(node[0], image, w, h, trim, atlas_size, margin_size)

def bt_flatten(node): 
    ''' Walks the tree and converts it to a list of (image, x, y, w, h, trim)
    '''
    if node[4]: 
        return [(node[4], node[2][0], node[2][1], node[2][2], node[2][3], node[3])]
    else:
        out = []
        for branch in [0,1]:             
            if node[branch]: 
                out.extend(bt_flatten(node[branch]))
        return out

def bt_new(atlas_size, margin_size): 
    ''' node = [left tree, right tree, (x,y,w,h), trim, image]
    '''
    return [None, 
            None, 
            (0,
             0,
             atlas_size,
             atlas_size), 
            None, 
            None]

def get_alpha_trim(image):
    ''' returns bounding box with transparent pixels trimming (left, top, right, bottom) 
    ''' 
    w, h = image.size
    mode = image.mode
    if mode != 'RGBA': 
        return (0,0,w,h)
    # TODO: try to read from cache
    i = 0
    col = 0
    row = 0
    left,top = w,h
    right,bottom = 0,0
    pixel_found = False
    for p in image.getdata(): 
        r,g,b,a = p
        if a != 0: 
            pixel_found = True
            col = i % w
            row = int(i / w)
            if col < left: left = col
            if col > right: right = col
            if row < top: top = row
            if row > bottom: bottom = row
        i += 1
    if pixel_found: 
        return (left, top, w-right-1, h-bottom-1)
    else: 
        return (0, 0, w-2, h-2)   # transparent: return the 2x2 top left corner

def read_image_data(image_path):
    ''' result: (image_path, w, h, trim)
    '''
    im = Image.open(image_path)
    w, h = im.size
    trim = get_alpha_trim(im)    
    return (image_path, w, h, trim)

def get_cached_image_data(image_path, cache): 
    result =  cache.get(image_path)
    if not result: 
        log.error('IMAGE MISSING FROM CACHE: %s' % image_path)
    return result

def load_image_dimensions(images, folder_path, resize_scale, flags, cache): 
    ''' result: [ (image, w, h, trim), ... ]
    '''
    dimensions = []
    for f in images: 
        trim = None
        image_path, w, h, trim_data = get_cached_image_data(folder_path + '/' + f, cache)
        if F_NO_TRIM not in flags:
            trim = trim_data
            log.debug('trim: %s', str(trim))
        if resize_scale != 100: 
            w = int(w * resize_scale / 100.0)
            h = int(h * resize_scale / 100.0)
        if trim != None:
            trim = map(lambda i: int(math.floor(i * resize_scale / 100.0)), trim)
        dimensions.append((f, w, h, trim))
    dimensions.sort(lambda x,y: y[2] - x[2] if y[1] == x[1] else y[1] - x[1])
    return dimensions

def prepare_atlas(batch):
    ''' batch:  ( folder_name, folder_path, [flags], {env}, [images] )
        result: [ (aname, folder_path, output_dir, aw, ah, compress_format, [(image, x, y, w, h, trim) ...]) ...]
    ''' 
    folder_name, folder_path, flags, env, images = batch
    output_dir = env.get('output_dir')
    atlas_size = env.get('atlas_size')
    margin_size = env.get('margin_size')
    image_cache = env.get('image_cache')
    atlas = []    

    resize_scale = env.get('resize_scale', 100.0)
    if F_NO_RESIZE in flags: 
        resize_scale = 100.0

    if F_NO_MARGIN in flags: 
        margin_size = 0

    compress_format = env.get('compress_format', None)
    if F_COMPRESS_PVR in flags:
        compress_format = COMPRESS_PVR
    elif F_NO_COMPRESS in flags:
        compress_format = None
        
    dimensions = load_image_dimensions(images, folder_path, resize_scale, flags, image_cache)

    seq = 0
    if F_NO_ATLAS in flags:
        for f, w, h, trim in dimensions: 
            x = 0
            y = 0            
            aw = w
            ah = h
            aname = folder_name.replace('/', '_') + '-' + str(seq) + '.png'
            seq += 1
            # F_NO_TRIM implied for F_NO_ATLAS
            atlas.append( (aname, folder_path, output_dir, aw, ah, compress_format, [(f, x, y, w, h, None)]) )
    else: 
        aw = atlas_size
        ah = atlas_size
        bins = [ bt_new(atlas_size, margin_size) ]
        for f, w, h, trim in dimensions: 
            if F_NO_TRIM in flags: 
                trim = None
            inserted = False
            for b in bins:                 
                if bt_insert(b, f, w, h, trim, atlas_size, margin_size): 
                    inserted = True
                    break
            if not inserted:
                new_node = bt_new(atlas_size, margin_size)
                bins.append(new_node)
                if not bt_insert(new_node, f, w, h, trim, atlas_size, margin_size): 
                    assert False, "image %s,%i,%i could not be inserted in a clean new bin" % (f,w,h)
        seq += 1
        for b in bins: 
            aname = folder_name.replace('/', '_') + '-' + str(seq) + '.png'
            seq += 1
            atlas.append( (aname, folder_path, output_dir, aw, ah, compress_format, bt_flatten(b)) )
    return atlas

# ----------------------------------------------------------------------

def write_atlas(atlas): 
    aname, folder_path, output_dir, aw, ah, compress_format, frames = atlas
    full_aname_png = output_dir + '/' + aname
    if compress_format == COMPRESS_PVR: 
        aname = aname + '.pvrtc'
    full_aname = output_dir + '/' + aname
    frame_locations = {}
    aim = Image.new('RGBA', (aw, ah))    # what about other types?
    for i in frames: 
        #log.debug('    i:%s', str(i))
        f, x, y, w, h, trim = i
        
        im = Image.open(folder_path + '/' + f)
        iw, ih = im.size
        if trim: 
            tl, tt, tr, tb = trim
        else:
            tl, tt, tr, tb = 0,0,0,0
        rw = w+tl+tr
        rh = h+tt+tb
        log.debug('%s (%i -> %i) -> %s', f, iw, rw, aname)
        if iw != rw or ih != rh:
            im = im.resize((rw, rh), RESAMPLE_FILTER)                    
        if trim: 
            im = im.crop((tl, tt, w+tl, h+tt))
            log.debug('   w:%i h:%i - cropping %i %i %i %i - size:%s', w, h, tl, tt, tr, tb, str(im.size))
        aim.paste(im, (x, y, x+w, y+h))
        frame_locations[f] = (aname, aw, ah, x, y, w, h, trim)
    aim.save(full_aname_png, "PNG")
    if compress_format == COMPRESS_PVR: 
        os.system(PVR_CMD + full_aname + ' ' + full_aname_png)
        # +atlasName+".pvrtc "+(COMPRESS_PREVIEW?" -p "+atlasName+".pvrtc.png ":"")+atlasName).execute() 
    return frame_locations       

# ----------------------------------------------------------------------

def create_metadata(frame_locations, path_prefix): 
    ''' frame_locations[frame_path] = (aname, aw, ah, x, y, w, h, trim)
    ''' 
    metadata = {}
    keys = frame_locations.keys()
    keys.sort()      # below algorithm requires sorted ascending
    for f in keys: 
        aname, aw, ah, x, y, w, h, trim = frame_locations[f]
        # Image parts:  name[-flags][-angle][-frame].png 
        #   flags: l = loop
        #   angle: \d\d
        #   frame: \d\d
        # common-images/pointers/hud_pointer_steam-l-10.png
        dn = os.path.dirname(f)
        bf = os.path.splitext(os.path.basename(f))[0]
        bfp = re.compile('([^-]*)-?(l)?-?(\d\d)?-?(\d\d)?')
        entry, loop, angle, frame = bfp.match(bf).groups()
        entry = os.path.join(dn, entry)   # keep relative directory for uniqueness
        if loop != None: 
            loop = True
        if angle != None:
            if frame != None: 
                frame = int(frame)
                angle = int(angle)
            else:
                frame = int(angle)
                angle = 0
        else:
            angle = 0
            frame = 0
        if trim: 
            tl, tt, tr, tb = trim
        else:
            tl, tt, tr, tb = 0,0,0,0
        fdata = {'path' : os.path.normpath(os.path.join(path_prefix, aname)), 
                 'width' : aw, 
                 'height' : ah, 
                 'rect' : [x,y,w,h],
                 'trim' : [tl,tt,tr,tb],
                 #  'bf': bf              # debug
                 }
        e = metadata.get(entry)
        if not e:
            e = {'name' : entry, 
                 'loop' : 1 if loop else 0, 
                 'framesets': [[]], 
                 }
            metadata[entry] = e
        fs = e['framesets']
        # suppose file names are sorted, so always append
        if len(fs) > angle:
            fs[angle].append(fdata)
        else:
            fs.append([fdata])
    return metadata.values()

# ----------------------------------------------------------------------

usage = '''
Usage: texture_atlas.py [options] input_directory output_directory output_metadata_filename

Options: 

  --atlas-size | -a 
    atlas size in pixels. power-of-2 please. 

  --debug | -d 
    debug logging... very verbose. 
  
  --compress FORMAT | -c FORMAT
    sets the default to compress with FORMAT. Can be overriden by folder flags. 
  
  --processes N | -p N
    number of simultaneous processes to run (default 8)

  --resize PERCENT | -r PERCENT
    resizes the images (integer number only, 100 = no resize).

  --verbose | -v
    enables debug logging. 


Images in subfolders in the input_directory are processed in their
separate atlas group. 

Image filename format:  name[-flags][-angle][-frame].png
  flags: 
    l: part of a loopable sequence

  eg: 
    name-l-01.png   # frame 01 of loopable animation
    name-01-03.png  # frame 03 of angle 01

A folder (including the root) can contain flags that apply to that folder.

Folder flags: 
  _COMPRESS_FORMAT : compress using FORMAT, where FORMAT can be: PVR2... (TODO)
  _NO_COMPRESS     : does not compress files
  _NO_ATLAS        : just keep the original image, including size, as the output.
  _NO_RESIZE       : ignore resize
  _NO_TRIM         : does not trim transparent parts of the images.
  _NO_MARGIN       : no margin when assembling the atlas. 

'''

if __name__ == '__main__': 
    verbose = False
    debug = False

    atlas_size = 1024
    margin_size = 2
    compress_format = None
    processes = 8
    resize_scale = 100.0

    try: 
        opts, args = getopt.getopt(sys.argv[1:], 
                                   'a:c:dm:p:r:v',
                                   ['atlas=',
                                    'compress=', 
                                    'debug',
                                    'margin=',
                                    'processes=',
                                    'resize=',
                                    'verbose', 
                                    ])
    except getopt.GetoptError, err: 
        print str(err)
        print usage
        sys.exit(2)

    if len(args) != 3: 
        print usage
        sys.exit(1)
        
    for o, a in opts: 
        if o in ('-a', '--atlas-size'): 
            atlas_size = int(a)
        elif o in ('-c', '--compress'): 
            compress_format = a
        elif o in ('-d', '--debug'): 
            debug = True
        elif o in ('-m', '--margin'):
            margin_size = int(a)
        elif o in ('-p', '--processes'): 
            processes = int(a)
        elif o in ('-r', '--resize'): 
            resize_scale = float(a)
        elif o in ('-v', '--verbose'): 
            verbose = True
        else: 
            assert False, ("invalid option: %s" % o)


    pp = pprint.PrettyPrinter(indent=2)
    if debug: 
        logging.basicConfig(level=logging.DEBUG)
    elif verbose: 
        logging.basicConfig(level=logging.INFO)
    else: 
        logging.basicConfig(level=logging.ERROR) 

    input_dir = args[0]
    output_dir = args[1]
    output_file = args[2]    
    img_data_cache = {}

    env = {
        'resize_scale'    : resize_scale, 
        'compress_format' : compress_format,
        'atlas_size'      : atlas_size,
        'input_dir'       : input_dir,
        'output_dir'      : output_dir,
        'margin_size'     : margin_size,
        'image_cache'     :img_data_cache,
        }

    log.info('\ninput_dir: %s\noutput_dir: %s\noutput_file: %s\n', input_dir, output_dir, output_file)
    log.debug('  env:%s', str(env))

    # 1. walk directories and prepare batch jobs:
    #    list of files, flags
    log.info('---- 1. BATCHES -----------------------------------------------')
    batches = prepare_batches(input_dir, env)
    log.debug('\n' + pp.pformat(batches))

    pool = Pool(processes=processes)

    # 2. multiproc: read imaages metadata and calculate trim 
    log.info('---- 2. CACHE IMAGE INFO --------------------------------------');
    img_paths = []
    for b in batches:         
        img_paths = img_paths + map(lambda x: '%s/%s' % (b[1],x) , b[4])
    #log.debug('\n' + pp.pformat(img_paths))
    img_data = pool.map(read_image_data, img_paths)
    for i in img_data: 
        img_data_cache[i[0]] = i  # load the cache map
    #log.debug('\n' + pp.pformat(img_data_cache))

    # 3. multiproc: identify each texture properties and calculate atlas metadata
    log.info('---- 3. PREPARE ATLAS -----------------------------------------')
    atlas = pool.map(prepare_atlas, batches)
    atlas = reduce(lambda x,y: x+y, atlas)   # concat all results 
    #log.debug('\n' + pp.pformat(atlas))

    # 4. multiproc: execute atlas tiling creating output images
    log.info('---- 4. WRITE ATLAS -------------------------------------------')
    log.info(' writing %i atlas files', len(atlas))
    frame_locations = pool.map(write_atlas, atlas)
    frame_locations = reduce(lambda x,y: dict(x.items() + y.items()), frame_locations)
    #log.debug('\n' + pp.pformat(frame_locations))

    # 5. create metadata from frame locations and write it
    log.info('---- 5. COMPILE METADATA --------------------------------------')
    path_prefix = os.path.relpath(output_dir, os.path.dirname(output_file))
    metadata = create_metadata(frame_locations, path_prefix)
    #log.debug('\n' + pp.pformat(metadata))
    of = open(output_file, 'w')
    of.write(json.dumps(metadata, indent=2, sort_keys=True))
    of.close()
