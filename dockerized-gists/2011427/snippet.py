#!/usr/bin/env python
#-*- coding:utf-8 -*-

from matplotlib import pyplot
import numpy as np

class ClickPlot:

	"""
	A clickable matplotlib figure
	
	Usage:
	>>> import clickplot
	>>> retval = clickplot.showClickPlot()
	>>> print retval['subPlot']
	>>> print retval['x']
	>>> print retval['y']
	>>> print retval['comment']
	
	See an example below
	"""

	def __init__(self, fig=None):
	
		"""
		Constructor
		
		Arguments:
		fig -- a matplotlib figure
		"""
	
		if fig != None:
			self.fig = fig		
		else:
			self.fig = pyplot.get_current_fig_manager().canvas.figure
		self.nSubPlots = len(self.fig.axes)
		self.dragFrom = None
		self.comment = '0'
		self.markers = []
				
		self.retVal = {'comment' : self.comment, 'x' : None, 'y' : None,
			'subPlot' : None}		

		self.sanityCheck()
		self.supTitle = pyplot.suptitle("comment: %s" % self.comment)
		self.fig.canvas.mpl_connect('button_press_event', self.onClick)
		self.fig.canvas.mpl_connect('button_release_event', self.onRelease)		
		self.fig.canvas.mpl_connect('scroll_event', self.onScroll)
		self.fig.canvas.mpl_connect('key_press_event', self.onKey)
		
	def clearMarker(self):
	
		"""Remove marker from retVal and plot"""
		
		self.retVal['x'] = None
		self.retVal['y'] = None
		self.retVal['subPlot'] = None
		for i in range(self.nSubPlots):
			subPlot = self.selectSubPlot(i)
			for marker in self.markers:
				if marker in subPlot.lines:
					subPlot.lines.remove(marker)				
		self.markers = []
		self.fig.canvas.draw()
		
	def getSubPlotNr(self, event):
	
		"""
		Get the nr of the subplot that has been clicked
		
		Arguments:
		event -- an event
		
		Returns:
		A number or None if no subplot has been clicked
		"""
	
		i = 0
		axisNr = None
		for axis in self.fig.axes:
			if axis == event.inaxes:
				axisNr = i		
				break
			i += 1
		return axisNr
		
	def sanityCheck(self):
	
		"""Prints some warnings if the plot is not correct"""
		
		subPlot = self.selectSubPlot(0)
		minX = subPlot.dataLim.min[0]
		maxX = subPlot.dataLim.max[0]				
		for i in range(self.nSubPlots):
			subPlot = self.selectSubPlot(i)
			_minX = subPlot.dataLim.min[0]
			_maxX = subPlot.dataLim.max[0]
			if abs(_minX-minX) != 0 or (_maxX-maxX) != 0:
				import warnings		
				warnings.warn('Not all subplots have the same X-axis')
		
	def show(self):
	
		"""
		Show the plot
		
		Returns:
		A dictionary with information about the response
		"""
	
		pyplot.show()
		self.retVal['comment'] = self.comment
		return self.retVal
		
	def selectSubPlot(self, i):
	
		"""
		Select a subplot
		
		Arguments:
		i -- the nr of the subplot to select
		
		Returns:
		A subplot
		"""
	
		pyplot.subplot('%d1%d' % (self.nSubPlots, i+1))
		return self.fig.axes[i]

	def onClick(self, event):
	
		"""
		Process a mouse click event. If a mouse is right clicked within a
		subplot, the return value is set to a (subPlotNr, xVal, yVal) tuple and
		the plot is closed. With right-clicking and dragging, the plot can be
		moved.
		
		Arguments:
		event -- a MouseEvent event
		"""		
	
		subPlotNr = self.getSubPlotNr(event)		
		if subPlotNr == None:
			return
		
		if event.button == 1:				
		
			self.clearMarker()
			for i in range(self.nSubPlots):
				subPlot = self.selectSubPlot(i)								
				marker = pyplot.axvline(event.xdata, 0, 1, linestyle='--', \
					linewidth=2, color='gray')
				self.markers.append(marker)

			self.fig.canvas.draw()
			self.retVal['subPlot'] = subPlotNr
			self.retVal['x'] = event.xdata
			self.retVal['y'] = event.ydata
			
		else:			
			# Start a dragFrom
			self.dragFrom = event.xdata
			
	def onKey(self, event):
	
		"""
		Handle a keypress event. The plot is closed without return value on
		enter. Other keys are used to add a comment.
		
		Arguments:
		event -- a KeyEvent
		"""
	
		if event.key == 'enter':
			pyplot.close()
			return
			
		if event.key == 'escape':
			self.clearMarker()
			return
			
		if event.key == 'backspace':
			self.comment = self.comment[:-1]
		elif len(event.key) == 1:			
			self.comment += event.key
		self.supTitle.set_text("comment: %s" % self.comment)
		event.canvas.draw()
			
	def onRelease(self, event):
	
		"""
		Handles a mouse release, which causes a move
		
		Arguments:
		event -- a mouse event
		"""
	
		if self.dragFrom == None or event.button != 3:
			return			
		dragTo = event.xdata
		dx = self.dragFrom - dragTo
		for i in range(self.nSubPlots):
			subPlot = self.selectSubPlot(i)			
			xmin, xmax = subPlot.get_xlim()
			xmin += dx
			xmax += dx				
			subPlot.set_xlim(xmin, xmax)
		event.canvas.draw()
											
	def onScroll(self, event):
	
		"""
		Process scroll events. All subplots are scrolled simultaneously
		
		Arguments:
		event -- a MouseEvent
		"""
	
		for i in range(self.nSubPlots):
			subPlot = self.selectSubPlot(i)		
			xmin, xmax = subPlot.get_xlim()
			dx = xmax - xmin
			cx = (xmax+xmin)/2
			if event.button == 'down':
				dx *= 1.1
			else:
				dx /= 1.1
			_xmin = cx - dx/2
			_xmax = cx + dx/2	
			subPlot.set_xlim(_xmin, _xmax)
		event.canvas.draw()
		
def showClickPlot(fig=None):

	"""
	Show a pyplot and return a dictionary with information
	
	Returns:
	A dictionary with the following keys:
	'subPlot' : the subplot or None if no marker has been set
	'x' : the X coordinate of the marker (or None)
	'y' : the Y coordinate of the marker (or None)
	'comment' : a comment string	
	"""

	cp = ClickPlot(fig)
	return cp.show()
	
if __name__ == '__main__':
	
	xData = np.linspace(0, 4*np.pi, 100)
	yData1 = np.cos(xData)
	yData2 = np.sin(xData)
	fig = pyplot.figure()
	subPlot1 = fig.add_subplot('211')
	pyplot.plot(xData, yData1, figure=fig)
	subPlot2 = fig.add_subplot('212')
	pyplot.plot(xData, yData2, figure=fig)
	
	# Show the clickplot and print the return values
	retval = showClickPlot()		
	print 'Comment = %s' % retval['comment']
	if retval['subPlot'] == None:
		print 'No subplot selected'
	else:
		print 'You clicked in subplot %(subPlot)d at (%(x).3f, %(y).3f)' \
			% retval
