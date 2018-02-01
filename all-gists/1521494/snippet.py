#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A simple tool for converting batches of PNG pages into a PDF file.

Usage:
1. Drop into the folder with the PNGs.
2. chmod +x png2pdf.py
3. Double-click it.

Requires:
- PyPDF 1.13+
- ImageMagick (in the PATH)
"""

__appname__ = "png2pdf"
__author__  = "Stephan Sokolow (deitarion/SSokolow)"
__version__ = "0.3"
__license__ = "GNU GPL 3.0 or later"

import logging
log = logging.getLogger(__name__)

import os, pyPdf, subprocess, sys

class Empty(object):
    pass

job = Empty()
job.terminal = Empty()
job.terminal.feed = sys.stderr.write
job.feed_status = lambda x: job.terminal.feed('\r\n%s\r\n' % x)

def magick_pngs_to_pdfs(job, data):
    # TODO: Decide how to handle removing PDFs for which the PNGs have been
    # deleted.

    dirn = os.path.split(data[0])[0]
    outdir = os.path.join(dirn, '_build')

    #TODO: What if it's not a dir?
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    outpaths = []
    for path in data:
        outname = os.path.splitext(os.path.split(path)[1])[0] + '.pdf'
        outpath = os.path.join(outdir, outname)

        in_stat = os.stat(path)
        try:
            out_stat = os.stat(outpath)
        except OSError:
            out_stat = None

        if not (out_stat and in_stat.st_mtime == out_stat.st_mtime):
            subprocess.check_call(['convert', '-monitor', path, outpath])
            os.utime(outpath, (getattr(out_stat, 'st_atime', in_stat.st_atime), in_stat.st_mtime))
        else:
            log.info("Generated PDF already up to date: %s", outpath)

        outpaths.append(outpath)

    return outpaths

def reduce_pdfs_to_pdf(job, data, outpath):
    """Bundle many PDFs into one without altering page dimensions.

    Resources in case this approach fails:
    - https://www.linux.com/news/software/applications/8229-putting-together-pdf-files
    - http://milan.kupcevic.net/ghostscript-ps-pdf/
    - http://www.ghostscript.com/doc/current/Devices.htm
    """
    dimensions, failed = None, []
    pieces, pdf_out, handles = len(data), pyPdf.PdfFileWriter(), []

    try:
        for idx, path in enumerate(data):
            #TODO: Probably a good idea to have another wrapper for status
            #      outputs which self-overwrite using \r
            job.feed_status("Queueing operations for final PDF: Piece %d of %d" % (idx, pieces))
            file_in = file(path, 'rb')
            handles.append(file_in)

            pdf_in = pyPdf.PdfFileReader(file_in)
            for pidx, page in enumerate(pdf_in.pages):
                try:
                    if dimensions:
                        assert page.mediaBox == dimensions
                    else:
                        dimensions = page.mediaBox

                    #TODO: Need to make the task progress bar definite.
                    pdf_out.addPage(page)
                except AssertionError:
                    failed.append((pidx, path))

        if failed:
            raise AssertionError("Page sizes don't match first page:\n\t%s" %
                    '\n\t'.join(['page %d of file %s' % x for x in failed]))

        with file(outpath, 'wb') as file_out:
            job.terminal.feed("\r\nBuilding %s (%d pages from %d source files)\r\n" %
                    (outpath, pdf_out.getNumPages(), pieces))
            pdf_out.write(file_out)
    finally:
        for fh in handles:
            fh.close()

def bundle_pngs(args, outpath):
    pdf_args = magick_pngs_to_pdfs(job, args)
    reduce_pdfs_to_pdf(job, pdf_args, outpath)
    return outpath

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(version="%%prog v%s" % __version__,
            usage="%prog [options] <argument> ...",
            description=__doc__.replace('\r\n','\n').split('\n--snip--\n')[0])
    parser.add_option('-v', '--verbose', action="count", dest="verbose",
        default=3, help="Increase the verbosity.")
    parser.add_option('-q', '--quiet', action="count", dest="quiet",
        default=0, help="Decrease the verbosity. Can be used thrice for extra effect.")
    parser.add_option('--go', action="store_true", dest="go",
        default=False, help="Used for two-stage startup with no arguments")

    opts, args  = parser.parse_args()

    # Set up clean logging to stderr
    log_levels = [logging.CRITICAL, logging.ERROR, logging.WARNING,
                  logging.INFO, logging.DEBUG]
    opts.verbose = min(opts.verbose - opts.quiet, len(log_levels) - 1)
    opts.verbose = max(opts.verbose, 0)
    logging.basicConfig(level=log_levels[opts.verbose],
                        format='%(levelname)s: %(message)s')

    if not args:
        if not opts.go:
            os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
            os.execlp('xterm', 'xterm', '-hold', '-e', sys.argv[0], '--go')
        log.info("No files specified. Using all PNGs in the current directory")
        args = [x for x in os.listdir('.') if x.lower().endswith('.png')]
        args.sort()
        #TODO: Use a more natural sorting algorithm.

    if args:
        #TODO: Add a -d/--directories option so I can easily batch-convert multiple books.
        bundle_pngs(args, 'book.pdf')
        print "Done."
    else:
        print "No files found."
