#!/usr/bin/env python

"""
If you use landslide to create slideshows using markdown, you may have found
yourself repeating endlessly:
+ save source document
+ switch to the terminal to run landslide
+ reload the generated html in your browser

This QT (using webkit) based "application" monitor changes to the source file
and automatically regenerates the HTML and refreshes the "browser".

$ ./qtkit.py --help
usage: qtkit.py [-h] --landslide LANDSLIDE [--port PORT] [--html HTML] file

landslide text to html viewer

positional arguments:
  file                  text file (md or rst)

optional arguments:
  -h, --help            show this help message and exit
  --landslide LANDSLIDE
                        path to the landslide binary
  --port PORT           simple http server port (default 8000)
  --html HTML           html filename (default presentation.html)

To quit close the QT window or press ctrl + c in the terminal.
"""

import sys
import os
import signal
import subprocess
import SimpleHTTPServer
import SocketServer
from multiprocessing import Process
import argparse

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *


class FullHelpArgumentParser(argparse.ArgumentParser):
    """ argument parser displaying the complete help on error """

    # http://stackoverflow.com/a/4042861/753565
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def parse_arguments():
    """ argparse wrapper """

    parser = FullHelpArgumentParser(description='landslide text to html viewer')
    parser.add_argument('file', help='text file (md or rst)', action='store')
    parser.add_argument('--landslide', help='path to the landslide binary',
                        action='store', required=True)
    parser.add_argument('--port', type=int, help='simple http server port (default 8000)',
                        default=8000, action='store')
    parser.add_argument('--html', help='html filename (default presentation.html)',
                        default='presentation.html', action='store')
    return parser.parse_args()

def http_server(path, port):
    """ start a simple http server listening on port serving files from path """

    os.chdir(path)
    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    # http://stackoverflow.com/questions/337115/setting-time-wait-tcp
    SocketServer.TCPServer.allow_reuse_address = True
    http = SocketServer.TCPServer(('', port), handler)
    # handling a ctrl-c termination
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        pass

def landslide(args):
    """ run args.landslide on args.file to create args.html """

    html_file = os.path.join(os.path.dirname(args.file), args.html)
    subprocess.call([args.landslide, '--embed', args.file, '-d', html_file])

def start_fs_watcher(web, args):
    """ create a watcher on args.file, calling landslide and reloading web """

    # http://stackoverflow.com/a/5339877/753565
    @pyqtSlot(str)
    def file_changed(path):
        landslide(args)
        web.reload()

    fs_watcher = QFileSystemWatcher([args.file])
    fs_watcher.connect(fs_watcher, SIGNAL('fileChanged(QString)'), file_changed)
    return fs_watcher


def main():
    args = parse_arguments()

    # using multiprocessing to start the http server in its own process
    http = Process(target=http_server, args=(os.path.dirname(args.file), args.port))
    http.start()

    app = QApplication([])
    web = QWebView()

    fs_watcher = start_fs_watcher(web, args)

    # compare html and text file last modified dates to only process if necessary
    mtime_text_file = os.path.getmtime(args.file)
    try:
        mtime_html_file = os.path.getmtime(os.path.join(os.path.dirname(args.file), args.html))
    except OSError:
        mtime_html_file = 0
    if mtime_text_file > mtime_html_file:
        landslide(args)
    web.load(QUrl('http://localhost:%i/%s' % (args.port, args.html)))
    web.show()

    # exiting from the command line (ctrl+c)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # starting the QT event loop
    app.exec_()

    # del fs_watcher in a cleanup slot connected to the aboutToQuit signal doesn't work
    del fs_watcher
    http.terminate()

if __name__ == '__main__':
    main()