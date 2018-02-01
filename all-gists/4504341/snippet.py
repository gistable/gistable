# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 08:20:14 2013

@author: Nick Coblentz
"""

from burp import IBurpExtender
from burp import IScannerInsertionPointProvider
from burp import IScannerInsertionPoint
from java.io import PrintWriter
import subprocess
import base64
from subprocess import CalledProcessError
import sys
from xml.sax import ContentHandler
import xml.sax
from xml.dom import minidom

class BurpExtender(IBurpExtender, IScannerInsertionPointProvider):
    
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        #Used to debug plugin
        self.stdout = PrintWriter(callbacks.getStdout(), True)
        self.stderr = PrintWriter(callbacks.getStderr(), True)
        # set our extension name
        callbacks.setExtensionName("WCF Binary Scan Insertion Point")
        callbacks.registerScannerInsertionPointProvider(self)
        return        
    
    def getInsertionPoints(self, baseRequestResponse):        
        request_bytes = baseRequestResponse.getRequest()
        body_bytes = WCFBinaryHelper.GetWCFBinaryRequestBodyBytes(self,request_bytes)
        if(body_bytes != None):
            return WCFBinaryInsertionPointFactory.GetWCFBinaryInsertionPoints(self,request_bytes,body_bytes)
        return None

class WCFBinaryHelper:

    @classmethod
    def GetHeadersContaining(cls, findValue, headers):
        if(findValue!=None and headers!=None and len(headers)>0):
            return [s for s in headers if findValue in s]
        return None
    
    @classmethod
    def GetWCFBinaryRequestBodyBytes(cls,extender, request_bytes):
        request_info = extender.helpers.analyzeRequest(request_bytes)
        headers = request_info.getHeaders()
        if(headers!=None and len(headers)>0):
            matched_headers = cls.GetHeadersContaining('Content-Type',headers)
            if(matched_headers!=None):
                for matched_header in matched_headers:
                    if('msbin1' in matched_header):
                        return request_bytes[request_info.getBodyOffset():]
        return None                
    
    @classmethod
    def DecodeWCF(cls,extender, base64EncodedBody):        
        try:
            proc = subprocess.Popen(['NBFS.exe','decode',base64EncodedBody],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            #proc.wait()
            output = proc.stdout.read()
            extender.stdout.println(output)
            extender.stdout.println(proc.stderr.read())
            return output

        except CalledProcessError, e:
            extender.stdout.println("error({0}): {1}".format(e.errno, e.strerror))
        except:
            extender.stdout.println("Unexpected error: %s: %s\n%s" % (sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))        
        return None
     
    @classmethod
    def EncodeWCF(cls,extender, xmlContent):       
        base64EncodedXML=base64.b64encode(xmlContent)
        try:
            proc = subprocess.Popen(['NBFS.exe','encode',base64EncodedXML],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            #proc.wait()
            output = proc.stdout.read()
            extender.stdout.println(output)
            extender.stdout.println(proc.stderr.read())
            return extender.helpers.stringToBytes(base64.b64decode(output))

        except CalledProcessError, e:
            extender.stdout.println("error({0}): {1}".format(e.errno, e.strerror))
        except:
            extender.stdout.println("Unexpected error: %s: %s\n%s" % (sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))
        return None

class WCFXMLContentHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self.current_element=None
        self.insertion_point_xml_tag_names=[]
        self.insertion_point_xml_tag_names_count={}

    def addTagInsertionPoint(self,tag,content):
        count = 0
        if(tag in self.insertion_point_xml_tag_names_count):
            count = self.insertion_point_xml_tag_names_count[tag]+1
        self.insertion_point_xml_tag_names_count[tag]=count
        self.insertion_point_xml_tag_names.append([self.current_element,count,content])
        
    def startElement(self,name,attributes):
        self.current_element=name
        
    def endElement(self,name):
        self.current_element=None
    
    def characters(self,content):
        if(content!=None):
            striped_content = content.strip()
            if(len(striped_content)>0):
                self.addTagInsertionPoint(self.current_element,content)
    
    def getInsertionPoints(self):
        return self.insertion_point_xml_tag_names
        
        
class WCFBinaryInsertionPointFactory:
    @classmethod
    def GetWCFBinaryInsertionPoints(cls,extender,request_bytes,body_bytes):        
        insertionPoints=[]
        decoded_wcf_body = base64.b64decode(WCFBinaryHelper.DecodeWCF(extender,base64.b64encode(extender.helpers.bytesToString(body_bytes))))
        wcfXMLContentHandler=WCFXMLContentHandler()
        xml.sax.parseString(decoded_wcf_body,wcfXMLContentHandler)
        tagNamesAndContent = wcfXMLContentHandler.getInsertionPoints()            
        for tagNameAndContent in tagNamesAndContent:
            insertionPoints.append(WCFBinaryInsertionPoint(extender,request_bytes,body_bytes,decoded_wcf_body,tagNameAndContent[0],tagNameAndContent[1],tagNameAndContent[2]))            
        return insertionPoints
    
            
            
class WCFBinaryInsertionPoint(IScannerInsertionPoint):
    def __init__(self, extender, request_bytes,body_bytes,decoded_wcf_body, tag_name, tag_count,content):
        self.request_bytes=request_bytes
        self.body_bytes=body_bytes
        self.tag_name=tag_name
        self.tag_count=tag_count
        self.content=content
        self.extender=extender
        self.myInsertionPointName=("WCF Binary Encoded Prameter: %s" % tag_name)
        self.myBaseValue=content
        self.decoded_wcf_body=decoded_wcf_body
        self.xml_body = minidom.parseString(decoded_wcf_body)
        request_info = self.extender.helpers.analyzeRequest(request_bytes)
        self.bodyOffset = request_info.getBodyOffset()
        self.extender.stdout.println("New Insertion Point Created: %s" % tag_name)
        
    def getInsertionPointName(self):
        return self.myInsertionPointName
        
    def getBaseValue(self):
        return self.myBaseValue

    def buildRequest(self, payload):
        elem = self.xml_body.getElementsByTagName(self.tag_name)
        if(elem!=None and len(elem)>=self.tag_count):
            txtelem = elem[self.tag_count].firstChild
            if(txtelem != None and txtelem.nodeType == xml.dom.Node.TEXT_NODE):
                txtelem.data=self.extender.helpers.bytesToString(payload)
                wcf_binary_body = WCFBinaryHelper.EncodeWCF(self.extender,self.xml_body.toxml())
                
                new_request_bytes = list(self.request_bytes)
                new_request_bytes[self.bodyOffset:]=wcf_binary_body
                return new_request_bytes
        return None

    def getPayloadOffsets(self, payload):
        # None because request body is encoded
        return None
    
    
    def getInsertionPointType(self):        
        return INS_EXTENSION_PROVIDED