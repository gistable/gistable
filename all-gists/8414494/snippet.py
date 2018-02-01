'''
ModuleManager.py

Defines ModuleManager class for enabling/disable Maya modules, and ModuleManagerDialog - a GUI for same.

Copyright  (c) 2014 Steve Theodore. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import itertools
import maya.cmds as cmds
import os
import maya.mel
from collections import namedtuple

# Mod manager classes
#==============================================================================================

modTuple = namedtuple('modTuple', ('enabled','name','version','path', 'file'))
''' describes a mod on disk ''' 
 
class ModuleManager (object):
    '''
    Manages the list of .mod files on the local maya's MAYA_MODULE_PATH
    '''
    def __init__(self):
        self.Modules = {}
        self.Module_Files = []
        self.refresh()
    
    def refresh(self):
        '''
        Update the internal module list to reflect the state of files on disk
        '''
        self.Module_Files = []
        self.Modules = {}
        module_paths = maya.mel.eval('getenv MAYA_MODULE_PATH').split(";")
        for p in module_paths:
            try:
                self.Module_Files += [os.path.join(p, x).replace('\\', '/') for x in os.listdir(p) if x.lower()[-3:] == "mod"]
            except OSError: 
                pass # ignore bad paths
        for eachfile in self.Module_Files:
            for eachmod in self.parse_mod(eachfile):
                self.Modules["%s (%s)" % (eachmod.name, eachmod.version)] = eachmod 
                
    def parse_mod(self, modfile):
        '''
        Yields a modtuple describing the supplied .mod file
        '''
        with open (modfile, 'rt') as filehandle:
            for line in filehandle:
                if line.startswith("+") or line.startswith("-"):
                    enable, name, version, path = self.parse_mod_entry(line)
                    yield modTuple(enable == "+", name, version, path, modfile)
                    
    def parse_mod_entry(self, line):
        '''
        parses a line from a mod file describing a given mod
        '''
        
        enable, ignore, line = line.partition(" ")
        name, ignore, line = line.partition(" ")
        if 'PLATFORM:' in name.upper():
            name, ignore, line  = line.partition(" ")
        version, ignore, path = line.strip().partition(" ")
        return enable, name, version, path
    
    
    def enable(self, modtuple):
        self._rewrite_mod(modtuple, '+')
 
    def disable(self, modtuple):
        self._rewrite_mod(modtuple, '-')
        
    def _rewrite_mod(self, modtuple, character):
        all_lines = []            
        with open(modtuple.file, 'rt') as filehandle:
            for line in filehandle:
                enable, name, version, path = self.parse_mod_entry(line)
                if name == modtuple.name and version == modtuple.version:
                    line = character + line[1:]
                all_lines.append(line)                
        with open(modtuple.file, 'wt') as filehandle:
            filehandle.write('\n'.join(all_lines))
            

# UI helpers
#==========================

# formlayout shorcuts
T = 'top'
L = 'left'
R = 'right'
B = 'bottom'


def formfill( form, ctrl, margin, sides ):
    ct = itertools.repeat(str(ctrl))
    mr = itertools.repeat(margin)
    af= [i for i in itertools.izip(ct, sides, mr)]
    print af
    cmds.formLayout( form, e=True, af= af)


def snap( form, ctrl1, ctrl2, edge, margin ):
    cmds.formLayout( form, e=True, ac=( ctrl1, edge, margin, ctrl2 ) )

def formchain(form, side, margin, *ctrls):
    first, second = itertools.tee(*ctrls)
    second.next()
    ac = []
    for f, s in itertools.izip(first, second):
        ac.append ( (f, side, margin, s) )
    cmds.formLayout( form, e=True, ac= ac)

#====================================

class uiCtx(object):
    '''
    quickie layouthelper: automatically setParents after a layout is finished
    '''
    def __init__(self, uiClass, *args, **kwargs):
        self.Control = uiClass(*args, **kwargs)
    
    def __enter__(self):
        return self
        
    def __exit__(self, tb, val, traceback):
        cmds.setParent("..")
        
    def __repr__(self):
        return self.Control

#======================================

class ModuleWidget(object):
    '''
    Item template for an individual module
    '''
    COLUMNS = (40, 340, 40, 40)
    
    def __init__(self, key, modtuple):
        self.Module  = modtuple
        self.ModuleKey = key
        self.Widget = self._layout()
        self.State = self.Module.enabled
        self._OrigState = self.Module.enabled
        self._Toggle = None;
            
    @property
    def Modified(self):
        return self._OrigState != self.State
            
    def _layout(self):
        with uiCtx(cmds.rowLayout, nc=4, cw4 = self.COLUMNS, co4 = (8,0,0,0), ct4 = ('both', 'left', 'both', 'both'), rat = [1,'top', 6]) as widget:
            self.Toggle = cmds.checkBox('', v = self.Module.enabled, cc = self._state_changed)
            with uiCtx(cmds.columnLayout, w=self.COLUMNS[1], cal='left') as details:
                cmds.text(l = self.ModuleKey, fn = "boldLabelFont")
                cmds.text(l = self.Module.path, fn = "smallObliqueLabelFont")
            cmds.button("edit",  c=self._edit)
            cmds.button("show", c=self._show)
        return widget
                        
    def _state_changed(self, *ignore):
        self.State = cmds.checkBox(self.Toggle, q=True, v=True)
        
    def _edit(self, *ignore):
        os.startfile(self.Module.file)
        
    def _show(self, *_):
        dirname = os.path.dirname(self.Module.file)
        os.startfile(dirname)
        
    
    
class ModuleManagerDialog(object):
    '''
    Module manager dialog, implemented via LayoutDialog
    '''
    def __init__(self):
        self.ModMgr = ModuleManager()
        self.Widgets = {}
        
    def _layout(self):
        topform = cmds.setParent(q=True)
        
        cmds.formLayout(topform, e=True, w=500, h=2)
        with uiCtx(cmds.formLayout) as root:
            with uiCtx(cmds.formLayout,  w=480) as body:
                with uiCtx(cmds.scrollLayout) as scroll:
                    with uiCtx(cmds.formLayout, w=470) as list:
                        widgets = []
                        for key, val in self.ModMgr.Modules.items():
                            widgets.append(ModuleWidget(key, val))
                            self.Widgets[key] = widgets[-1]
                            formfill(list, widgets[-1].Widget, 4, [L,R])
                        widget_objects = [w.Widget for w in widgets]
                        formchain(list, 'top', 8, widget_objects)
            with uiCtx(cmds.rowLayout, nc=2, cw2 = (255,255), ct2 = ['both'] *2  ) as buttons :
                cmds.button('Cancel', c = self._cancel)
                cmds.button('Save', c= self._save)
            
        formfill(topform, root, 0, [T,B,L,R])
        formfill(root, body, 4, [T,L,R])
        formfill(root, buttons, 4, [B,L,R])
        formfill(body, scroll, 0, [T,B,L,R])
        snap(root, body, buttons, B, 4)
        self.Window = topform
            
    def _cancel(self, *args):
        cmds.layoutDialog(dismiss = "dismiss")
 
    def _save(self, *arg):
        for k, v in self.Widgets.items():
            if v.Modified:
                if v.State: self.ModMgr.enable(v.Module)
                if not v.State: self.ModMgr.disable(v.Module)            
        cmds.layoutDialog(dismiss = "OK")
 
    def show(self):
        self.ModMgr.refresh()
        cmds.layoutDialog(ui = self._layout, t='Module editor')


m = ModuleManagerDialog()        
m.show()