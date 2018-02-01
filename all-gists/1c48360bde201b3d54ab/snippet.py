# Copyright (C) 2015 Niklas Rosenstein
# All rights reserved.
#
# File: show_shaders.py
# Last Modified: 16.11.2015
# Description: This script opens a dialog that displays all
#   shaders in a material, tag or object that can be specified
#   with a link box.

import c4d
import os

def get_shaders(node):
    if node.CheckType(c4d.Xbase):
        return node.GetChildren()
    res = []
    sha = node.GetFirstShader()
    while sha:
        res.append(sha)
        sha = sha.GetNext()
    return res

def script_open_async_dialog(dlg, *args, **kwargs):
    # xxx: this is a very dirty hack
    dialogs = vars(os).setdefault('__c4d_dialogs', [])
    dialogs = [d for d in dialogs if d.IsOpen()]
    dialogs.append(dlg)
    os.__c4d_dialogs = dialogs
    return dlg.Open(c4d.DLG_TYPE_ASYNC, *args, **kwargs)

class ShaderDialog(c4d.gui.GeDialog):
    
    def GetLink(self, param_id):
        gui = self.FindCustomGui(param_id, c4d.CUSTOMGUI_LINKBOX)
        if gui:
            return gui.GetLink()
        return None

    def AddLinkBox(self, param_id, flags, link=None):
        gui = self.AddCustomGui(param_id, c4d.CUSTOMGUI_LINKBOX,
            "", flags, 0, 0)
        gui.SetLink(link)
        return gui

    def AddShaderWidgets(self, sha, parent, depth):
        msg1 = ''
        msg2 = ''
        if sha.CheckType(c4d.Xbitmap):
            msg2 = sha[c4d.BITMAPSHADER_FILENAME] or ''
        if parent:
            for bc, did, __ in parent.GetDescription(0):
                try:
                    if parent[did] != sha:
                        continue
                except AttributeError:
                    # Parameter inacessible from Python
                    continue

                msg1 = bc[c4d.DESC_IDENT] or '<no ident>'
                break
            else:
                msg1 = '<no parameter>'

        self.GroupBegin(0, c4d.BFH_SCALEFIT)
        self.AddStaticText(0, c4d.BFH_LEFT, name='---' * depth)
        self.AddLinkBox(0, c4d.BFH_SCALEFIT, link=sha)
        self.GroupEnd()
        self.AddStaticText(0, 0, name=sha.GetTypeName())
        self.AddStaticText(0, 0, name=msg1)
        self.AddStaticText(0, 0, name=msg2)

    def Update(self, node=None, depth=0):
        is_root = (not node)
        if is_root:
            self.LayoutFlushGroup(1001)
            node = self.GetLink(1000)
            if not node:
                self.AddStaticText(0, c4d.BFH_CENTER, name="Nothing selected")
                self.AddStaticText(0, c4d.BFH_SCALEFIT, name="")
                self.LayoutChanged(1001)
                return

        shaders = get_shaders(node)
        if not shaders:
            if is_root:
                self.AddStaticText(0, c4d.BFH_CENTER, name="No shaders in the list")
                self.AddStaticText(0, c4d.BFH_SCALEFIT, name="")
                self.LayoutChanged(1001)
            return

        if is_root:
            self.AddStaticText(0, 0, name="Shader")
            self.AddStaticText(0, 0, name="Type")
            self.AddStaticText(0, 0, name="Parameter")
            self.AddStaticText(0, 0, name="Info")
            self.AddSeparatorH(0)
            self.AddSeparatorH(0)
            self.AddSeparatorH(0)
            self.AddSeparatorH(0)

        for sha in shaders:
            self.AddShaderWidgets(sha, node, depth)
            self.Update(sha, depth + 1)

        if is_root:
            self.LayoutChanged(1001)

    def CreateLayout(self):
        self.SetTitle("Shader Show")
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 0)
        self.GroupBorderSpace(6, 6, 6, 6)
        self.AddLinkBox(1000, c4d.BFH_SCALEFIT)
        self.AddSeparatorH(c4d.BFH_SCALEFIT)
        self.GroupBegin(1001, c4d.BFH_SCALEFIT, 4, 0)
        self.GroupEnd()
        self.GroupEnd()
        self.Update()
        return True

    def Command(self, wid, msg):
        if wid == 1000:
            self.Update()
        return True

    def CoreMessage(self, wid, msg):
        if wid == c4d.EVMSG_CHANGE:
            self.Update()
        return True

script_open_async_dialog(ShaderDialog(), 0, -1, -1, 400, 300)
