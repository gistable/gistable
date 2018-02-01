# See also http://wiki.xbmc.org/index.php?title=Autoexec.py
# Put this into the userdata folder, see http://wiki.xbmc.org/index.php?title=Userdata for details where this is for each platform
import xbmc
xbmc.executebuiltin('xbmc.PlayMedia("/storage/videos/","isdir")')
xbmc.executebuiltin('xbmc.PlayerControl(repeatall)')
xbmc.executebuiltin("Action(Fullscreen)")