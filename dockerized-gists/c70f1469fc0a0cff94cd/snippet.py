"""
This creates the following GIF, where the text appears to be "embedded"
in the video and "disappears" behind rapunzel.

http://i.imgur.com/gxEHfLX.gif
"""

from moviepy.editor import *
import numpy as np
import skimage.morphology as skm


tangled = VideoFileClip("tangled.flv", audio=False)
clip = tangled.subclip((32,37.2),(32,39.7)).resize(width=360)

# 'Background' frame. We'll spot Rapunzel by comparing the frames to this background.
ref_frame = clip.get_frame(0)

text = (TextClip("MoviePy !!!", fontsize=72, font='Impact-Normal',
                 color='yellow', stroke_color='black', stroke_width=3)
       .resize(width=125)
       .on_color(size=clip.size, col_opacity=0)
       .set_duration(clip.duration))

def mask_fl(gf, t):
    """ Returns the mask around Rapunzel for the given time t """
    frame = clip.get_frame(t)
    diff = (((frame-ref_frame)**2).max(axis=2) > 10**2)
    cleaned = skm.remove_small_objects(diff, 40)
    dilated = skm.binary_dilation(cleaned, skm.diamond(2))
    return np.minimum(gf(t), 1.0-dilated)

text.mask = text.mask.fl(mask_fl, keep_duration=True)

final = CompositeVideoClip([clip, text])
final.write_gif('moviepy.gif', fps= 3*tangled.fps/5,)