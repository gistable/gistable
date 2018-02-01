# place at ~/.kodi/userdata/autoexec.py
import xbmc

xbmc.executebuiltin('PlayMedia("/storage/videos/","isdir")')
xbmc.executebuiltin('xbmc.PlayerControl(repeatall)')
xbmc.executebuiltin("Action(Fullscreen)")