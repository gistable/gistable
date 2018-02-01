"""
Script to import multiple directories with textile files into Confluence Wikis. Can be used with OnDemand instances.

To use as redmine migration tool, you need to export wiki pages in textile format. One way is described in: http://stbuehler.de/blog/article/2011/06/04/exporting_redmine_wiki_pages.html


~/redmine $ RAILS_ENV=production ./script/console -s

def export_text(p)
  c = p.content_for_version(nil)
  "#{c.text}"
end

def export_wiki(dir, wiki)
  dir = dir + "/" + wiki.project.identifier
  Dir.mkdir(dir)
  wiki.pages.each { |p|File.open(dir + "/" + p.title + ".textile", "w") { |f| f.write(export_text(p)) } }
  true
end

Project.all

export_wiki("/tmp", Project.find(2).wiki)

"""

import sys
import os
import re
from xmlrpclib import ServerProxy, Fault

# Connects to confluence server with username and password
site_URL = "https://yoursite.atlassian.net/wiki/"
server = ServerProxy(site_URL + "/rpc/xmlrpc")

username = "confluence_username"
pwd = "confluence_password" 
token = server.confluence2.login(username, pwd)

spaces = {
  "your_redmine_project_name":"CONFLUENCECODE"
}

def save(space, filename, pagename):
	# Retrives text from a file
	f = open(filename, 'r')
	content = f.readlines()
	content = '\n'.join(content[1:])
	content = re.subn(r'([{}])',r'\\\1',content, flags=re.S)[0]
	content = re.subn(r'@(.*?)@',r'{{\1}}}',content)[0]
	content = re.subn(r'<pre>(.*?)</pre>',r'{code}\1{code}',content, flags=re.S)[0]
	f.close()

	# Creates a new page to insert in the new space from text file content

	content = server.confluence2.convertWikiToStorageFormat(token, content)

	newpage = {"title":pagename, "space":space, "content":content}
	server.confluence2.storePage(token, newpage)

for project_dir, subdirs, files in os.walk('.'):
	try:
		project_name = project_dir.split('/')[1]
	except IndexError:
		continue
	for filename in files:
		if filename[-8:] == '.textile':
			pagename = filename[:-8].replace('_',' ').strip()
		else:
			continue
		try:
			server.confluence2.getPage(token,spaces[project_name],pagename)
		except KeyError:
			print "Project %s not mapped" % project_name
			break
		except Fault:
			pass
		else: 
			print "Page %s exists" % pagename
			continue

		print "Saving page %s"% pagename
		save(spaces[project_name], os.path.join(project_dir,filename),pagename) 

server.confluence2.logout(token)
