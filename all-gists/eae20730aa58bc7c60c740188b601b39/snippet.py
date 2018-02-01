#!/usr/bin/python3

#
# Copyright(c) 2017 Daniel Knüttel
#

# This program is free software.
# Anyways if you think this program is worth it
# and we meet shout a drink for me.


#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
#    der GNU Affero General Public License, wie von der Free Software Foundation,
#    Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
#    veröffentlichten Version, weiterverbreiten und/oder modifizieren.
#
#    Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber
#    OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
#    Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
#    Siehe die GNU Affero General Public License für weitere Details.
#
#    Sie sollten eine Kopie der GNU Affero General Public License zusammen mit diesem
#    Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.


"""
alldoc -- extract reStructuredText docstrings from all 
sourcefiles.

This does include non-python files/languages.

Invoke alldoc using 
::

	python3 alldoc.py <outfile> <infile> {<infile>}



"""

import logging
# logging.basicConfig(level = logging.DEBUG)
logging.basicConfig()


start_alldoc = [ "<alldoc>", "<doc>", "startdoc", "SDOC"]
stop_alldoc = ["</alldoc>", "</doc>", "stopdoc", "EDOC"]

def indexof(str_, substr):
	"""
	This is handy if you want to get the next substr.
	"""
	try:
		return str_.index(substr)
	except:
		return float("inf")

def extract_docs(str_, start_alldoc = start_alldoc, stop_alldoc = stop_alldoc):
	"""
	Extract all docstrings starting with ``start_alldoc`` and stopping with
	``stop_alldoc``.

	For instance:
	::
		
		/*
		 <DOC>
		 This is a docstring
		 </DOC>
		 */
	
	"""
	lines_done = 0
	while(1):
		next_doc_start, start = min([(indexof(str_, start), start) for start in start_alldoc])
		if(next_doc_start == float("inf")):
			logging.debug("no more docstrings found in line "+ str(lines_done))
			break
		logging.debug("found docstart " + start)
		unused, str_ = str_[:next_doc_start], str_[next_doc_start + len(start):]
		lines_done += unused.count("\n")
		logging.debug("docstart is in " + str(lines_done))
		doc_stop, token = min([(indexof(str_, stop), stop) for stop in stop_alldoc])
		if(doc_stop == float("inf")):
			raise ExtractException("unterminated docstart: " + start + " in line " + str(lines_done))
		doc, str_ = str_[:doc_stop], str_[doc_stop + len(token):]
		logging.debug("found docstop " + token)
		yield doc
		lines_done += doc.count("\n")
		logging.debug("docstop is in " + str(lines_done))

def docs_from_file(path, delim = "\n\n"):
	"""
	Read all docstrings from one file.
	"""
	with open(path) as f:
		logging.debug("reading file " + path)
		str_ = f.read()
		docs = delim.join(extract_docs(str_))
		f.close()
	return docs

def collect_docs(files, delim = "\n\n"):
	"""
	Read all docstrings from multiple files
	"""
	for file_ in files:
		yield docs_from_file(file_, delim)

def generate_rst_head(str_, underscore = "="):
	"""
	Generate a rst Heading.
	"""
	return str_ + "\n" + underscore * len(str_) + "\n"

def generate_docfile(fname, files, delim = "\n\n", add_rst_head = True):
	"""
	Read all docstrings and output one file.

	FIXME: try to spend less memory.
	"""
	f = open(fname, "w")
	f.write("".join(["".join(t) for t in zip([generate_rst_head(file) for file in files] , collect_docs(files))]))
	f.close()
	


class ExtractException(Exception):
	def __init__(self, *args):
		Exception.__init__(self, *args)

if __name__ == "__main__":
	import sys
	if(len(sys.argv) < 3):
		print("Usage:", sys.argv[0], "outfile infile {infile}")
		print("extract docstrings from non-python files")
		print("start tokens: ", start_alldoc)
		print("stop tokens: ", stop_alldoc)
		sys.exit(1)
	outfile = sys.argv[1]
	infiles = sys.argv[2:]
	try:
       		generate_docfile(outfile, infiles)
	except Exception as e:
		print("Error:", e)
		sys.exit(1)
