#!/usr/bin/python

from gi.repository import AppIndicator3 as AppIndicator
from gi.repository import Gtk
import re
import signal
import sys
import threading


class Indicator(object):

  ICON_IDLE = "ubuntuone-client-idle"
  ICON_SYNCING = "ubuntuone-client-updating"
  ICON_ERROR = "ubuntuone-client-offline"
  ICONS = {"idle": ICON_IDLE, "syncing": ICON_SYNCING, "error": ICON_ERROR}

  def __init__(self):
    self.indicator = None

  # Main entry-point.
  def main(self):
    self.initialize()
    self.run()

  def initialize(self):
    # This is so Gtk.main receives keyboard interrupts.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    self.indicator = AppIndicator.Indicator.new("sync-indicator-client", "sync-indicator-messages",
        AppIndicator.IndicatorCategory.APPLICATION_STATUS)
    self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
    self.indicator.set_icon(self.ICON_IDLE)
    self.indicator.set_menu(Gtk.Menu())

  def run(self):
    # Gtk gets the main thread, stdin monitoring actually controls the life of
    # the process but runs in a separate thread.
    threading.Thread(target=self.run_stdin_monitor).start()
    Gtk.main()

  def run_stdin_monitor(self):
    # Run by the stdin monitoring thread.
    keep_going = True
    try:
      while keep_going:
        keep_going = self.process_line()
    finally:
      Gtk.main_quit()

  ACTION_RE = re.compile(r"^\[SYNC: ([a-z]+)\]$")
  def process_line(self):
    line = sys.stdin.readline()
    if not line:
      # This is the Ctrl-D case.
      return False
    matcher = self.ACTION_RE.match(line)
    if matcher is None:
      sys.stdout.write(line)
    else:
      state = matcher.group(1)
      icon = self.ICONS.get(state, self.ICON_IDLE)
      self.indicator.set_icon(icon)
    return True


if __name__ == "__main__":
  Indicator().main()
