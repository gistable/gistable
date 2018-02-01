# Result: http://i.imgur.com/thrh1TU.gif

from moviepy.editor import *

# We start with a looping gif, and we will add some text
clip = VideoFileClip("eugene.gif").speedx(0.7) # slow down a little

txt = (TextClip("Hey", fontsize=78, font='Impact-Normal',
                     color='yellow', stroke_color='black',
                     stroke_width=3, kerning=1.5)
       .resize(width=60)
       .set_pos((20,30)))

final = CompositeVideoClip([clip,txt]).set_duration(clip.duration)
final.write_gif('hey_txt.gif')