# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2007-2011 by the Sphinx team, see AUTHORS.
:copyright: Copyright 2013 Maciej Stankiewicz
:license: BSD, see LICENSE for details.


If refferede resource is a folder, it is automaticaly packed to zip file.

From now on one can referr to folders like to files:
    :download:`downloads/tutorial_01/`
Trailing slash is optional, but using it You can easily distinguish
what is referred in download role.  If "tutorial_01" is a folder,
"tutorial_01.zip" will be created and stored # in common place for downloads.

How to use it?

1. Store download.py in visible place (usualy Your Sphinx project)
2. In conf.py of your Sphinx project add this fix to extensions list

Tested on Sphinx 1.1.3 + Python 2.7
(should work with Python 3.x)
"""




import os
import sys
import zipfile

if sys.version_info[:3] >= (3, 0, 0):
	from urllib.request import pathname2url
else:
	from urllib import pathname2url	

from sphinx import addnodes
from sphinx.util.console import brown
from sphinx.util.osutil import ensuredir, copyfile
from sphinx.environment import BuildEnvironment
from sphinx.writers.html import HTMLTranslator
from sphinx.builders.html import StandaloneHTMLBuilder


def injectMethodInto(obj):
	def wrapper(f):
		name = f.__name__
		if hasattr(obj, name):
			if not hasattr(obj, "__orig__"):
				obj.__orig__ = {}
			obj.__orig__[name] = getattr(obj, name)
		setattr(obj, name, f)
	return wrapper


@injectMethodInto(BuildEnvironment)
def process_downloads(self, docname, doctree):
	"""Process downloadable file paths. """
	for node in doctree.traverse(addnodes.download_reference):
		targetname = node['reftarget']
		rel_filename, filename = self.relfn2path(targetname, docname)
		### {{{ Modification
		# add new property
		node['refisfolder'] = os.path.isdir(filename)
		### Modification }}}
		self.dependencies.setdefault(docname, set()).add(rel_filename)
		if not os.access(filename, os.R_OK):
			self.warn_node('download file not readable: %s' % filename, node)
			continue
		uniquename = self.dlfiles.add_file(docname, filename)
		node['filename'] = uniquename


@injectMethodInto(HTMLTranslator)
def visit_download_reference(self, node):
	if node.hasattr('filename'):
		### {{{ Modification
		filename = node['filename']
		if node['refisfolder']:
			filename += ".zip"
		## FIX: was:
		# self.body.append(
        #       '<a class="reference download internal" href="%s">'
        #       % posixpath.join(self.builder.dlpath, filename))
		## FIX: is:
		self.body.append(
            '<a class="reference download internal" href="%s">'
            % pathname2url(os.path.join(self.builder.dlpath, filename)))
		### Modification }}}
		self.context.append('</a>')
	else:
		self.context.append('')


@injectMethodInto(StandaloneHTMLBuilder)
def copy_download_files(self):
	# copy downloadable files
	if self.env.dlfiles:
		### {{{ Modification
		destFolder = os.path.join(self.outdir, '_downloads')
		ensuredir(destFolder)
		for src in self.status_iterator(self.env.dlfiles,
                                        'copying downloadable files... ',
                                        brown, len(self.env.dlfiles)):
			destFile = self.env.dlfiles[src][1]
			if os.path.isdir(src):
				# compress folder and save as zip archive
				destFile += ".zip"
				archivePath = os.path.join(destFolder, destFile)
				try:
					srcBaseLen = len(src) + 1
					archive = zipfile.ZipFile(archivePath,
                                              'w',
                                              compression=zipfile.ZIP_DEFLATED)
					for base, dirs, files in os.walk(src):
						for f in files:
							fn = os.path.join(base, f)
							archive.write(fn, fn[srcBaseLen:])
					archive.close()
				except Exception, err:
					self.warn('cannot compressed folder %r: %s' % (src, err))
				else:
					self.info('    folder compressed to %s' % archivePath)
			else:	
				# copy file
				try:
					copyfile(os.path.join(self.srcdir, src),
                        os.path.join(destFolder, destFile))
				except Exception, err:
					self.warn(
                        'cannot copy downloadable file %r: %s' %
                        (os.path.join(self.srcdir, src), err))
		### SDFG Modification}}}


def setup(app):
	pass
