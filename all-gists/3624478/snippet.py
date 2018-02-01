import os
import wave
import threading
import sys

# PyAudio Library
import pyaudio

class WavePlayerLoop(threading.Thread) :
  """
  A simple class based on PyAudio to play wave loop.

  It's a threading class. You can play audio while your application
  continues to do its stuff. :)
  """

  CHUNK = 1024

  def __init__(self,filepath,loop=True) :
    """
    Initialize `WavePlayerLoop` class.

    PARAM:
        -- filepath (String) : File Path to wave file.
        -- loop (boolean)    : True if you want loop playback. 
                               False otherwise.
    """
    super(WavePlayerLoop, self).__init__()
    self.filepath = os.path.abspath(filepath)
    self.loop = loop

  def run(self):
    # Open Wave File and start play!
    wf = wave.open(self.filepath, 'rb')
    player = pyaudio.PyAudio()

    # Open Output Stream (basen on PyAudio tutorial)
    stream = player.open(format = player.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True)

    # PLAYBACK LOOP
    data = wf.readframes(self.CHUNK)
    while self.loop :
      stream.write(data)
      data = wf.readframes(self.CHUNK)
      if data == '' : # If file is over then rewind.
        wf.rewind()
        data = wf.readframes(self.CHUNK)

    stream.close()
    player.terminate()


  def play(self) :
    """
    Just another name for self.start()
    """
    self.start()

  def stop(self) :
    """
    Stop playback. 
    """
    self.loop = False
