"""\
Pluzz Downloader

Downloads a movie from the French Television VOD

Usage:
  pluzz_downloader.py [<url>] [--gui] [-t <target>] [--avconv <avconv>]

Options:
  -g --gui               Launch graphical user interface
  -t --target <target>   Target directory to download the file to [default: ~/Downloads]
  --avconv <avconv>      Sets full path to avconv binary [default: /usr/bin/avconv]
  -h --help              Show this screen.
  --version              Show version.

(c)2014 Bernard `Guyzmo` Pratz
Under the WTFPL <http://wtfpl.net>
"""

import io
import os
import re
import sys
import json
import time
import types
import select
import requests
import subprocess
from lxml import etree

class PluzzMovie():
    data_url = "http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={show}&catalogue=Pluzz&callback=webserviceCallback_{show}"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:19.0) Gecko/20100101 Firefox/19.0'}
    avconv_args = ['-y', '-vcodec', 'copy', '-acodec', 'copy']

    def __init__(self, url):
        self.url = url
        self.show_id = None
        self.data = {}

    def retrieve_data(self):
        p = etree.HTML(requests.get(self.url, headers=self.headers).text)
        self.show_id = p.xpath('//meta[@property="og:url"]/@content')[0].split(',')[-1].split('.')[0]
        self.data = json.loads("".join(requests.get(self.data_url.format(show=self.show_id), headers=self.headers).text.split('(')[1:])[:-1])

    def save(self, target_path="~/Downloads", callback=lambda p, t, d, s: print(p, t, d, s), avconv_path='/usr/bin/avconv'):
        if not os.path.isdir(target_path):
            raise Exception("Can't download and convert: target directory '{}' does not exists".format(target_path))
        def output_parser(output, env={}):
            duration_m = duration_r.match(output)
            if duration_m:
                h,m,s = duration_m.groups()
                env['duration'] = int(h)*3600 + int(m)*60 + float(s)
                env['start'] = time.time()
            elif 'duration' in env.keys():
                processd_m = processd_r.match(output)
                if processd_m:
                    pos = float(processd_m.groups()[0])
                    spt = int(time.time()-env['start'])
                    callback(pos, env['duration'], spt, env['start'])
                else:
                    overwrite_m = overwrite_r.match(output)
                    if overwrite_m:
                        path = overwrite_m.groups()[0]
                        raise Exception('Output file "{}" already exists in target directory.'.format(path))

        p = requests.get(list(filter(lambda x: x['format'] == 'm3u8-download', self.data['videos']))[0]['url'], headers=self.headers).text
        video_url = list(filter(lambda l: "index_2" in l, p.split()))[0]
        dest_file = "{}_{}.mkv".format(self.data['code_programme'], self.show_id)
        self.dest_file = os.path.join(os.path.expanduser(target_path), dest_file)
        p = subprocess.Popen([avconv_path, '-i', video_url] + self.avconv_args + [self.dest_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = io.TextIOWrapper(p.stdout)
        err = io.TextIOWrapper(p.stderr)
        while p.poll() == None:
            ret = select.select([out.fileno(), err.fileno()], [], [])
            for fd in ret[0]:
                if fd == out.fileno():
                    output_parser(out.readline())
                if fd == err.fileno():
                    output_parser(err.readline())
        for line in out.read().split('\n'):
            output_parser(line)
        for line in err.read().split('\n'):
            output_parser(line)

    def __getitem__(self, it):
        return self.data[it]

    def __setitem__(self, it, val):
        raise Exception("Movie data are immutables")


# Duration: 00:44:47.95, start: 0.100667, bitrate: 0 kb/s\n
duration_r = re.compile(r'.*Duration: (\d\d):(\d\d):(\d\d.\d\d), .*')
# frame=59282 fps=939 q=-1.0 size=  244134kB time=2371.24 bitrate= 843.4kbits/s
processd_r = re.compile(r'.* time=(\d+.\d\d) .*')
# already exists. Overwrite ? [y/N]
overwrite_r = re.compile(r".*File '([^']+)' already exists.*")

def get_term_size():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])

def show_progress(position, total, spent, start):
    width = (get_term_size()[0]*0.6)
    adv = position/total
    eta = int((time.time() - start)*total/position)
    print(('Download and convert: [{: <'+str(int(width))+'s}] {:0.0%} ETA: {}s/{}s').format('#'*int(width*adv), adv, spent, eta), end='\r')


gui=True
try:
    try:
        from PyQt5 import QtCore
        from PyQt5 import QtWidgets
    except ImportError:
        from PyQtX import QtCore
        from PyQtX import QtWidgets

    class QPluzz(QtWidgets.QWidget):

        update_progress_bar = QtCore.pyqtSignal(int)
        update_eta_text = QtCore.pyqtSignal(str)

        def __init__(self, args):
            super(QPluzz, self).__init__()

            self.defaults = args

            # row #0
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel('Pluzz Movie Downloader'))
            # row #1
            hbox = QtWidgets.QHBoxLayout()
            hbox.addStretch(1)
            hbox.addWidget(QtWidgets.QLabel('URL of movie to load'))
            self.url_txt = QtWidgets.QLineEdit()
            self.url_txt.setText(args['<url>'])
            hbox.addWidget(self.url_txt)
            vbox.addLayout(hbox)
            # row #2
            hbox = QtWidgets.QHBoxLayout()
            hbox.addStretch(1)
            hbox.addWidget(QtWidgets.QLabel('Directory where to download'))
            self.path_txt = QtWidgets.QLineEdit()
            self.path_txt.setText(args['--target'])
            hbox.addWidget(self.path_txt)
            vbox.addLayout(hbox)
            # row #3
            hbox = QtWidgets.QHBoxLayout()
            self.eta = QtWidgets.QLabel('ETA -/-')
            self.update_eta_text.connect(self.eta.setText)
            hbox.addWidget(self.eta)
            self.pbar = QtWidgets.QProgressBar()
            self.pbar.setMinimum(0)
            self.pbar.setMaximum(100)
            self.pbar.setTextVisible(True)
            self.update_progress_bar.connect(self.pbar.setValue)
            hbox.addWidget(self.pbar, stretch=1)
            vbox.addLayout(hbox)
            # row #4
            self.start_btn = QtWidgets.QPushButton('Start Download!')
            self.start_btn.clicked.connect(self.on_click_start)
            vbox.addWidget(self.start_btn)
            vbox.addStretch(1)

            self.setLayout(vbox)

            self.setWindowTitle('Pluzz Movie loader')
            self.show()

        @QtCore.pyqtSlot()
        def on_click_start(self):
            def update_progress(position, total, spent, start):
                eta = int((time.time() - start)*total/position)
                adv = position/total
                # print("{: >10}/{: <10} : {: >3}s/{: <3}s".format(position, total, spent, eta), end='\r')
                self.update_eta_text.emit("ETA {}s/{}s".format(spent, eta))
                self.update_progress_bar.emit(adv*100)

            def dl(that):
                self.start_btn.setDisabled(True)
                movie.save(callback=update_progress, avconv_path=self.defaults['--avconv'])
                self.update_eta_text.emit("ETA -/-")
                self.update_progress_bar.emit(0)
                self.start_btn.setEnabled(True)

            movie = PluzzMovie(self.url_txt.text())
            movie.retrieve_data()
            t = QtCore.QThread(self)
            # Monkey patching of QThread to change the run function!
            t.run = types.MethodType(dl, t)
            t.start()

except ImportError:
    gui=False

def main():
    from docopt import docopt
    try:
        args = docopt(__doc__)
        if args['--gui']:
            if not gui:
                raise Exception("Couldn't load Qt libraries")
            app = QtWidgets.QApplication(sys.argv)
            qpluzz = QPluzz(args)
            sys.exit(app.exec_())
        else:
            if not args['<url>']:
                raise Exception('Missing URL!')
            print("Init…", end="\r", file=sys.stderr)
            m = PluzzMovie(args['<url>'])
            print("Get data…", end="\r", file=sys.stderr)
            m.retrieve_data()
            print("Download and convert…", end='\r', file=sys.stderr)
            m.save(args['--target'], callback=show_progress, avconv_path=args['--avconv'])
            print(("{: <"+str(int(get_term_size()[0]))+"}").format("Download and convertion done: '{}' saved".format(m.dest_file)))
    except Exception as err:
        print("", file=sys.stderr)
        print("Error:", err, file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
