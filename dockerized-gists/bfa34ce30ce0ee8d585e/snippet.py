import sys
import time
import logging
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ORTHANC_HOST = "http://localhost:8042"
ORTHANC_RESET_URL = ORTHANC_HOST + "/tools/reset"
# Set user/pass if basic authentication is enabled
USER = ""
PASS = ""


class FileReloaderEvent(FileSystemEventHandler):
    """Handler for modified file events that triggers Orthanc to restart."""

    def on_modified(self, event):
        logging.info(event.src_path + " was modified. Restarting Orthanc...")
        if (USER and PASS):
            requests.post(ORTHANC_RESET_URL, auth=(USER, PASS))
        else:
            requests.post(ORTHANC_RESET_URL)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = FileReloaderEvent()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
