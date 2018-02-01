from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from zipfile import ZipFile
from string import join
import os
import re

def getMavenCoordinates(elements):
    return dict(zip(('group', 'artifact', 'version'), elements))
    
def getMavenArtifactName(coordinates):
    return coordinates['artifact'] + '-' + coordinates['version'] + '-javadoc.jar' 
    
def mavenGroupToPath(group):
    return group.replace('.', '/')

def getMavenPath(base_dir, elements):
    coordinates = getMavenCoordinates(elements)
    group_path = mavenGroupToPath(coordinates['group'])
    artifact_name = getMavenArtifactName(coordinates)
    artifact_id = coordinates['artifact']
    version = coordinates['version']
    return '/'.join((base_dir, group_path, artifact_id, version, artifact_name))
    
def findMavenJavadocArtifacts(base_dir):
    base_directory = os.path.expanduser(base_dir)
    projects = list()
    for (path, dirs, files) in os.walk(base_directory):
        files = [f for f in files if re.match('.*-javadoc.jar$', f)]
        if len(files) > 0:
            projects.append(path.replace(base_dir, ''))
    return projects
    
def outputIndex(wfile, projects):
   wfile.write('<html><body>')
   for project in projects:
       parts = project.split('/')
       version = parts.pop()
       artifact = parts.pop()
       parts.pop(0)
       group = '.'.join(parts)
       print group, artifact, version 
       wfile.write("<a href=\"m2/%s/%s/%s/index.html\">%s:%s:%s</a><br/>\n" % (group, artifact, version, group, artifact, version))
   wfile.write('</body></html>') 

"""
Serve javadocs from ~/.m2/repository
URL: http://localhost:8080/m2/[groupId]/[artifactId]/[version]/[path]
It's still a little crude so you have to append index.html to the end
"""
class Handler(BaseHTTPRequestHandler):
    def do_GET(this):
        base_dir = os.path.expanduser('~/.m2/repository')
        path_elements = this.path.split('/')
        (repo_type, elements) = path_elements[1], path_elements[2:]
        archive_path = None
        if repo_type == 'm2':
            if len(elements) == 0:
                outputIndex(this.wfile, findMavenJavadocArtifacts(base_dir))
            else:
                try:
                    docs = ZipFile(getMavenPath(base_dir, elements))
                    this.wfile.write(docs.read('/'.join(elements[3:])))
                except:
                    pass
                else:    
                    docs.close()     
            

httpd = HTTPServer(('', 8080), Handler)
httpd.serve_forever()