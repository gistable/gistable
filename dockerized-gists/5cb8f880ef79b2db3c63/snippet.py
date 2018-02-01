#
# This Python script makes a summary of a football game by cutting
# the video around the 10 % loudest moments, which generally 
# include the goals and other important events.
# For more details, see this blog post:
# http://zulko.github.io/blog/2014/07/04/automatic-soccer-highlights-compilations-with-python/
#
# LICENCE: Creative Commons 0 - Public Domain
# I, the author of this script, wave any rights and place this work in the public domain.
#

import numpy as np # for numerical operations
from moviepy.editor import VideoFileClip, concatenate

clip = VideoFileClip("soccer_game.mp4")
cut = lambda i: clip.audio.subclip(i,i+1).to_soundarray(fps=22000) 
volume = lambda array: np.sqrt(((1.0*array)**2).mean())
volumes = [volume(cut(i)) for i in range(0,int(clip.audio.duration-2))]
averaged_volumes = np.array([sum(volumes[i:i+10])/10
                             for i in range(len(volumes)-10)])

increases = np.diff(averaged_volumes)[:-1]>=0
decreases = np.diff(averaged_volumes)[1:]<=0
peaks_times = (increases * decreases).nonzero()[0]
peaks_vols = averaged_volumes[peaks_times]
peaks_times = peaks_times[peaks_vols>np.percentile(peaks_vols,90)]

final_times=[peaks_times[0]]
for t in peaks_times:
    if (t - final_times[-1]) < 60:
        if averaged_volumes[t] > averaged_volumes[final_times[-1]]:
            final_times[-1] = t
    else:
        final_times.append(t)

final = concatenate([clip.subclip(max(t-5,0),min(t+5, clip.duration))
                     for t in final_times])
final.to_videofile('soccer_cuts.mp4') # low quality is the default