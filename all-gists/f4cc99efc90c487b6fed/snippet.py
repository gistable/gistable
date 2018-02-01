"""
Example of overlaying an image on a 3D view with tvtk
"""
##
import mayavi.mlab as mlab
import numpy as np
import pylab as pl
import vtk
from tvtk.api import tvtk
##
fig = mlab.figure()
scene = fig.scene

#reader = tvtk.PNGReader()
#reader.file_name = 'img.png'
#reader.update()

img = pl.imread('img.png')
# Set alpha for all non-transparent pixels
img[img[:,:,3] > 0, 3] = 0.5
img = (img*255).astype(np.uint8)
img = np.flipud(img).copy()

def image_data_from_array(arr):
    assert arr.dtype == np.uint8
    i = tvtk.ImageImport()
    i.set_data_scalar_type_to_unsigned_char()
    i.number_of_scalar_components = 4
    i.whole_extent = (0, arr.shape[1] - 1, 0, arr.shape[0] - 1, 0, 0)
    i.set_data_extent_to_whole_extent()
    i.copy_import_void_pointer(arr, arr.nbytes)
    return i.output

image_data = image_data_from_array(img)

def fit_to(img_width, img_height, target_width, target_height):
    """
    Return new dimensions for img such that it fits completely
    in target_width/target_height
    Actually returns (new_width, new_height, -1) to be compatible with tvtk
    """
    width_factor = target_width / float(img_width)
    height_factor = target_height / float(img_height)
    if width_factor < height_factor:
        return (target_width, width_factor * img_height, -1)
    else:
        return (height_factor * img_width, target_height, -1)

imsize = (img.shape[1], img.shape[0])
#imsize = (reader.output.whole_extent[1], reader.output.whole_extent[3])

resize = tvtk.ImageResize()
#resize.input = reader.output
#resize.set_input_data(image_data) in VTK 6
resize.input = image_data
resize.resize_method = 'output_dimensions'
#resize.output_dimensions = (-1, -1, -1)
#resize.output_dimensions = fit_to(imsize[0], imsize[1], 200, 200)

mapper = tvtk.ImageMapper()
#mapper.input = reader.output
#mapper.set_input_data(reader.output) in VTK 6
mapper.input = resize.output
mapper.color_window = 255
mapper.color_level = 127

map_actor = tvtk.Actor2D()
map_actor.mapper = mapper
map_actor.position = (0,0)
# Opacity doesn't seem to be supported, see
# http://vtk.1045678.n5.nabble.com/Opacity-of-vtkActor2D-td1238026.html
map_actor.property.opacity = 0.5

renderer = scene.renderer
renderer.add_actor2d(map_actor)

window = scene.render_window

def fit_image_to_window():
    resize.output_dimensions = fit_to(imsize[0], imsize[1],
                                      window.size[0], window.size[1])
fit_image_to_window()
def on_window_modified(obj, evt):
    #print 'window size : ', window.size
    fit_image_to_window()

window.add_observer('ModifiedEvent', on_window_modified)

mlab.points3d(1,1,1)
##