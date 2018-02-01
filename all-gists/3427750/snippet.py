from PyQt4 import QtCore, QtGui

class Window(QtGui.QDialog):

	def __init__(self):
		super(Window, self).__init__()
		self.resize(200,100)

		self._new_slider_min = .1
		self._new_slider_max = .9

		layout = QtGui.QVBoxLayout(self)
		self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, None)
		self.slider.setRange(0,100)
		self.slider.valueChanged.connect(self.handleSlider)
		layout.addWidget(self.slider)

	def handleSlider(self, val):
		newVal = fit(
			val, 
			self.slider.minimum(), self.slider.maximum(), 
			self._new_slider_min, self._new_slider_max
		)

		print "Slider: %0.2f => %0.2f" % (val, newVal)


def fit(v, oldmin, oldmax, newmin=0.0, newmax=1.0):
	"""
	Just a standard math fit/remap function 

		number v 		- initial value from old range 
		number oldmin 	- old range min value 
		number oldmax 	- old range max value 
		number newmin 	- new range min value 
		number newmax 	- new range max value  

	Example:

		fit(50, 0, 100, 0.0, 1.0)
		# 0.5

	"""
	scale = (float(v) - oldmin) / (oldmax - oldmin) 
	new_range = scale * (newmax - newmin)
	if newmin < newmax: 
		return newmin + new_range
	else: 
		return newmin - new_range	



if __name__ == "__main__":
	app = QtGui.QApplication([])
	win = Window()
	win.show()
	win.raise_()
	app.exec_()

