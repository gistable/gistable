#!/usr/bin/env python

# This script was written by Lars Wallin to facilitate export from svg to any output basically.
# For now only bitmap rendering is supported (to some degree...)
# Future versions should include rendering of canvas documents (css, html, ddh, ...)

# Please note that i have not run this script since i added this verbose commenting, so i might have broken some tab position or something...


import inkex

import sys, os, commands,subprocess
import string
from xml.dom.minidom import Document
from xml.dom.minidom import DocumentType

# This line is only needed if you don't put the script directly into
# the installation directory

#sys.path.append('/usr/share/inkscape/extensions')

# The simplestyle module provides functions for style parsing.
from simplestyle import *

# Generic class to handle object meta data.
class imageMetaData():
    id = ""
    background = ""
    width = ""
    height = ""
    path = ""
    area = ""
    x = 0
    y = 0
        
# Effect main class
class ExportToAny(inkex.Effect):

    parserProcessHandle = None
    saveLocation = ""
    where = ""
    what = ""
    svg_file = ""
    renderHistory = []

    def __init__(self):
        """
        Constructor.
        Defines the "--what" option of a script.
        """

        # Call the base class constructor.
        inkex.Effect.__init__(self)

        # The OptionParser stuff below are Inkscape specific code which sets up the dialog for the extension GUI.
        # The current options are just lab stuff and should be substituted with something more usefull. 
        
        # Define string option "--what" with "-w" shortcut.
        self.OptionParser.add_option('-w', '--what', action = 'store',
              type = 'string', dest = 'what', default = 'World',
              help = '')
          
        self.OptionParser.add_option('--where', action = 'store',
              type = 'string', dest = 'where', default = 'c:\\',
              help = 'Where to save?')
    
    
    # exportImage takes as argument the current svg element id. This is then used to select which element the Inkscape exe should export.
    def exportImage(self,id,parent_id):
            
            # The easiest way to name rendered elements is by using their id since we can trust that this is always unique.
            # The id will later be used as reference by the canvas document (html, ddh, css, ...)
            filename = os.path.join(self.where, id+'.png')
            
            # Inkscape has many really usefull cmd line arguments which can be used to query for data, and render bitmaps.
            # Please not that Inkscape supports shell execution and should really be started as such at the beginning of parsing. 
            # The shell spawning stuff is commented out at the bottom of this script.
            # The current command will start/close a new instance of the app for every element parsed.
            command = "inkscape --without-gui --export-area-snap --export-id %s --export-png %s %s " % (id, filename, self.svg_file) #create the command that will be use to export
            processHandle = subprocess.Popen(command,
                       shell=True,
                       stdout=subprocess.PIPE)
            
            # Inkscape is gracious enough to return some metadata regarding the exported bitmap.
            stdout_value = processHandle.communicate()[0]
            
            # Inkscapes element metadata is not a pleasant format. parseImageMetaData data tries to remedy this.            
            imageMetaData = self.parseImageMetaData(
                                str(stdout_value)
                            )

            return ((id + ";" + parent_id) + (";" + imageMetaData))


    # exportImage takes as argument the current svg element id. This is then used to select which element the Inkscape exe should export.
    def getImage(self,id,parent_id):
            
            # Inkscape has many really useful cmd line arguments which can be used to query for data, and render bitmaps.
            # Please not that Inkscape supports shell execution and should really be started as such at the beginning of parsing. 
            # The shell spawning stuff is commented out at the bottom of this script.
            # The current command will start/close a new instance of the app for every element parsed.
            command = "inkscape --without-gui --export-area-snap --export-id %s --export-png %s %s " % (id, filename, self.svg_file) #create the command that will be use to export
            processHandle = subprocess.Popen(command,
                       shell=True,
                       stdout=subprocess.PIPE)
            
            # Inkscape is gracious enough to return some metadata regarding the exported bitmap.
            stdout_value = processHandle.communicate()[0]
            
            # Inkscapes element metadata is not a pleasant format. parseImageMetaData data tries to remedy this.            
            imageMetaData = self.parseImageMetaData(
                                str(stdout_value)
                            )

            return ((id + ";" + parent_id) + (";" + imageMetaData))

    def parseImageMetaData(self,metaDataString):
        
        # Inkscape exports information about svg objects in a pretty ugly format. Lets do a quick and dirty solution to this problem :)             
        # NOTE: The input format of the metaDataString may very well change in future Inkscape releases.
        
        if(metaDataString != ''):

            metaDataString = metaDataString.replace('Background RRGGBBAA: ','')
            metaDataString = metaDataString.replace('Area ',';')
            metaDataString = metaDataString.replace(' exported to ',';')
            metaDataString = metaDataString.replace('Bitmap saved as: ','')
            metaDataString = metaDataString.replace(' x ',';')
            metaDataString = metaDataString.replace(' pixels (90 dpi)',';')
            metaDataString += ''
        
        
        
        return metaDataString
    
    # parseDoc is the first level of parsing.
    def parseDoc(self):
        # As you can see in the xpath query below we select all groups at the first level of the document.
        layers = self.document.xpath('//svg:svg/svg:g',namespaces=inkex.NSS)
        
        # For each group (which at this level is actually an Inkscape layer) call parseLayer.
        for node in layers:
            layerStr = self.exportImage(node.get('id'),'svg')
            self.debugLogger(layerStr)
            self.parseLayer(node)


    def parseLayer(self,rootElement):
        # I have chosen to call the level above layer "panel". 
        panels = rootElement.xpath('svg:g',namespaces=inkex.NSS)
        
        # Hey ho here we go
        for node in panels:
            self.parsePanel(node)


    def parsePanel(self,rootElement):
        # A panel is an area of the layer which we want to define. This area will not be rendered as a bitmap but saved as model data to be used when
        # rendering the canvas document (html, ddh, ...)
        elements = rootElement.xpath('svg:g',namespaces=inkex.NSS)
        #self.debugLogger(len(elements))
        
        # Loop through all *grouped elements*, which will be rendered as png bitmaps. Ungrouped elements will be ignored.
        for node in elements:
            self.parseElement(node)

    def parseElement(self,node):

        element_metadata = ""
        id = node.get('id')
        
        # Do actual export

        element_metadata = self.exportImage(id,'svg')
        element_metadata = element_metadata.split(';')
        element_metadata[3] = element_metadata[3].split(':')

        

        # Assign the element_metadata values to an elementData struct which we later can query for element data. This will be used for rendering of content documents.
        elementData = {
            'id':element_metadata[0],
            'parent_id':element_metadata[1],
            'background': element_metadata[2],
            'area':{
                'x':element_metadata[3][0],
                'y':element_metadata[3][1],
                'rel_x':element_metadata[3][2],
                'rel_y':element_metadata[3][3]
            },
            'width':element_metadata[4],
            'height':element_metadata[5],
            'path':element_metadata[6]
            }
        


        # Here we simply add the new struct to the renderHistory array.
        self.renderHistory.append(elementData)
        
        # And just for debug sake write some stuff back to the document.
        #self.debugLogger(self.renderHistory[0]['id'])

    # Sub-optimal function just as "proof-of-concept"
    def renderDDHDoc(self):
        bitmapSchemaString = ''
        bitmapDBString = ''
        ddhDocString = ''
        
        iterator = 0
        
        # Ok lets render the bitmap schema section of the ddh
        bitmapSchemaString = '<BitmapSchema><SchemaId>1</SchemaId><DayMode><BitmapDirectory>%s</BitmapDirectory>'%(self.where)
        
        for node in self.renderHistory:                        
            bitmapSchemaString += '<Bitmap>\n<BitmapId>%s</BitmapId>\n<DefaultBitmapFileName>%s</DefaultBitmapFileName>\n</Bitmap>\n'%(node['id'],node['path'].replace('\n',''))
        
        # Add the end tag
        bitmapSchemaString += '</BitmapSchema>\n'
        
        # --------------------------------------------------------------------------------------------------------------------------------
        
        # Ok lets render the bitmap database section of the ddh
        
        for node in self.renderHistory:            
            iterator = iterator + 1
            bitmapDBString += '<Bitmap ddh:Name="%s">\n<BitmapId>%s</BitmapId>\n<BitmapRenderValue>FixedSize</BitmapRenderValue>\n</Bitmap>\n'%(iterator,node['id'])

    
    
        ddhDocString = ('<BitmapDatabase ddh:NextIdForDatabase="">\n' + bitmapSchemaString + bitmapDBString + '</BitmapDatabase>')
        
        # Let's create a file and write it to disk.
        filename = os.path.join(self.where, "ddh_sections.xml")        
            
        # Create a file object:
        # in "write" mode
        FILE = open(filename,"w")
        FILE.write(ddhDocString)
                        
        FILE.close()
        
        #self.debugLogger(ddhDocString)
        

    # Sub-optimal function just as "proof-of-concept"
    def renderCSSDoc(self):
        docString = ''
        
        iterator = 0
        
        # Ok lets render the bitmap schema section of the ddh
        docString = '<style>\n'
        topPos = 0
        for node in self.renderHistory:                        
            topPos = 1#(node['area']['y'] + node['height'])
            docString += '.%s {position:relative;top:%spx;left:%spx;}\n'%(node['id'],topPos,node['area']['y'])
        
        # Add the end tag
        docString += '</style>\n'
        
        # --------------------------------------------------------------------------------------------------------------------------------
            
        # Let's create a file and write it to disk.
        filename = os.path.join(self.where, "css.css")        
            
        # Create a file object:
        # in "write" mode
        FILE = open(filename,"w")
        FILE.write(docString)
                        
        FILE.close()
        
        #self.debugLogger(docString)


    def effect(self):
    
        """
        Effect behaviour.
        Overrides base class method
        """

        self.svg_file = self.args[-1]

        # Get script's "--what" option value.
        self.what = self.options.what

        # Get script's "--where" option value.
        self.where = self.options.where
        
        # Get the handle for the parser process. In this case Inkscape is used.
        #self.parserProcessHandle = self.getParserSession()

        self.parseDoc()
        
        self.renderCSSDoc()
        
        #self.endParserSession()


    def debugLogger(self,textStr):
        debugLayer = self.document.xpath('//svg:svg/svg:g',namespaces=inkex.NSS)[0]
        
        # Create text element
        text = inkex.etree.Element(inkex.addNS('text','svg'))
        text.text = str(textStr)

        # Set text position to center of document.
        text.set('x', str(300 / 2))
        text.set('y', str(300 / 2))

        # Center text horizontally with CSS style.
        style = {'text-align' : 'center', 'text-anchor': 'middle'}
        text.set('style', formatStyle(style))

        # Connect elements together.
        debugLayer.append(text)

# Create effect instance and apply it.
effect = ExportToAny()
effect.affect()

"""
def getParserSession(self):
        command = "inkscape --shell"
        processHandle = subprocess.Popen(command,
                   shell=True,
                   stdout=subprocess.PIPE,
                   stdin=subprocess.PIPE)
        return processHandle

def endParserSession(self):
        command = "exit"
        stdout_value = self.parserProcessHandle.communicate(command)
        return repr(stdout_value)
"""