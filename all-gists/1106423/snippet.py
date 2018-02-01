#!/usr/bin/env python
#
# Copyright (c) 2007, Hans Meine <hans_meine@gmx.net>
#  All rights reserved.
#
# This is licensed according to the new BSD license.
# Please send patches / comments, I would be happy about any feedback.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# * Neither the name of the University of Hamburg nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys, os.path, subprocess, glob, time, optparse, tempfile

op = optparse.OptionParser(usage="%prog [options] foo.tikz")
op.add_option("-v", "--verbose", action = "store_true", default = False,
			  dest = "verbose", help = "verbose output")
op.add_option("-o", "--once", action = "store_true",
			  dest = "once", default = False,
			  help = "only convert once, then clean up temporary files and quit")
op.add_option("-s", "--view", action = "store_true",
			  dest = "view", default = False,
			  help = "start viewer after first successful compilation")

options, args = op.parse_args()
tikzName, = args # exactly one filename expected

basename = "tikz2pdf_temp"
texName = basename + ".tex"
pdfName = basename + ".pdf"

templateFilename = os.path.expanduser("~/.tikz2pdf.tex")
searchDir = os.getcwd()
while searchDir != "/":
	candidate = os.path.join(searchDir, ".tikz2pdf.tex")
	if os.path.exists(candidate):
		templateFilename = candidate
		sys.stdout.write("Using template %r.\n" % candidate)
		break
	searchDir = os.path.split(searchDir)[0]

# re-use texdoc's configuration variables for viewing TeX's output:
viewCommand = "open %r"
texdocViewCommand = os.environ.get("TEXDOCVIEW_pdf", None)
if texdocViewCommand:
	viewCommand = texdocViewCommand.rstrip("&").replace("%s", "%r")

if os.path.exists(templateFilename):
	template = file(templateFilename).read()
else:
	template = r"""\documentclass{article}

\usepackage{tikz,nicefrac,amsmath,pifont}
\usetikzlibrary{arrows,snakes,backgrounds,patterns,matrix,shapes,fit,calc,shadows,plotmarks}

\usepackage[graphics,tightpage,active]{preview}
\PreviewEnvironment{tikzpicture}
\newlength{\imagewidth}
\newlength{\imagescale}

\begin{document}

\input{%s}

\end{document}
"""
	sys.stderr.write("INFO: '%s' did not exist, saving default template - please configure!\n" % templateFilename)
	file(templateFilename, "w").write(template)

file(texName, "w").write(template % tikzName)

def verboseUnlink(filename):
	# FIXME: check mtime
	if options.verbose:
		print "cleaning up %r..." % filename
	try:
		os.unlink(filename)
	except OSError, e:
		if e.errno != 2:
			raise e

viewer = None

previous = 0
while True:
	try:
		mtime = os.path.getmtime(tikzName)
		if mtime > previous:
			out = None
			print "tikz2pdf: calling pdflatex..."
			if not options.verbose:
				out = tempfile.TemporaryFile()
			ec = subprocess.call(
				["pdflatex", "-halt-on-error", texName], stdout = out)
			if ec:
				if out:
					out.seek(0)
					sys.stdout.write(out.read())
				print "tikz2pdf: ERROR generating %r with pdflatex." % pdfName
			else:
				print "tikz2pdf: Successfully generated %r." % pdfName
				if options.view and viewer is None:
					print "tikz2pdf: starting viewer..."
					viewer = subprocess.Popen(viewCommand % pdfName, shell = True)
			if out:
				out.close()

			previous = mtime
			if options.once:
				break
		time.sleep(1)
	except KeyboardInterrupt:
		verboseUnlink(pdfName)
		break

verboseUnlink(texName)
for temp in glob.glob("tikz2pdf_temp.*"):
	if temp != pdfName:
		verboseUnlink(temp)
# for ext in (".aux", ".log"):
# 	verboseUnlink(basename + ext)