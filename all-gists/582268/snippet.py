#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, os, random

"""
DedeInjector is a shortcut class for making dedeler as a background into the target friend's computers.
only supports for gnome/linux environments.

warning: do not try this on people who you don't know well. you don't know how they react after the injection.
it can be dangerous, seriously.
"""

class DedeInjector(object):
    """
    random dede choice
    @return string
    """
    DEDELER = "dede%s.jpg" % random.choice(xrange(1, 5))

    def __init__(self):
        """
        get user's login name
        @return void
        """
        self.user = os.getenv("USERNAME")
        self.printMessage("ilgili dede: %s" % DedeInjector.DEDELER)
    
    def injectDede(self):
        """
        download selected dede
        @return string
        """
        self.printMessage("dede download ediliyor")
        dede_image = urllib.urlopen("http://www.emreyilmaz.me/fun/dedeler/%s" % DedeInjector.DEDELER)
        dede_file_handle = open("/home/%s/dede.jpg" % self.user, "wb+")
        dede_file_handle.write(dede_image.read())
        dede_file_handle.close()
        
        self.__makeDedeDesktopBackground()
        
    def __makeDedeDesktopBackground(self):
        """
        gconftool-2 is sexier than dedeler.
        @return void
        """
        self.printMessage("dede masaüstü resmi olarak ayarlaniyor.")
        os.system("gconftool-2 -t str --set /desktop/gnome/background/picture_filename /home/%s/dede.jpg" % self.user)
        os.system('gconftool-2 -t str --set /desktop/gnome/background/picture_options "centered"')
        
    def printMessage(self, message):
        """
        formats sys.stdout messages.
        @return string
        """
        print("[+] %s" % message)

if __name__ == '__main__':
    injector = DedeInjector()
    injector.injectDede()