"""
Turn a piano MIDI file into a basic 3D animated piano video.
See the result here:


I am leaving it as a script because it is not tested on enough MIDI files yet.

Zulko 2014
This script is released under a Public Domain (Creative Commons 0) licence.

"""

import os
import numpy as np
import mido
from vapory import *
from moviepy.editor import VideoClip, AudioFileClip

MIDI_NAME = "./selec/lets_fall_in_love.mid"
MP3_NAME = MIDI_NAME[:-3]+"mp3"
VIDEO_NAME = MIDI_NAME[:-3]+"mp4"

os.system('fluidsynth piano.SF2 %s -T raw -F - | lame -r - "%s"'%(
           MIDI_NAME, MP3_NAME))


# GET INFO AND EVENTS FROM THE MIDI FILE

midi = mido.MidiFile(MIDI_NAME)
info_track = midi.tracks[0]
piano_track = midi.tracks[1]
tempo = [e.tempo for e in info_track if hasattr(e,'tempo')][0]
seconds_per_beat=1.0*tempo/10**6 
seconds_per_tick = seconds_per_beat/midi.ticks_per_beat
events = {note: [] for note in range(0,120)}

t=0
for e in piano_track:
    t += seconds_per_tick*e.time
    if e.type in ["note_on", "note_off"]:
        events[e.note].append((t, e.type, e.velocity))

def get_height(note, t):
    """ Returns the height of a given key at the given time. """

    slope = lambda t : max(0,min(1,t))

    def term(t,event):
        event_time, event_type, velocity = event
        if event_type == 'note_on':
            return -slope(100*(t-event_time))
        else:
            return +slope(100*(t-event_time))
    
    return max(0,min(1,1+sum([ term(t,e) for e in events[note]])))


# Some dimensions of the piano keys and the black "piano box"

key_w = 0.4
key_h = 1.1*key_w
key_l = 5*key_w
box_bottom = 0.2

light = LightSource([0, 1000, -1000], [1.4,1.4,1.4],'parallel',
                    'point_at',[0,0,0])
wall = Plane([0,0,1],20, Texture(Pigment('color', [1,1,1])))
ground = Plane( [0,1,0], 0, Texture( Pigment( 'color', [1,1,1]),
                                     Finish( 'phong', 0.1,
                                             'reflection',0.2,
                                             'metallic', 0.3)))
piano_box = Box([-60*key_w, 0,1-key_l-0.1], [60*key_w,box_bottom, 1.01],
                Texture( Pigment( 'color', [0,0,0]), Finish('reflection', 0.0)))

camera = Camera("location", [0, 15, -30], "look_at", [0, 0, 0], "angle", 75)
scene = Scene( camera, objects = [ ground, light, piano_box])


# COMPUTE THE COORDINATES AND COLOR OF THE DIFFERENT KEYS

def compute_key_attributes(key):
    distance_to_C4 = key-60
    octave, note = distance_to_C4//12, distance_to_C4%12
    x_coordinate = 14*octave + note + (note>4)
    color = 'black' if (note in [1,3,6,8,10]) else 'white'
    return (x_coordinate, color)

keys = range(21, 108)
keys_attributes = { k: compute_key_attributes(k) for k in keys}


def make_piano_keys(keys_heights):
    keys = []
    for key, height in keys_heights.items():
        x_c, color = keys_attributes[key]  
        x_c = x_c*(key_w*1.03)-2
        
        if color=='white':
            w, h, l, color = key_w, key_h*(1-0.7*(1-height)), key_l, [1,1,1]
        else:
            w, h, l, color = (0.47*key_w, key_h*(1.5-0.4*(1-height)),
                              0.6*key_l, [0,0,0])
        keys.append(Box([x_c-w, box_bottom,1-l], [x_c+w,box_bottom+h,1],
                        Texture( Pigment( 'color', color),
                                 Finish('ambient', 0.2, 'brilliance',0.3))))
    return keys


# WE KNOW DEFINE EXACTLY THE FRAME AT TIME t, AND ASSEMBLE THE VIDEO.

def make_frame(t):
    keys_heights = {k: get_height(k,t) for k in keys}
    newscene = scene.add_objects(make_piano_keys(keys_heights))
    newscene.camera = Camera( "location", [0, 10, -25], "look_at", [0, 0, 0],
                              "angle", 70)
    return newscene.render(width=1000, height=100, antialiasing=0.001)


audio = AudioFileClip(MP3_NAME)
clip = VideoClip(make_frame, duration = audio.duration).subclip(.05)
clip.write_videofile(VIDEO_NAME, fps=30, bitrate='8000k', audio=MP3_NAME)