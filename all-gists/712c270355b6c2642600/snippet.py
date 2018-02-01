#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
GStreamer Tutorial 3: Splitting multimedia
In this tutorial we will stream a video from a website using 
the playbin2 element, split the audio into different element 
chains where we play the audio, show a waveform visualization
of the audio, and record the audio.

            ------------------------------------------output_bin-------------------------------------------
            |                                  -> queue -> autoaudiosink                                  |
playbin2 -> | decodebin -> audioconvert -> tee -> queue -> wavescope -> ffmpegcolorspace -> autovideosink |
            |                                  -> queue -> lamemp3enc -> filesink                         |
            -----------------------------------------------------------------------------------------------
"""

import gst

# Callback function to link decodebin to autoconvert.
def on_new_decoded_pad(dbin, pad, islast):
    decode = pad.get_parent()
    pipeline = decode.get_parent()
    convert = pipeline.get_by_name('convert')
    decode.link(convert)
    print 'linked!'

# Create the pipeline and bin
output_bin = gst.Bin('output_bin')

# Create the elements.
media_source = gst.element_factory_make('playbin2', 'media_source')
decode = gst.element_factory_make('decodebin', 'decode')
convert = gst.element_factory_make('audioconvert', 'convert')
tee = gst.element_factory_make('tee', 'tee')
audio_queue = gst.element_factory_make('queue', 'audio_queue')
audio_sink = gst.element_factory_make('autoaudiosink', 'audio_sink')
wavescope_queue = gst.element_factory_make('queue', 'wavescope_queue')
wavescope_visual = gst.element_factory_make('wavescope', 'wavescope_visual')
wavescope_convert = gst.element_factory_make('ffmpegcolorspace', 'wavescope_convert')
wavescope_sink = gst.element_factory_make('autovideosink', 'wavescope_sink')
file_queue = gst.element_factory_make('queue', 'file_queue')
file_encode = gst.element_factory_make('lamemp3enc', 'file_encode')
file_sink = gst.element_factory_make('filesink', 'file_sink')

# Ensure all elements were created successfully.
if (not output_bin or not media_source or not decode or not convert or 
    not tee or not audio_queue or not audio_sink or not wavescope_queue or
    not wavescope_visual or not wavescope_convert or not wavescope_sink or 
    not file_queue or not file_encode or not file_sink):
    print 'Elements could not be linked.'
    exit(-1)

# Configure our elements.
#media_source.set_property('uri', 'file:///home/reimus/Public/sintel_trailer-480p.webm')
media_source.set_property('uri', 'http://docs.gstreamer.com/media/sintel_trailer-480p.webm')
wavescope_visual.set_property('shader', 0)
wavescope_visual.set_property('style', 3)
file_sink.set_property('location', 'myaudio.mp3')

# Add elements to our bin
output_bin.add(decode, convert, tee, audio_queue, audio_sink, wavescope_queue,
    wavescope_visual, wavescope_convert, wavescope_sink, file_queue, 
    file_encode, file_sink)

# Link decodebin with autoconvert when its source pad has been created.
decode.connect('new-decoded-pad', on_new_decoded_pad)

# Link the rest of our elements together.
if (not gst.element_link_many(convert, tee) or
    not gst.element_link_many(audio_queue, audio_sink) or
    not gst.element_link_many(wavescope_queue, wavescope_visual, 
        wavescope_convert, wavescope_sink) or
    not gst.element_link_many(file_queue, file_encode, file_sink)):
    print 'Not all elements could link.'

# Request pads to manually link the tee Element.
tee_audio_pad = tee.get_request_pad('src%d')
tee_wavescope_pad = tee.get_request_pad('src%d')
tee_file_pad = tee.get_request_pad('src%d')
print 'Obtained request pad %s for audio branch.'% tee_audio_pad.get_name()
print 'Obtained request pad %s for audio branch.'% tee_wavescope_pad.get_name()
print 'Obtained request pad %s for audio branch.'% tee_file_pad.get_name()

# Manually link the tee pads to the queue pads.
queue_audio_pad = audio_queue.get_static_pad('sink')
queue_wavescope_pad = wavescope_queue.get_static_pad('sink')
queue_file_pad = file_queue.get_static_pad('sink')
if (tee_audio_pad.link(queue_audio_pad) != gst.PAD_LINK_OK or
    tee_wavescope_pad.link(queue_wavescope_pad) != gst.PAD_LINK_OK or
    tee_file_pad.link(queue_file_pad) != gst.PAD_LINK_OK):
    print 'Tee could not be linked.'
    exit(-1)

# Create pads for the bin.
decode_pad = decode.get_static_pad('sink')
ghost_pad = gst.GhostPad('sink', decode_pad)
ghost_pad.set_active(True)
output_bin.add_pad(ghost_pad)

# Set media_source's audio sink.
media_source.set_property('audio-sink', output_bin)

# Set our pipeline state to Playing.
media_source.set_state(gst.STATE_PLAYING)

# Wait until error or EOS.
bus = media_source.get_bus()
msg = bus.timed_pop_filtered(gst.CLOCK_TIME_NONE,
    gst.MESSAGE_ERROR | gst.MESSAGE_EOS)
print msg

# Free resources.
media_source.set_state(gst.STATE_NULL)