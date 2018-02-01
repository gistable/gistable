#!/usr/bin/python
#
# mm2fm - Mind Manager to FreeMind file converter
#
# Copyright (C) 2007 David Symons <david.symons@liberatedcomputing.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Dependencies: python, python-libxml2, python-libxslt1
#
# Instructions: Make the file executable and put it somewhere in your PATH.
# Also see 'mm2fm --help'.

import libxml2
import libxslt
import os.path
import sys
import zipfile

version = '0.1'
usage = """
Usage: mm2fm file [file ...]

For more details see 'mm2fm --help'
"""

if len(sys.argv) < 2:
  print usage
  sys.exit()

elif sys.argv[1] == "--help":
  print usage
  print """Converts a file or group of files to Freemind format. Creates new files using the existing filename but with a .mm extension.

Examples: mm2fm MyMap.mmap
          mm2fm MyMap1.mmap MyMap2.mmap
          mm2fm *.mmap
"""
  sys.exit()

elif sys.argv[1] == "--version":
  print """
Version: %s
""" % version
  sys.exit()

# The XSLT stylesheet. It was added to the Freemind wiki[1] by unnamed
# contributor. Many thanks and kudos to him/her as this really is the magic in
# this program.
#
# [1] http://freemind.sourceforge.net/wiki/index.php/Import_and_export_to_other_applications
#
stylesheet = """<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ap="http://schemas.mindjet.com/MindManager/Application/2003"
>
      <xsl:output
        method="xml"
      version="1.0"
      encoding="iso-8859-1"
      omit-xml-declaration="yes"
      indent="yes"
      /> 
  <xsl:template match="/">
    <xsl:element name="map">
      <xsl:attribute name="version">0.7.1</xsl:attribute>
      <xsl:apply-templates select="ap:Map/ap:OneTopic/ap:Topic" />
    </xsl:element>
  </xsl:template>
  <xsl:template match="ap:Topic">
    <xsl:element name="node">
      <xsl:attribute name="TEXT">
        <xsl:value-of select="ap:Text/@PlainText" />
      </xsl:attribute> <xsl:if test="ap:Text/ap:Font/@Color">
        <xsl:attribute name="COLOR">
          <xsl:value-of select="concat('#', substring(ap:Text/ap:Font/@Color, 3, 6))" />
        </xsl:attribute>
      </xsl:if>
      <xsl:variable name="OId" select="@OId" />
      <xsl:variable name="relation" select="/ap:Map/ap:Relationships/ap:Relationship[ap:ConnectionGroup[@Index=0]/ap:Connection/ap:ObjectReference/@OIdRef=$OId]" />
      <xsl:if test="$relation">
        <xsl:variable name="toId" select="$relation/ap:ConnectionGroup[@Index=1]/ap:Connection/ap:ObjectReference/@OIdRef" />
        <xsl:element name="arrowlink">
          <xsl:attribute name="ENDARROW">Default</xsl:attribute>
          <xsl:attribute name="DESTINATION">
            <xsl:value-of select="$relation/ap:ConnectionGroup[@Index=1]/ap:Connection/ap:ObjectReference/@OIdRef" />
          </xsl:attribute>
          <xsl:attribute name="STARTARROW">None</xsl:attribute>
        </xsl:element>
      </xsl:if>
      <xsl:variable name="toId" select="/ap:Map/ap:Relationships/ap:Relationship/ap:ConnectionGroup[@Index=1]/ap:Connection/ap:ObjectReference[@OIdRef=$OId]/@OIdRef" />
      <xsl:if test="$toId">
        <xsl:attribute name="ID">
          <xsl:value-of select="$toId" />
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="ap:SubTopics"/>
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>
"""

for filename in sys.argv[1:]:
  styledoc = libxml2.parseDoc(stylesheet)
  style = libxslt.parseStylesheetDoc(styledoc)
  f = open( filename, 'r' )
  z = zipfile.ZipFile( f )
  content = z.read( "Document.xml" )
  f.close()
  doc = libxml2.parseDoc( content )
  result = style.applyStylesheet(doc, None)
  str = style.saveResultToString(result)
  style.freeStylesheet()
  doc.freeDoc()
  result.freeDoc()
  outfile = open( os.path.splitext( filename )[0] + '.mm', 'w' )
  outfile.write( str )
  outfile.close()