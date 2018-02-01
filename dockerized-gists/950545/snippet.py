from threading import Thread
import random
import time

def random_wait(max_seconds, callback):
  seconds = random.randrange(max_seconds)
  time.sleep(seconds)
  callback(seconds)

class Sketch(object):
  def setup(self):
    size(400, 240)
    self.message = "click to start thread"
    self.thread = None
  def draw(self):
    background(255)
    textAlign(CENTER, CENTER)
    textSize(32)
    if self.thread and self.thread.isAlive():
      fill(frameCount % 240)
      text("waiting...", width/2, height/2)
    else:
      fill(64)
      text(self.message, width/2, height/2)
  def thread_callback(self, seconds):
    self.message = "waited " + str(seconds) + " seconds"
  def mousePressed(self):
    if self.thread and self.thread.isAlive():
      print "thread already running"
      return
    self.thread = Thread(target=random_wait, args=(10, self.thread_callback))
    self.thread.start()

sketch = Sketch()

def setup(): sketch.setup()
def draw(): sketch.draw()
def mousePressed(): sketch.mousePressed()
