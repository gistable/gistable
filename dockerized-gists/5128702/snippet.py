from flask import Flask, send_file, send_from_directory
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

NBCONVERT_PATH  = '../nbconvert/nbconvert.py'
TARGET_IPYNB = 'presentation.ipynb'
TARGET_HTML = 'presentation_slides.html'

def nbconvert():
	print "Converting ", TARGET_IPYNB, "to a presentation"
	os.system("python " + NBCONVERT_PATH + " -f reveal " + TARGET_IPYNB)

class ChangeHandler(FileSystemEventHandler):
	def on_modified(self, event):
		if event.is_directory:
            		return
            	if event.src_path.endswith(TARGET_IPYNB):
            		nbconvert()

app = Flask(__name__)

@app.route('/reveal/<path:filename>')
def custom_static_reveal(filename):
	return send_from_directory('reveal', filename)

@app.route('/js/<path:filename>')
def custom_static_js(filename):
	return send_from_directory('js', filename)

@app.route("/")
def index():
	return send_file(TARGET_HTML)

if __name__ == "__main__":
	nbconvert()
	observer = Observer()
	event_handler = ChangeHandler()
	observer.schedule(event_handler, path='.')
	observer.start()
	app.run(host='127.0.0.1', port=8000, debug=True)
	observer.stop()
	observer.join()