# Robofont script to remove broken image paths, keeping good ones intact.
import os
f = CurrentFont()

layerOrder = ['foreground']
layerOrder.extend(f.layerOrder)

for g in f:
    for layerName in layerOrder:
        layeredGlyph = g.getLayer(layerName)
        if layeredGlyph.lib.get('com.typemytype.robofont.image', None):
            if not os.path.exists(layeredGlyph.lib['com.typemytype.robofont.image']['path']):
                print 'Removing orphan image from {} ({})'.format(layeredGlyph.name, layerName)
                del(layeredGlyph.lib['com.typemytype.robofont.image'])

print 'done'
