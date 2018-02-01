import subprocess
import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    """React to modified .tex files."""
    def on_any_event(self, event):
        """If a file or folder is changed."""
        if event.is_directory:
            return
        if os.path.splitext(event.src_path)[-1].lower() == ".tex":
            subprocess.call("make", shell=True)


def main():
    handler = ChangeHandler()
    observer = Observer()
    observer.schedule(handler, '.')
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
