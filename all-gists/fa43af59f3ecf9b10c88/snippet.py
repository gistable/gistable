# IMPORTS: THIS SCRIPT REQUIRES THE PACKAGES PYLAB AND MOVIEPY
# It produces this gif: http://i.imgur.com/LbU55oK.gif

from pylab import *
import moviepy.editor as mp
from moviepy.video.io.bindings import mplfig_to_npimage


# PARAMETERS OF THE CURVE AND THE GIF

curve = lambda t : ( cos(80*t) - cos(t)**3, sin(t) -  sin(80*t)**3 )

curve_latex = (r"$\left(\,\, \cos(80t) - \cos(t^3),\,\,\,"
              +r"\sin(t) -  \sin(80t)^3 \,\,\right)$")

t_min=0
t_max = 2*pi
number_of_points = 20000 

gif_name = "test.gif"
gif_duration = 5
gif_fps = 15



# PRECOMPUTE THE CURVE

times = linspace(0, 2*pi, number_of_points)
curve_x, curve_y = zip(*[curve(t) for t in times])

# INITIALIZE THE FIGURE

fig, ax = subplots(1, figsize=(4,4), facecolor='white')
ax.axis("off")
ax.set_title(fun_latex)
line, = ax.plot(curve_x, curve_y)

# ANIMATE WITH MOVIEPY

def make_frame(t):
    index_max = int( (1.0*t/clip_duration)*number_of_points)
    line.set_xdata(curve_x[:index_max])
    line.set_ydata(curve_y[:index_max])
    return mplfig_to_npimage(fig)

clip = mp.VideoClip(make_frame, duration=gif_duration)
clip = clip.fx( mp.vfx.freeze, t='end', freeze_duration=1)
clip.write_gif(gif_name, fps=gif_fps)