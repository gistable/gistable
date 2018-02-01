# Run:
# $ virtualenv env
# $ cd env 
# $ env/bin/pip install watchdog
# $ env/bin/pip install selenium
# $ env/bin/python sphinx-reload.py

import logging
import os
import selenium.webdriver
import subprocess
import time

from urllib import pathname2url
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

#XXX in Windows set bat command
MAKE_COMMAND = 'make html'.split()

class SphinxEventHandler(PatternMatchingEventHandler):
    """Rebuild and refresh on every change event."""

    def __init__(self, patterns=None, ignore_patterns=None, 
            ignore_directories=False, case_sensitive=False):
        super(SphinxEventHandler, self).__init__(patterns, ignore_patterns,
                ignore_directories, case_sensitive)
        path = os.path.join('_build', 'html', 'index.html')
        url = 'file:///' + pathname2url(os.path.abspath(path))
        self.driver = selenium.webdriver.Firefox()
        self.driver.get(url)

    def cleanup(self):
        self.driver.quit()

    def _run(self):
        subprocess.call(MAKE_COMMAND)
        self.driver.refresh()
        logging.info("Rebuild and refreshed")

    def on_moved(self, event):
        super(SphinxEventHandler, self).on_moved(event)
        self._run()

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(SphinxEventHandler, self).on_created(event)
        self._run()

        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(SphinxEventHandler, self).on_deleted(event)
        self._run()

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(SphinxEventHandler, self).on_modified(event)
        self._run()

        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)


if __name__ == "__main__":
    if not os.path.isdir(os.path.abspath('_build')):
        # very simplistic sanity check. Works for me, as I generally use
        # sphinx-quickstart defaults
        print('You must run this application from a Sphinx directory containing _build')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        event_handler = SphinxEventHandler(patterns=['*.rst'], 
                ignore_patterns=['*.html'], ignore_directories=["_build"])
        observer = Observer()
        observer.schedule(event_handler, path=os.path.abspath("."), 
                recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        event_handler.cleanup()
        observer.join()