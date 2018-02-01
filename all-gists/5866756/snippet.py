# -*- coding: utf-8 -*-
"""
    sphinx.builders.mobi
    ~~~~~~~~~~~~~~~~~~~~

    Build mobi files.
    Originally derived from epub.py.

    :copyright: Copyright 2007-2011 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import os
import re
import shutil
import sys
import time
import codecs
import zipfile
import subprocess
from os import path

from docutils import nodes

from sphinx import addnodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.osutil import EEXIST, make_filename
from sphinx.util.smartypants import sphinx_smarty_pants as ssp


# (Fragment) templates from which the metainfo files content.opf, toc.ncx,
# mimetype, and META-INF/container.xml are created.
# This template section also defines strings that are embedded in the html
# output but that may be customized by (re-)setting module attributes,
# e.g. from conf.py.

_mimetype_template = 'application/x-mobipocket-ebook' # no EOL!

_container_template = u'''\
<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0"
      xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf"
        media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
'''

_toc_template = u'''\
<?xml version="1.0"?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
    <meta name="dtb:uid" content="%(uid)s"/>
    <meta name="dtb:depth" content="%(level)d"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>%(title)s</text>
  </docTitle>
  <navMap>
%(navpoints)s
  </navMap>
</ncx>
'''

_navpoint_template = u'''\
%(indent)s  <navPoint id="%(navpoint)s" playOrder="%(playorder)d">
%(indent)s    <navLabel>
%(indent)s      <text>%(text)s</text>
%(indent)s    </navLabel>
%(indent)s    <content src="%(refuri)s" />
%(indent)s  </navPoint>'''

_navpoint_indent = '  '
_navPoint_template = 'navPoint%d'

_content_template = u'''\
<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0"
      unique-identifier="%(uid)s">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf"
        xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:language>%(lang)s</dc:language>
    <dc:title>%(title)s</dc:title>
    <dc:creator opf:role="aut">%(author)s</dc:creator>
    <dc:publisher>%(publisher)s</dc:publisher>
    <dc:rights>%(copyright)s</dc:rights>
    <dc:identifier id="%(uid)s" opf:scheme="%(scheme)s">%(id)s</dc:identifier>
    <dc:date>%(date)s</dc:date>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
%(files)s
  </manifest>
  <spine toc="ncx">
%(spine)s
  </spine>
  <guide>
    <reference Type="toc" title="Table of Contents" href="index.html" />
  </guide>
</package>
'''

_cover_template = u'''\
    <meta name="cover" content="%(cover)s"/>
'''

_file_template = u'''\
    <item id="%(id)s"
          href="%(href)s"
          media-type="%(media_type)s" />'''

_spine_template = u'''\
    <itemref idref="%(idref)s" />'''

_toctree_template = u'toctree-l%d'

_link_target_template = u' [%(uri)s]'

_css_link_target_class = u'link-target'

_media_types = {
    '.html': 'application/xhtml+xml',
    '.css': 'text/css',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.otf': 'application/x-font-otf',
    '.ttf': 'application/x-font-ttf',
}

# Regular expression to match colons only in local fragment identifiers.
# If the URI contains a colon before the #,
# it is an external link that should not change.
_refuri_re = re.compile("([^#:]*#)(.*)")


def clean_html_file_for_kindle(filename):
    def replace_tag(tag_old, tag_new, txt):
        txt = txt.replace("<" + tag_old, "<" + tag_new)
        return txt.replace("</{0}>".format(tag_old), "</{0}>".format(tag_new))

    bakname = filename + ".bak"
    shutil.move(filename, bakname)
    destination = open(filename, 'w')
    original = open(bakname, 'r')

    for txt in original:
        txt = replace_tag("span", "samp", txt)
        #txt = replace_tag("pre", "code", txt)
        destination.write(txt)

    destination.close()
    original.close()
    os.remove(bakname)


# The mobi publisher

class MobiBuilder(StandaloneHTMLBuilder):
    """
    Builder that outputs mobi files.

    It creates the metainfo files container.opf, toc.ncx, mimetype, and
    META-INF/container.xml.  Afterwards, all necessary files are zipped to an
    mobi file.
    """
    name = 'mobi'

    # don't copy the reST source
    copysource = False
    supported_image_types = ['image/svg+xml', 'image/png', 'image/gif',
                             'image/jpeg']

    # don't add links
    add_permalinks = False
    # don't add sidebar etc.
    embedded = True

    def init(self):
        StandaloneHTMLBuilder.init(self)
        # the output files for mobi must be .html only
        self.out_suffix = '.html'
        self.playorder = 0

    def get_theme_config(self):
        return self.config.mobi_theme, {}

    # generic support functions
    def make_id(self, name):
        """Replace all characters not allowed for (X)HTML ids."""
        return name.replace('/', '_').replace(' ', '')

    def esc(self, name):
        """Replace all characters not allowed in text an attribute values."""
        # Like cgi.escape, but also replace apostrophe
        name = name.replace('&', '&amp;')
        name = name.replace('<', '&lt;')
        name = name.replace('>', '&gt;')
        name = name.replace('"', '&quot;')
        name = name.replace('\'', '&#39;')
        return name

    def get_refnodes(self, doctree, result):
        """Collect section titles, their depth in the toc and the refuri."""
        # XXX: is there a better way than checking the attribute
        # toctree-l[1-8] on the parent node?
        if isinstance(doctree, nodes.reference) and doctree.has_key('refuri'):
            refuri = doctree['refuri']
            if refuri.startswith('http://') or refuri.startswith('https://') \
                or refuri.startswith('irc:') or refuri.startswith('mailto:'):
                return result
            classes = doctree.parent.attributes['classes']
            for level in range(8, 0, -1): # or range(1, 8)?
                if (_toctree_template % level) in classes:
                    result.append({
                        'level': level,
                        'refuri': self.esc(refuri),
                        'text': ssp(self.esc(doctree.astext()))
                    })
                    break
        else:
            for elem in doctree.children:
                result = self.get_refnodes(elem, result)
        return result

    def get_toc(self):
        """Get the total table of contents, containg the master_doc
        and pre and post files not managed by sphinx.
        """
        doctree = self.env.get_and_resolve_doctree(self.config.master_doc,
            self, prune_toctrees=False)
        self.refnodes = self.get_refnodes(doctree, [])
        master_dir = os.path.dirname(self.config.master_doc)
        if master_dir:
            master_dir += '/' # XXX or os.sep?
            for item in self.refnodes:
                item['refuri'] = master_dir + item['refuri']
        self.refnodes.insert(0, {
            'level': 1,
            'refuri': self.esc(self.config.master_doc + '.html'),
            'text': ssp(self.esc(
                    self.env.titles[self.config.master_doc].astext()))
        })
        for file, text in reversed(self.config.mobi_pre_files):
            self.refnodes.insert(0, {
                'level': 1,
                'refuri': self.esc(file),
                'text': ssp(self.esc(text))
            })
        for file, text in self.config.mobi_post_files:
            self.refnodes.append({
                'level': 1,
                'refuri': self.esc(file),
                'text': ssp(self.esc(text))
            })

    def fix_fragment(self, prefix, fragment):
        """Return a href/id attribute with colons replaced by hyphens."""
        return prefix + fragment.replace(':', '-')

    def fix_ids(self, tree):
        """Replace colons with hyphens in href and id attributes.

        Some readers crash because they interpret the part as a
        transport protocol specification.
        """
        for node in tree.traverse(nodes.reference):
            if 'refuri' in node:
                m = _refuri_re.match(node['refuri'])
                if m:
                    node['refuri'] = self.fix_fragment(m.group(1), m.group(2))
            if 'refid' in node:
                node['refid'] = self.fix_fragment('', node['refid'])
        for node in tree.traverse(addnodes.desc_signature):
            ids = node.attributes['ids']
            newids = []
            for id in ids:
                newids.append(self.fix_fragment('', id))
            node.attributes['ids'] = newids

    def add_visible_links(self, tree):
        """Append visible link targets after external links."""
        for node in tree.traverse(nodes.reference):
            uri = node.get('refuri', '')
            if (uri.startswith('http:') or uri.startswith('https:') or
                    uri.startswith('ftp:')) and uri not in node.astext():
                uri = _link_target_template % {'uri': uri}
                if uri:
                    idx = node.parent.index(node) + 1
                    link = nodes.inline(uri, uri)
                    link['classes'].append(_css_link_target_class)
                    node.parent.insert(idx, link)

    def write_doc(self, docname, doctree):
        """Write one document file.

        This method is overwritten in order to fix fragment identifiers
        and to add visible external links.
        """
        self.fix_ids(doctree)
        if self.config.mobi_add_visible_links:
            self.add_visible_links(doctree)
        return StandaloneHTMLBuilder.write_doc(self, docname, doctree)

    def fix_genindex(self, tree):
        """Fix href attributes for genindex pages."""
        # XXX: modifies tree inline
        # Logic modeled from themes/basic/genindex.html
        for key, columns in tree:
            for entryname, (links, subitems) in columns:
                for (i, (ismain, link)) in enumerate(links):
                    m = _refuri_re.match(link)
                    if m:
                        links[i] = (ismain,
                                    self.fix_fragment(m.group(1), m.group(2)))
                for subentryname, subentrylinks in subitems:
                    for (i, (ismain, link)) in enumerate(subentrylinks):
                        m = _refuri_re.match(link)
                        if m:
                            subentrylinks[i] = (ismain,
                                self.fix_fragment(m.group(1), m.group(2)))

    def handle_page(self, pagename, addctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        """Create a rendered page.

        This method is overwritten for genindex pages in order to fix href link
        attributes.
        """
        if pagename.startswith('genindex'):
            self.fix_genindex(addctx['genindexentries'])
        StandaloneHTMLBuilder.handle_page(self, pagename, addctx, templatename,
            outfilename, event_arg)


    # Finish by building the mobi file
    def handle_finish(self):
        """Create the metainfo files and finally the mobi."""
        self.get_toc()
        self.build_mimetype(self.outdir, 'mimetype')
        self.build_container(self.outdir, 'META-INF/container.xml')
        self.build_content(self.outdir, 'content.opf')
        self.build_toc(self.outdir, 'toc.ncx')

        # we build an epub for now
        self.cleanup_files()

        mobi_name = self.config.mobi_basename + '.mobi'
        fullname = os.path.join(self.outdir, "content.opf")
        subprocess.call(["kindlegen", "-c1", fullname, "-o", mobi_name])


    def build_mimetype(self, outdir, outname):
        """Write the metainfo file mimetype."""
        self.info('writing %s file...' % outname)
        f = codecs.open(path.join(outdir, outname), 'w', 'utf-8')
        try:
            f.write(_mimetype_template)
        finally:
            f.close()

    def build_container(self, outdir, outname):
        """Write the metainfo file META-INF/cointainer.xml."""
        self.info('writing %s file...' % outname)
        fn = path.join(outdir, outname)
        try:
            os.mkdir(path.dirname(fn))
        except OSError, err:
            if err.errno != EEXIST:
                raise
        f = codecs.open(path.join(outdir, outname), 'w', 'utf-8')
        try:
            f.write(_container_template)
        finally:
            f.close()

    def content_metadata(self, files, spine):
        """Create a dictionary with all metadata for the content.opf
        file properly escaped.
        """
        metadata = {}
        metadata['title'] = self.esc(self.config.mobi_title)
        metadata['author'] = self.esc(self.config.mobi_author)
        metadata['uid'] = self.esc(self.config.mobi_uid)
        metadata['lang'] = self.esc(self.config.mobi_language)
        metadata['publisher'] = self.esc(self.config.mobi_publisher)
        metadata['copyright'] = self.esc(self.config.mobi_copyright)
        metadata['scheme'] = self.esc(self.config.mobi_scheme)
        metadata['id'] = self.esc(self.config.mobi_identifier)
        metadata['date'] = self.esc(time.strftime('%Y-%m-%d'))
        metadata['files'] = files
        metadata['spine'] = spine
        return metadata

    def build_content(self, outdir, outname):
        """Write the metainfo file content.opf It contains bibliographic data,
        a file list and the spine (the reading order).
        """
        self.info('writing %s file...' % outname)

        # files
        if not outdir.endswith(os.sep):
            outdir += os.sep
        olen = len(outdir)
        projectfiles = []
        self.files = []
        self.ignored_files = ['.buildinfo',
            'mimetype', 'content.opf', 'toc.ncx', 'META-INF/container.xml',
            self.config.mobi_basename + '.mobi'] + \
            self.config.mobi_exclude_files
        for root, dirs, files in os.walk(outdir):
            for fn in files:
                filename = path.join(root, fn)[olen:]
                if filename in self.ignored_files:
                    continue
                ext = path.splitext(filename)[-1]
                if ext not in _media_types:
                    self.warn('unknown mimetype for %s, ignoring' % filename)
                    continue
                projectfiles.append(_file_template % {
                    'href': self.esc(filename),
                    'id': self.esc(self.make_id(filename)),
                    'media_type': self.esc(_media_types[ext])
                })
                self.files.append(filename)

        # spine
        spine = []
        for item in self.refnodes:
            if '#' in item['refuri']:
                continue
            if item['refuri'] in self.ignored_files:
                continue
            spine.append(_spine_template % {
                'idref': self.esc(self.make_id(item['refuri']))
            })
        for info in self.domain_indices:
            spine.append(_spine_template % {
                'idref': self.esc(self.make_id(info[0] + self.out_suffix))
            })
        if self.config.html_use_index:
            spine.append(_spine_template % {
                'idref': self.esc(self.make_id('genindex' + self.out_suffix))
            })

        # add the optional cover
        content_tmpl = _content_template
        if self.config.mobi_cover:
            image = self.config.mobi_cover
            mpos = content_tmpl.rfind('</metadata>')
            cpos = content_tmpl.rfind('\n', 0 , mpos) + 1
            content_tmpl = content_tmpl[:cpos] + \
                _cover_template % {'cover': self.esc(self.make_id(image))} + \
                content_tmpl[cpos:]

        projectfiles = '\n'.join(projectfiles)
        spine = '\n'.join(spine)

        # write the project file
        f = codecs.open(path.join(outdir, outname), 'w', 'utf-8')
        try:
            f.write(content_tmpl % \
                self.content_metadata(projectfiles, spine))
        finally:
            f.close()

    def new_navpoint(self, node, level, incr=True):
        """Create a new entry in the toc from the node at given level."""
        # XXX Modifies the node
        if incr:
            self.playorder += 1
        node['indent'] = _navpoint_indent * level
        node['navpoint'] = self.esc(_navPoint_template % self.playorder)
        node['playorder'] = self.playorder
        return _navpoint_template % node

    def insert_subnav(self, node, subnav):
        """Insert nested navpoints for given node.

        The node and subnav are already rendered to text.
        """
        nlist = node.rsplit('\n', 1)
        nlist.insert(-1, subnav)
        return '\n'.join(nlist)

    def build_navpoints(self, nodes):
        """Create the toc navigation structure.

        Subelements of a node are nested inside the navpoint.  For nested nodes
        the parent node is reinserted in the subnav.
        """
        navstack = []
        navlist = []
        level = 1
        lastnode = None
        for node in nodes:
            if not node['text']:
                continue
            file = node['refuri'].split('#')[0]
            if file in self.ignored_files:
                continue
            if node['level'] > self.config.mobi_tocdepth:
                continue
            if node['level'] == level:
                navlist.append(self.new_navpoint(node, level))
            elif node['level'] == level + 1:
                navstack.append(navlist)
                navlist = []
                level += 1
                if lastnode and self.config.mobi_tocdup:
                    # Insert starting point in subtoc with same playOrder
                    navlist.append(self.new_navpoint(lastnode, level, False))
                navlist.append(self.new_navpoint(node, level))
            else:
                while node['level'] < level:
                    subnav = '\n'.join(navlist)
                    navlist = navstack.pop()
                    navlist[-1] = self.insert_subnav(navlist[-1], subnav)
                    level -= 1
                navlist.append(self.new_navpoint(node, level))
            lastnode = node
        while level != 1:
            subnav = '\n'.join(navlist)
            navlist = navstack.pop()
            navlist[-1] = self.insert_subnav(navlist[-1], subnav)
            level -= 1
        return '\n'.join(navlist)

    def toc_metadata(self, level, navpoints):
        """Create a dictionary with all metadata for the toc.ncx file
        properly escaped.
        """
        metadata = {}
        metadata['uid'] = self.config.mobi_uid
        metadata['title'] = self.config.mobi_title
        metadata['level'] = level
        metadata['navpoints'] = navpoints
        return metadata

    def build_toc(self, outdir, outname):
        """Write the metainfo file toc.ncx."""
        self.info('writing %s file...' % outname)

        navpoints = self.build_navpoints(self.refnodes)
        level = max(item['level'] for item in self.refnodes)
        level = min(level, self.config.mobi_tocdepth)
        f = codecs.open(path.join(outdir, outname), 'w', 'utf-8')
        try:
            f.write(_toc_template % self.toc_metadata(level, navpoints))
        finally:
            f.close()

    def cleanup_files(self):
        """Write the mobi file using kindlegen."""

        self.info('cleaning html files...')
        for item in self.files:
            if item.endswith("html"):
                clean_html_file_for_kindle(os.path.join(self.outdir, item))


def setup(app):
    app.add_config_value('mobi_basename',lambda self: make_filename(self.project), None)
    app.add_config_value('mobi_theme','mobi', 'html')
    app.add_config_value('mobi_title',lambda self: self.html_title, 'html')
    app.add_config_value('mobi_author','unknown', 'html')
    app.add_config_value('mobi_language',lambda self: self.language or 'en', 'html')
    app.add_config_value('mobi_publisher','unknown', 'html')
    app.add_config_value('mobi_copyright',lambda self: self.copyright, 'html')
    app.add_config_value('mobi_identifier','unknown', 'html')
    app.add_config_value('mobi_scheme','unknown', 'html')
    app.add_config_value('mobi_uid','unknown', 'env')
    app.add_config_value('mobi_cover',(), 'env')
    app.add_config_value('mobi_pre_files',[], 'env')
    app.add_config_value('mobi_post_files',[], 'env')
    app.add_config_value('mobi_exclude_files',[], 'env')
    app.add_config_value('mobi_tocdepth',3, 'env')
    app.add_config_value('mobi_tocdup',True, 'env')
    app.add_config_value('mobi_add_visible_links',True, 'env')

    app.add_builder(MobiBuilder)
