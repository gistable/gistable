"""
Model of a Zombie outbreak in France, starting in Grenoble

This is a rewrite from this blog post by Max Berrgren:

http://maxberggren.github.io/2014/11/27/model-of-a-zombie-outbreak/

with a different country, a slightly different model, and different
libraries. The map of population density is taken from Wikimedia Commons

Model
------

I use a modified SIR model. "Modified" because I didn't fully understood
SIR when I wrote the code. The population is divided in 3 categories:

S = Sane people
I = People who have been beaten, they are Incubating, soon-to-be Zombies
R = Rampaging Zombies, who bite sane people.

The rules are as follows:
- Sane citizen don't move (the army forbids it) until they get biten
  by a zombie
- Biten people move fast (they don't control themselves) and after
  some time they are tranformed into zombies. As a consequence, some
  cities like Paris will be contaminated by these people, ahead of the
  main zombie wave.
- Zombies walk slowly and bite people.

All units are really much arbitrary and tuned to make a sexy animation.

Result
-------
See the resulting animation here:
http://i.imgur.com/BsgBP4g.gif

Blue represents sane citizen, red zombies, and green/yellow infected
people. Looks like Maubeuge, in the north-east, will (finally) be the
place to go.

Requirements:
-------------

Numpy for numerical computations.
Scipy for the convolution that computes the dispersion
MoviePy for the animation (requires FFMPEG installed)
ImageMagick if you want to make a gif

Copyright Zulko 2014, Licence Public Domain (Creative Commons 0)

@NSA, @DGSE => This is just for science. No plans.
"""


import urllib
import numpy as np
from scipy.ndimage.filters import convolve
import moviepy.editor as mpy


#### RETRIEVE THE MAP FROM THE WEB


filename = ("http://upload.wikimedia.org/wikipedia/commons/a/aa/"
            "France_-_2011_population_density_-_200_m_%C3%"
            "97_200_m_square_grid_-_Dark.png")
urllib.urlretrieve(filename, "france_density.png")


#### PARAMETERS AND CONSTANTS


infection_rate = 0.3
incubation_rate = 0.1

dispersion_rates  = [0, 0.07, 0.03] # for S, I, R

# This kernel models how the people/zombies at one position
# spread to the neighboring positions
dispersion_kernel = np.array([[0.5, 1 , 0.5],
                                [1  , -6, 1],
                                [0.5, 1, 0.5]]) 

france = mpy.ImageClip("france_density.png").resize(width=400)
SIR = np.zeros( (3,france.h, france.w),  dtype=float)
SIR[0] = france.get_frame(0).mean(axis=2)/255

start = int(0.6*france.h), int(0.737*france.w)
SIR[1,start[0], start[1]] = 0.8 # infection in Grenoble at t=0

dt = 1.0 # one update = one hour of real time
hours_per_second= 7*24 # one second in the video = one week in the model
world = {'SIR':SIR, 't':0}


##### MODEL


def infection(SIR, infection_rate, incubation_rate):
    """ Computes the evolution of #Sane, #Infected, #Rampaging"""
    S,I,R = SIR
    newly_infected = infection_rate*R*S
    newly_rampaging = incubation_rate*I
    dS = - newly_infected
    dI = newly_infected - newly_rampaging
    dR = newly_rampaging
    return np.array([dS, dI, dR])

def dispersion(SIR, dispersion_kernel, dispersion_rates):
    """ Computes the dispersion (spread) of people """
    return np.array( [convolve(e, dispersion_kernel, cval=0)*r
                       for (e,r) in zip(SIR, dispersion_rates)])

def update(world):
    """ spread the epidemic for one time step """
    infect = infection(world['SIR'], infection_rate, incubation_rate)
    disperse = dispersion(world['SIR'], dispersion_kernel, dispersion_rates)
    world['SIR'] += dt*( infect + disperse)
    world['t'] += dt

    
# ANIMATION WITH MOVIEPY


def world_to_npimage(world):
    """ Converts the world's map into a RGB image for the final video."""
    coefs = np.array([2,25,25]).reshape((3,1,1))
    accentuated_world = 255*coefs*world['SIR']
    image = accentuated_world[::-1].swapaxes(0,2).swapaxes(0,1)
    return np.minimum(255, image)

def make_frame(t):
    """ Return the frame for time t """
    while world['t'] < hours_per_second*t:
        update(world)
    return world_to_npimage(world)
    

animation = mpy.VideoClip(make_frame, duration=25)
# You can write the result as a gif (veeery slow) or a video:
#animation.write_gif(make_frame, fps=15)
animation.write_videofile('test.mp4', fps=20)