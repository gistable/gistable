#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
GStreamer Tutorial 1: Simple Project
In this tutorial we will receive an mp3 file from our harddrive, manipulate
with an equalizer element, and output that to our speakers.

   ------------------------pipeline-------------------------
   |        |           |                 |                |
filesrc -> mad -> audioconvert -> equalizer-3bands -> autoaudiosink

"""

import gst

# Create the pipeline for our elements.
pipeline = gst.Pipeline('pipeline')

# Create the elements for our project.
audio_source = gst.element_factory_make('filesrc', 'audio_source')
decode = gst.element_factory_make('mad', 'decode')
convert = gst.element_factory_make('audioconvert', 'convert')
equalizer = gst.element_factory_make('equalizer-3bands', 'equalizer')
audio_sink = gst.element_factory_make('autoaudiosink', 'audio_sink')

# Ensure all elements were created successfully.
if (not pipeline or not audio_source or not decode or not convert or 
    not equalizer or not audio_sink):
    print 'Not all elements could be created.'
    exit(-1)

# Configure our elements.
audio_source.set_property('location', 'myfile.mp3')
equalizer.set_property('band1', -24.0)
equalizer.set_property('band2', -24.0)

# Add our elements to the pipeline.
pipeline.add(audio_source, decode, convert, equalizer, audio_sink)

# Link our elements together.
if (not gst.element_link_many(audio_source, decode, convert, equalizer, audio_sink)):
    print "Elements could not be linked."
    exit(-1)

# Set our pipelines state to Playing.
pipeline.set_state(gst.STATE_PLAYING)

# Wait until error or EOS.
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(gst.CLOCK_TIME_NONE,
    gst.MESSAGE_ERROR | gst.MESSAGE_EOS)
print msg

# Free resources.
pipeline.set_state(gst.STATE_NULL)