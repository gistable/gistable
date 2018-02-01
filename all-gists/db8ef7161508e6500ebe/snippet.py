class MainWidget(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(MainWidget, self).__init__(parent)
		self.setWindowTitle("FiFiFactory App")
		self.resize(720,480)
		self.setAcceptDrops(True)

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		files = [unicode(u.toLocalFile()) for u in event.mimeData().urls()]
		for f in files:
			print f