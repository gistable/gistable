# -- encoding: utf-8 --
""" A fairly advanced HTML/HTML5 compressor. """

from __future__ import with_statement
import re
from itertools import chain

HTML5_BLOCKS = set(
	'head body title link '
	'article aside nav section '
	'h1 h2 h3 h4 h5 h6 hgroup p'.strip().split()
)
HTML5_BLOCKS_RE_FRAG = "(%s)" % ("|".join(re.escape(b) for b in sorted(HTML5_BLOCKS)))
STRAY_LEAD_WS_RE = re.compile(r"^\s+", re.MULTILINE)
STRAY_TRAIL_WS_RE = re.compile(r"\s+$", re.MULTILINE)
QUOTED_PARAM_RE = re.compile(r'([a-z]+)=\"([-._:/a-z0-9]+)\"', re.I)
XHTML_CLOSE_RE = re.compile(r'\s+/>')
WS_BEFORE_BLOCK_START = re.compile(r'\s+(<%s>)' % HTML5_BLOCKS_RE_FRAG, re.I)
WS_AFTER_BLOCK_START = re.compile(r'(<%s>)\s+' % HTML5_BLOCKS_RE_FRAG, re.I)
WS_BEFORE_BLOCK_END = re.compile(r'\s+(</%s>)' % HTML5_BLOCKS_RE_FRAG, re.I)
WS_AFTER_BLOCK_END = re.compile(r'(</%s>)\s+' % HTML5_BLOCKS_RE_FRAG, re.I)
NEWLINE_RE = re.compile(r'[\r\n]+')
EMPTY_PARAM_RE = re.compile(r'(rel|id|class)=\"\s*\"')
NEWLINE_SEP_PARAM_RE = re.compile(r'[\r\n]+(\w+=[\"\'])')
CLEAN_SIMPLE_TAG_RE = re.compile(r'<\s*(\w+)\s*>')
SIMPLE_TEXT_TAG_RE = re.compile(r'<(?P<tag>a)(?P<params>.*)>(?P<content>[\w\s&;\n]+)</(?P=tag)>', re.UNICODE)


def unquote(match):
	""" Internal: Unquote an HTML attribute. In cases such as defer="defer", turn them into just defer. """
	name = match.group(1)
	val = match.group(2)
	if name == val:
		return name
	return "%s=%s" % (name, val)


# List of conservative replacements.
conservativeReps = (
	(	# Clean line-starting and line-ending whitespaces.
		(STRAY_TRAIL_WS_RE, STRAY_LEAD_WS_RE),
		""
	),
	(	# Clean whitespaces before and after block starts and ends.
		(WS_BEFORE_BLOCK_START, WS_BEFORE_BLOCK_END, WS_AFTER_BLOCK_END, WS_AFTER_BLOCK_START),
		r'\1'
	),
)

# List of drastic replacements.
drasticReps = (
	(	# Turn XHTML closing tags (/>) into HTML closing tags (>)
		(XHTML_CLOSE_RE, ),
		'>'
	),
	(	# Remove empty parameters
		(EMPTY_PARAM_RE, ),
		""
	),
	(	# ensure parameters are delimited by spaces
		(NEWLINE_SEP_PARAM_RE, ),
		r" \1"
	),
	(	# Unquote HTML parameters that are safe to unquote.
		(QUOTED_PARAM_RE, ),
		unquote
	),
	(	# ensure simple tags (after empty-params) don't have spaces in them
		(CLEAN_SIMPLE_TAG_RE, ),
		r"<\1>"
	),
	(	# ensure <a href="ccc">             a                   </a> turns into something saner
		(SIMPLE_TEXT_TAG_RE, ),
		lambda m: "<%s%s>%s</%s>" % (m.group("tag"), m.group("params"), m.group("content").strip(), m.group("tag"))
	),
	
)


def squeeze_html(html, conservative=False):
	""" Squeeze every single spare byte out of the given HTML. If 'conservative' is set, attempt to retain XHTML compliance. """
	reps = (conservativeReps if conservative else chain(conservativeReps, drasticReps))
	for rs, rep in reps:
		for r in rs:
			html = r.sub(rep, html)
	html = NEWLINE_RE.sub("\n", html).strip()
	return html

def cmdline():
	import argparse
	ap = argparse.ArgumentParser("squeeze")
	ap.add_argument("files", nargs="+")
	ap.add_argument("--conservative", "-c", default = False, action="store_true")
	opts = ap.parse_args()
	for filename in opts.files:
		with file(filename, "rb") as in_file:
			print squeeze_html(in_file.read(), bool(opts.conservative))
	

if __name__ == '__main__':
	cmdline()