'''
This python script listens for distributed notifications from iTunes of new songs playing, 
works alot better then constantly polling. 
'''
import Foundation
from AppKit import *
from PyObjCTools import AppHelper

class GetSongs(NSObject):
    def getMySongs_(self, song):
        song_details = {}
        ui = song.userInfo()
        song_details = dict(zip(ui.keys(), ui.values()))
        print song_details

nc = Foundation.NSDistributedNotificationCenter.defaultCenter()
GetSongs = GetSongs.new()
nc.addObserver_selector_name_object_(GetSongs, 'getMySongs:', 'com.apple.iTunes.playerInfo',None)

NSLog("Listening for new tunes....")
AppHelper.runConsoleEventLoop()