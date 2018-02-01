#!/usr/bin/env python
import pygst
pygst.require("0.10")
import gst, pygtk, gtk
import sys
class Main(object):
  def __init__(self):
    self.multimedia_file=""
    # Create the GUI
    self.win = gtk.Window()
    self.win.set_title("Play Video Example")
    self.win.connect("delete_event",
    lambda w,e: gtk.main_quit())
    vbox = gtk.VBox(False, 0)
    hbox = gtk.HBox(False, 0)
    self.load_file = gtk.FileChooserButton("Choose Audio File")
    self.play_button = gtk.Button("Play", gtk.STOCK_MEDIA_PLAY)
    self.pause_button = gtk.Button("Pause", gtk.STOCK_MEDIA_PAUSE)
    self.stop_button = gtk.Button("Stop", gtk.STOCK_MEDIA_STOP)
    self.videowidget = gtk.DrawingArea()
    # You want to expand the video widget or
    # else you cannot see it
    self.videowidget.set_size_request(400, 250)
    self.load_file.connect("selection-changed",
    self.on_file_selected)
    self.play_button.connect("clicked", self.on_play_clicked)
    self.pause_button.connect("clicked", self.on_pause_clicked)
    self.stop_button.connect("clicked", self.on_stop_clicked)
    hbox.pack_start(self.play_button, False, True, 0)
    hbox.pack_start(self.pause_button, False, True, 0)
    hbox.pack_start(self.stop_button, False, True, 0)
    vbox.pack_start(self.load_file, False, True, 0)
    vbox.pack_start(self.videowidget, True, True, 0)
    vbox.pack_start(hbox, False, True, 0)
    self.win.add(vbox)
    self.win.show_all()
    # Setup GStreamer
    self.player = gst.element_factory_make(
    "playbin", "MultimediaPlayer")
    bus = self.player.get_bus()
    bus.add_signal_watch()
    bus.enable_sync_message_emission()
    #used to get messages that GStreamer emits
    bus.connect("message", self.on_message)
    #used for connecting video to your application
    bus.connect("sync-message::element",
    self.on_sync_message)
  def on_file_selected(self, widget):
    self.multimedia_file = self.load_file.get_filename()
  def on_play_clicked(self, widget):
    self.player.set_property('uri',
    "file://" + self.multimedia_file)
    self.player.set_state(gst.STATE_PLAYING)
  def on_pause_clicked(self, widget):
    self.player.set_state(gst.STATE_PAUSED)
  def on_stop_clicked(self, widget):
    self.player.set_state(gst.STATE_NULL)
  def on_message(self, bus, message):
    if message.type == gst.MESSAGE_EOS:
    # End of Stream
      self.player.set_state(gst.STATE_NULL)
    elif message.type == gst.MESSAGE_ERROR:
      self.player.set_state(gst.STATE_NULL)
    
      (err, debug) = message.parse_error()
      print "Error: %s" % err, debug
      
  def on_sync_message(self, bus, message):
    if message.structure is None:
      return False
    if message.structure.get_name() == "prepare-xwindow-id":
      if sys.platform == "win32":
	win_id = self.videowidget.window.handle
      else:
	win_id = self.videowidget.window.xid
      assert win_id
      imagesink = message.src
      imagesink.set_property("force-aspect-ratio", True)
      imagesink.set_xwindow_id(win_id)

if __name__ == "__main__":
  Main()
  gtk.main()
