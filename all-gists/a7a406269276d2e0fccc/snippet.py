# Copyright (C) <year> <name>
# All rights reserved.
#
# \\file <filename>
# \\lastmodified <date>
# \\brief <description>

import c4d
import os

def load_icon(fn):
  """ Loads a c4d.bitmaps.BaseBitmap by name relative to the plugins
  containing directory and returns it. None is returned if the bitmap
  could not be loaded. """

  fn = os.path.join(os.path.dirname(__file__), fn)
  bmp = c4d.bitmaps.BaseBitmap()
  if bmp.InitWith(fn)[0] == c4d.IMAGERESULT_OK:
    return bmp
  return None

class PluginCommand(c4d.plugins.CommandData):
  """ Cinema 4D Command Plugin ... """

  PLUGIN_ID = <plugin_id>
  PLUGIN_NAME = "Plugin Name"
  PLUGIN_HELP = "May the force be with you."
  PLUGIN_INFO = 0
  PLUGIN_ICON = load_icon('res/image/plugin.tif')

  def Register(self):
    return c4d.plugins.RegisterCommandPlugin(self.PLUGIN_ID, self.PLUGIN_NAME,
      self.PLUGIN_INFO, self.PLUGIN_ICON, self.PLUGIN_HELP, self)

  def Execute(self, doc):
    return True

def main():
  PluginCommand().Register()

if __name__ == "__main__":
  main()
