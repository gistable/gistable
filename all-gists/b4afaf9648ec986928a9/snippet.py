#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uno
from com.sun.star.beans import PropertyValue
from pythonscript import ScriptContext
import os
import sys
import time

class UnoConnector():
    """
    Libre Office Runtime Connector
    It is assumed libreoffice is run like this from a shell:
        libreoffice "--accept=socket,host=localhost,port=2002;urp;" ./test1.ods &
        or
        libreoffice "--accept=pipe,name=some_name;urp;StarOffice.Servicemanager" ./test1.ods &
    """

    def __init__(self, docName = "_blank", pipeName = None, host = None, port = None, loIsRunning = False, headless = ""):
        if pipeName == None and port == None:
            raise Exception("Must specify either port or pipe")
        if pipeName != None and port != None:
            raise Exception("Must specify either port or pipe, not both")
        self.headless = headless
        self.docName = docName
        self.port = port
        self.pipeName = pipeName
        if self.port != None:
            if host == None:
                self.host = "localhost"
            else:
                self.host = host
            self.loLaunch = """ libreoffice --accept="socket,host=%s,port=%s;urp;" --norestore --nologo --nodefault %s %s &""" % (self.host, self.port, self.headless, [self.docName, ""][self.docName == '_blank'])
            self.resolveStr = "uno:socket,host=%s,port=%s;urp;StarOffice.ComponentContext" % (self.host, self.port)
        else:
            self.host = None
            self.loLaunch = """ libreoffice --accept="pipe,name=%s;urp;StarOffice.Servicemanager" --norestore --nologo --nodefault %s %s &""" % (self.pipeName, self.headless, [self.docName, ""][self.docName == '_blank'])
            self.resolveStr = "uno:pipe,name=%s;urp;StarOffice.ComponentContext" % (self.pipeName)
        if not loIsRunning:
            if self.launch_lo() == 0:
                self.connect_to_office()
            else:
                print("Error launching LibreOffice")
        else:
            self.connect_to_office()

    def launch_lo(self):
        result = os.system(self.loLaunch)
        time.sleep(1)
        return result

    def connect_to_office(self):
        self.localContext = uno.getComponentContext()
        self.resolver = self.localContext.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', self.localContext)
        #self.client = self.resolver.resolve("uno:pipe,name=some_name;urp;StarOffice.ComponentContext")
        self.client = None
        for n in range(1, 61):
            try:
                print("Connectiong client, attemp No %d" % (n,))
                self.client = self.resolver.resolve(self.resolveStr)
                break
            except:
                time.sleep(1)
        if self.client:    
            self.scriptContext = ScriptContext(self.client, None, None)
            self.desktop = self.scriptContext.getDesktop()
            if self.docName == '_blank':
                self.newDoc()
            return self.doc
        else:
            self.scriptContext = None
            self.desktop = None
            self.doc = None
            return None
    
    def newDoc(self, doctype = "calc"):
        self.desktop.loadComponentFromURL("private:factory/s%s" % (doctype,), "_blank", 0, ())
        self.doc = None
        for n in range(1, 61):
            print("Trying to load default document, attemp No %d" % (n,))
            self.doc = self.scriptContext.getDocument()
            if self.doc != None:
                break
            else:
                time.sleep(1)
    
    def saveAs(self, newName, excelFormat = False):
        if not self.doc:
            return None
        else:
            self.docName = newName
            pv = ()
            if excelFormat:
                pv = (PropertyValue("FilterName", 0, "MS Excel 97", 0),)
            self.doc.storeAsURL("file://%s%s%s" % (os.getcwd(), os.path.sep, self.docName), pv)
            return self.doc
    
    def save(self):
        if not self.doc:
            return None
        else:
            if self.docName == "_blank":
                print("File must have a name in order to be saved. Use 'saveAs'first")
                return None
            else:
                self.doc.store()
                return self.doc

    def exportPDF(self, newName):
        if not self.doc:
            return None
        else:
            pv = (PropertyValue("FilterName", 0, "writer_pdf_Export", 0),)
            self.doc.storeToURL("file://%s%s%s.pdf" % (os.getcwd(), os.path.sep, newName.replace('.pdf', '')), pv)
        return self.doc
    


                                              

