# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 14:20:28 2012

@author: Nick Coblentz
"""

from burp import IBurpExtender
from burp import IMessageEditorTabFactory
from burp import IMessageEditorTab
from java.io import PrintWriter
import re
import base64
import StringIO
import zipfile
from xml.dom.minidom import parseString

#Implements MessageEditorTabFactory
class BurpExtender(IBurpExtender, IMessageEditorTabFactory):
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks=callbacks
        #Used to debug plugin
        self.stdout = PrintWriter(callbacks.getStdout(), True)
        self.stderr = PrintWriter(callbacks.getStderr(), True)
        self.helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Base 64 Zip Helper")
        #Indicate that this class contains the method to instantiate a new Message Editor Tab
        callbacks.registerMessageEditorTabFactory(self)
        return
        
    #Instatiates a new Message Editor Tab of type Base64ZipInputTab
    def createNewInstance(self, controller, editable):                
        return Base64ZipInputTab(self, controller, editable)
        
#Implements MessageEditorTab        
class Base64ZipInputTab(IMessageEditorTab):
    def __init__(self, extender, controller, editable):
        self.extender = extender
        self.editable = editable
        self.controller = controller
                
        self.txtInput = extender.callbacks.createTextEditor()
        #self.txtInput.setEditable(editable)
        #View only plugin
        self.txtInput.setEditable(False)
        return
        
    def getTabCaption(self):
        return "Base 64 Encoded Zip File Data"
        
    def getUiComponent(self):
        return self.txtInput.getComponent()
    
    #The targeted SOAP responses data is inside the fourth XML tag, return that data
    def getInnerXMLContent(self,content):
        matches = re.search('(?:<.*>){4}([^<]+)(?:<.*>){4}',content)
        if(matches != None):
            return matches.group(1)
        return None
        
    #if its a response (not a request), the targeted domain is found and data is found 4 XML tags deep in a SOAP responses, show the tab
    def isEnabled(self, content, isRequest):
        if(not isRequest):
            if('exampledomain.com' in self.controller.getHttpService().getHost()):
                if(self.getInnerXMLContent(self.extender.helpers.bytesToString(content))!=None):
                    return True
        return False
    
    def isModified(self):        
        return self.txtInput.isTextModified()
    
    def getSelectedData(self):        
        return self.txtInput.getSelectedText()
        
    #base64 decode, unzip, and then prettify the XML data.  Show the result in the tab    
    def setMessage(self, content, isRequest):
        #sometimes old data was displayed, not sure why.  Solution was to clear it out each time.
        self.txtInput.setText("")
        output=[]

        s0 = self.getInnerXMLContent(self.extender.helpers.bytesToString(content))
        s1=base64.b64decode(s0)
        z1=zipfile.ZipFile(StringIO.StringIO(s1),"r")
        z1filelist=z1.filelist
        
        while(len(z1filelist)>0):
            #output.append("\n===============")
            filename=z1filelist.pop().filename
            #output.append(filename+":")
            output.append(z1.read(filename))        
        
        self.txtInput.setText(self.extender.helpers.stringToBytes(self.prettyXML("\n".join(output))))
        return
        
    def prettyXML(self,xmldata):
        try:
            return parseString(xmldata).toprettyxml(encoding="utf-8")
        except:
            return xmldata
        
        
    def getMessage(self):
        return self.txtInput.getText()
        