from __future__ import print_function
import bpy
from functools import reduce

D = bpy.data

OUT_DIR = '/tmp'

f2=open(OUT_DIR+'/markers.log', 'w')
for clip in D.movieclips:
    print('processing clip {0}...'.format(clip.name), file=f2)
    width=clip.size[0]
    height=clip.size[1]
    for ob in clip.tracking.objects:
        print('processing object {0}...'.format(ob.name), file=f2)
        for track in ob.tracks:
            print('processing track {0}...'.format(track.name), file=f2)
            fn = OUT_DIR+'/data/{0}_{1}_tr_{2}.csv'.format(clip.name.split('.')[0], ob.name, track.name)
            with open(fn, 'w') as f:
                framenum = 0
                while framenum < clip.frame_duration:
                    markerAtFrame = track.markers.find_frame(framenum)
                    if markerAtFrame:
                        coords = markerAtFrame.co.xy
                        corners = markerAtFrame.pattern_corners
                        corners = reduce(lambda x,y: x+y, map( list, corners ))
                        corners = [
                            corners[0]*width, corners[1]*height,
                            corners[2]*width, corners[3]*height,
                            corners[4]*width, corners[5]*height,
                            corners[6]*width, corners[7]*height  ]
                        print('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}'.format(framenum, coords[0]*width, coords[1]*height, *corners), file=f)
                    framenum += 1
f2.close()
