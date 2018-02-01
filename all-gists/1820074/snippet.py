import pygtk
pygtk.require('2.0')
import gtk
import os

class TextBox:
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_size_request(200,250)
		self.window.connect("destroy", self.close_application)
		self.window.set_title("sticky note")
		self.window.set_border_width(4)
		self.box1 = gtk.EventBox()
		self.box1.connect('leave_notify_event',self.save_text)
		self.window.add(self.box1)
		self.box1.show()
		
		self.textview = gtk.TextView()
		self.textbuffer = self.textview.get_buffer()
		self.textview.set_editable(True)
		self.box1.add(self.textview)
		self.textview.show()
		if os.path.isfile(os.path.join(os.getcwd(),'stickynote.txt')):
		  infile = open('stickynote.txt','r')
	  	if infile:
	  	  string = infile.read()
	  	  infile.close()
	  	  self.textbuffer.set_text(string)
		  
		self.window.show()
        
	def close_application(self, widget):
		file = open('stickynote.txt','w')
		startiter = self.textbuffer.get_start_iter()
		enditer = self.textbuffer.get_end_iter()
		text = self.textbuffer.get_text(startiter, enditer)
		file.write(text)
		file.close()
		gtk.main_quit()
	
	def save_text(self, widget, data=None):
	  file = open('stickynote.txt','w')
	  startiter = self.textbuffer.get_start_iter()
	  enditer = self.textbuffer.get_end_iter()
	  text = self.textbuffer.get_text(startiter, enditer)
	  file.write(text)
	  file.close()
	  return	
def main():
	gtk.main()
	
if __name__ == '__main__':
	TextBox()
	main()