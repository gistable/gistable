#!/usr/bin/env python

import gtk, threading, datetime, urllib2, json
import Image, ImageChops, ImageStat, StringIO

CONFIG_FILE = "config.json"

# config sample
#{
#  "sensivity": 10,
#  "cameraurl": "http://192.168.1.100/snapshot.cgi?user=admin&pwd=123456",
#  "commandurl": "http://192.168.1.100/decoder_control.cgi?user=admin&pwd=123456&degree=10&command=%d"
#}

class PySurCamUI(gtk.Window):
    def __init__(self):
        super(PySurCamUI, self).__init__()
        
        try:
            self.config = json.load(open(CONFIG_FILE))
        except:
            raise SystemExit("%s config file was not found or parsed correctly" % CONFIG_FILE)
            
        # variables
        self.dnd = False
        self.isrunning = True
        self.currentimage = None
        self.previousimage= None
        self.rms = 0
        
        # window decoration
        self.set_default_size(320, 240)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_position(gtk.WIN_POS_CENTER)
        
        # status icon
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_stock(gtk.STOCK_MEDIA_RECORD) 
        self.statusicon.connect("activate", self.togglevisibility)
        self.statusicon.connect("popup-menu", self.popupmenu)
        
        # image view canvas
        canvaseventbox = gtk.EventBox()
        self.canvas = gtk.Image()
        self.canvas.show()
        canvaseventbox.connect("button-press-event", self.cameraclick)
        canvaseventbox.add(self.canvas)
        self.add(canvaseventbox)
        
        self.show_all()
        
    def cameraclick (self, event, pointer):      
        # doubleclick handler for moving camera
        if not pointer.type == gtk.gdk._2BUTTON_PRESS: return
        
        direction = None
        
        if pointer.x < 70: direction = 4
        elif pointer.x > 250: direction = 6
        elif pointer.y < 40: direction = 0
        elif pointer.y > 200: direction = 2
        
        if not direction == None:
            urllib2.urlopen(self.config['commandurl'] % direction)           
        
    
    def imageprocess(self):
        
        while self.isrunning:
            try:
                self.currentframedata = urllib2.urlopen(self.config['cameraurl']).read()
            except:
                continue
            
            if not self.dnd:
                
                self.currentimage = Image.open(StringIO.StringIO(self.currentframedata))
                if self.previousimage == None: self.previousimage = self.currentimage.copy()
                framedifference = ImageStat.Stat(ImageChops.difference(self.currentimage, self.previousimage)).rms
                self.rms = sum(framedifference)/len(framedifference)
                self.previousimage = self.currentimage.copy()
                self.currentimage = None              
                
                if self.rms > self.config['sensivity']:
                    self.show()
                
            gtk.gdk.threads_enter()
            try:
                if self.get_visible():
                    self.set_title(str(datetime.datetime.now()))
                    framedataloader=gtk.gdk.PixbufLoader()
                    framedataloader.write(self.currentframedata)
                    framedataloader.close()
                    self.canvas.set_from_pixbuf(framedataloader.get_pixbuf())
            finally:
                gtk.gdk.threads_leave()
                    
    def popupmenu(self, icon, button, time):
        menu = gtk.Menu()
        
        shlabel = "Hide" if self.get_visible() else "Show"
        showhide = gtk.MenuItem(shlabel)
        
        dndmode = gtk.CheckMenuItem("DND Mode")
        dndmode.set_active(self.dnd)
        
        quit = gtk.MenuItem("Quit")
        
        showhide.connect("activate", self.togglevisibility)
        dndmode.connect("activate", self.dndtoggle)
        quit.connect("activate", self.main_quit)
        
        menu.append(showhide)
        menu.append(dndmode)
        menu.append(quit)
        
        menu.show_all()
        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)
    
    def dndtoggle(self, event):            
        self.dnd = True if not self.dnd else False
    
    def togglevisibility(self, event):
        if self.get_visible():
            self.hide()
        else:
            self.show()
    
    def minimizeonclose(self, window, event):
        self.hide_on_delete()
        return True

    def main_quit(self, event):
        self.isrunning = False
        self.imageprocessthread = False
        gtk.main_quit()
            
    def main(self):
        # background image process and update thread
        gtk.gdk.threads_init()
        self.imageprocessthread = threading.Thread(target=self.imageprocess)
        self.imageprocessthread.start()
        
        self.connect("destroy", self.main_quit)
        self.connect("delete-event", self.minimizeonclose)
        
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()

UI = PySurCamUI()
UI.main()