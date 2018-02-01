def resizeNav():
	"""
		This can be used if you'd like to be able to 
		grow and shrink a left side nav bar
	"""
	from java.awt import Dimension
	windows= system.gui.getOpenedWindows()
	nav = system.gui.getWindow('Navigation')	
	root = nav.getRootContainer()
	d = nav.getSize()
	"""		
		navcontainer is not visible
		width is 60px
	"""
	width = 0 if d.width == 200 else  200	
	nav.resize(width, d.height)
	for window in windows:
		if window.name not in ['Navigation']:
			d = window.getSize()
			window.setLocation(width,(0 if window.name == 'Header' else 40))
			window.setSize(d.width + (200 if width==0 else -200), d.height)