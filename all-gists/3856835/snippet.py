# -*- coding: utf-8 -*-

import sys, os

sys.path.insert(0, os.path.abspath('extensions'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.todo',
              'sphinx.ext.coverage', 'sphinx.ext.pngmath', 'sphinx.ext.ifconfig',
              'epub2', 'mobi', 'autoimage', 'code_example']

todo_include_todos = True
templates_path = ['_templates']
source_suffix = '.rst'
main_doc = 'index'
exclude_patterns = []
add_function_parentheses = True
#add_module_names = True
# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

project = u'Music for Geeks and Nerds'
copyright = u'2012, Pedro Kroger'

version = ''
release = ''

# -- Options for HTML output ---------------------------------------------------

html_theme = 'book'
html_theme_path = ['themes']
html_title = "Music for Geeks and Nerds"
#html_short_title = None
#html_logo = None
#html_favicon = None
html_static_path = ['_static']
html_domain_indices = False
html_use_index = False
html_show_sphinx = False
htmlhelp_basename = 'MusicforGeeksandNerdsdoc'
html_show_sourcelink = False

# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
     'papersize': '',
     'fontpkg': '',
     'fncychap': '',
     'maketitle': '\\cover',
     'pointsize': '',
     'preamble': '',
     'releasename': "",
     'babel': '',
     'printindex': '',
     'fontenc': '',
     'inputenc': '',
     'classoptions': '',
     'utf8extra': '',
     
}

latex_additional_files = ["mfgan-bw.sty", "mfgan.sty", "_static/cover.png"]

latex_documents = [
  ('index', 'music-for-geeks-and-nerds.tex', u'Music for Geeks and Nerds',
   u'Pedro Kroger', 'manual'),
]

latex_show_pagerefs = False
latex_domain_indices = False
latex_use_modindex = False
#latex_logo = None
#latex_show_urls = False

# -- Options for Epub output ---------------------------------------------------

epub_title = u'Music for Geeks and Nerds'
epub_author = u'Pedro Kroger'
epub_publisher = u'Pedro Kroger'
epub_copyright = u'2012, Pedro Kroger'

epub_theme = 'epub2'

# The scheme of the identifier. Typical schemes are ISBN or URL.
#epub_scheme = ''

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#epub_identifier = ''

# A unique identification for the text.
#epub_uid = ''

# A tuple containing the cover image and cover page html template filenames.
epub_cover = ("_static/cover.png", "epub-cover.html")

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_post_files = []

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['_static/opensearch.xml', '_static/doctools.js',
    '_static/jquery.js', '_static/searchtools.js', '_static/underscore.js',
    '_static/basic.css', 'search.html', '_static/websupport.js']

# The depth of the table of contents in toc.ncx.
epub_tocdepth = 2

# Allow duplicate toc entries.
epub_tocdup = False


# -- Options for Mobi output ---------------------------------------------------

mobi_theme = "mobi"
mobi_title = u'Music for Geeks and Nerds'
mobi_author = u'Pedro Kroger'
mobi_publisher = u'Pedro Kroger'
mobi_copyright = u'2012, Pedro Kroger'

# The scheme of the identifier. Typical schemes are ISBN or URL.
#mobi_scheme = ''

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#mobi_identifier = ''

# A unique identification for the text.
#mobi_uid = ''

mobi_cover = "_static/cover.png"

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#mobi_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#mobi_post_files = []

# A list of files that should not be packed into the mobi file.
mobi_exclude_files = ['_static/opensearch.xml', '_static/doctools.js',
    '_static/jquery.js', '_static/searchtools.js', '_static/underscore.js',
    '_static/basic.css', 'search.html', '_static/websupport.js']

# The depth of the table of contents in toc.ncx.
mobi_tocdepth = 2

# Allow duplicate toc entries.
mobi_tocdup = False

mobi_add_visible_links = False


# -- Options for Code Examples output ---------------------------------------------------


code_example_dir = "code-example"
code_add_python_path = ["../py"]


################################################################################


def setup(app):
     from sphinx.util.texescape import tex_replacements
     tex_replacements += [(u'♮', u'$\\natural$'),
                          (u'ē', u'\=e'),
                          (u'♩', u'\quarternote'),
                          (u'↑', u'$\\uparrow$'),
                          ]
