# Version: 0.0.022

# Please note: This has only been tested on Sublime Text 3 Build 3065

# Installation:
# 1. Click "Download Gist"
# 2. Put alloy.py in: ~/Library/Application Support/Sublime Text 3/Packages/User/
# 3. Set your layout to Grid 4 - Go to view > layout > Grid: 4
# 4. Add to the bliss of working with Alloy...

# Based on this Gist from Fokke - https://gist.github.com/FokkeZB/6218345
# Alloy lay-out for Sublime Text http://withtitanium.com/2013/08/titanium-alloy-optimized-sublime-text-2-layout/

import sublime, sublime_plugin, time
from os.path import splitext
from os.path import isfile

currentFile = ''
debug = False

class MoveWindowCommand(sublime_plugin.EventListener):
    def on_load(self, view):
        global currentFile, debug

        if view.file_name() == None:
            return False

        window = sublime.active_window()

        if window.num_groups() != 4:
            return None

        if view.file_name() == currentFile:
            return False

        currentFile = view.file_name()

        if (debug):
            print('on_load(): ' + view.file_name())

        group, index = window.get_view_index(view)
        fileName, fileExtension = splitext(view.file_name())
        
        if fileExtension == '.xml':
            window.set_view_index(view, 2, 0)
        elif fileExtension == '.tss':
            window.set_view_index(view, 1, 0)
        elif fileExtension == '.js':
            isLib = True
            window.set_view_index(view, 0, 0)
            window.open_file(view.file_name())
            if isfile(fileName.replace('/controllers/','/views/')+'.xml'):  
                isLib = False 
                window.open_file(fileName.replace('/controllers/','/views/')+'.xml')
            if isfile(fileName.replace('/controllers/','/styles/')+'.tss'):
                isLib = False 
                window.open_file(fileName.replace('/controllers/','/styles/')+'.tss')
            if isLib:
                window.set_view_index(view, 3, 0)                
            else:
                window.set_view_index(view, 0, 0)
        else :
            window.set_view_index(view, 3, 0)      

        window.focus_view(view)   
        window.focus_group(0)  
    
    def on_close(self, view): 
        global currentFile, debug

        if view.file_name() == None:
            return None

        if (debug):
            print('on_close(): ' + view.file_name())            

        window = sublime.active_window()

        if window.num_groups() != 4:
            return None

        fileName, fileExtension = splitext(view.file_name())
            
        if fileExtension != '.js': 
            return None

        if view.file_name().find("controllers") == -1:
            return None    

        if not isfile(fileName.replace('/controllers/','/views/') + '.xml') or not isfile(fileName.replace('/controllers/','/styles/') + '.tss'):
            return None
        
        xmlFileView = window.find_open_file(fileName.replace('/controllers/','/views/')+'.xml')
        window.focus_view(xmlFileView)
        window.run_command('close_file')

        tssFileView = window.find_open_file(fileName.replace('/controllers/','/styles/')+'.tss')
        window.focus_view(tssFileView)
        window.run_command('close_file')

    def on_activated(self, view):
        global currentFile, debug

        if view.file_name() == None:
            return None        

        if (debug):
            print('on_activated(): ' + view.file_name())

        window = sublime.active_window()

        if window.num_groups() != 4:
            return None            

        group, index = window.get_view_index(view)
        fileName, fileExtension = splitext(view.file_name())  

        if fileExtension != '.js': 
            return None

        if view.file_name() == currentFile:
            return None

        currentFile = view.file_name()     

        if (debug):
            print('on_activated() - pass: ' + view.file_name())       

        if view.file_name().find("controllers") != -1 and fileExtension == '.js':   

            if isfile(fileName.replace('/controllers/','/styles/')+'.tss'):            
                tssFileView = window.find_open_file(fileName.replace('/controllers/','/styles/')+'.tss')
                if tssFileView == None:
                    return False

                sublime.set_timeout(lambda: window.set_view_index(tssFileView, 1, index), 0)
                sublime.set_timeout(lambda: window.focus_view(tssFileView), 0)

            if isfile(fileName.replace('/controllers/','/views/')+'.xml'):  
                xmlFileView = window.find_open_file(fileName.replace('/controllers/','/views/')+'.xml')
                if xmlFileView == None:
                    return False


                sublime.set_timeout(lambda: window.set_view_index(xmlFileView, 2, index), 1)
                sublime.set_timeout(lambda: window.focus_view(xmlFileView), 1)

            
            sublime.set_timeout(lambda: window.focus_group(0), 2)