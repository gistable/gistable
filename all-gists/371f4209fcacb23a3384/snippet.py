'''
PySide Session 2 - Notes
'''
'''
Packages
'''



# Window flags
# http://srinikom.github.io/pyside-docs/PySide/QtCore/Qt.html

'''
Paths
'''
# Starting out by breaking up the scripts path.
base_path = os.path.split(__file__)[0]
# Pieces together the full icon path.
print base_path
full_path = os.path.join(base_path, icon_folder, icon_name)

# Creating a tool to get the image paths.
def get_icon_path(icon_name, icon_folder='icons'):
	'''
	The point of this function is ot return the location of 
		a icon in an adjacent folder next to the script.

	Make sure ot import this script into the scirpt you want to use it.
	Then you can use the path_tools.get_icon_path('icon.png') anywhere you 
		need to implant an image path.

	How to Run:

	import path_tools

	# Use the path 
	pm.symbolButton(image=path_tools.get_icon_path('icon.png'))
	'''

	# os.path.split breaks up a file path.
	base_path = os.path.split(__file__)[0]
	# Pieces together the full icon path.
	print base_path
	full_path = os.path.join(base_path, icon_folder, icon_name)

	return full_path 

'''
Windows always on top!

This window will not always be on top!  
I am looking for a less agressive flag. 
'''
# Connecting this window to Maya's main window.
self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

'''
Adding an image inside of designer.
'''

# Understanding how pyside locates images.
# This code is from the compiled designer file.
# It looks good.  Why is the image not appearing?
# It because relative images in pyside relate to from where the files is loaded.
# This is not where the script is located.
self.label.setPixmap(QtGui.QPixmap("icons/rabbit_face.png"))


# We have two options here.  Compile the images into a resource file (rcc) or 
# 	define the paths ourselves.  We are going to go with the second option here.

# Overwriting the paths in our main script.
background_image = get_icon_path('rabbit_face.png')
green_icon = get_icon_path('green_light.png')

# Background image.
self.label.setPixmap(QPixmap(background_image))

# Selection Buttons
icon = QIcon()
icon.addPixmap(QPixmap(green_icon), QIcon.Normal, QIcon.Off)
self.rt_lip2_btn.setIcon(icon)


'''
Autodesks Widget Integraion
http://knowledge.autodesk.com/search-result/caas/CloudHelp/cloudhelp/2015/ENU/Maya-SDK/files/GUID-66ADA1FF-3E0F-469C-84C7-74CEB36D42EC-htm.html

'''




'''
Maya Object inside of Pyside. 

Currently there will be too much to get this working.  I did find some examples though.
http://callanw.com/2014/07/custom-timeline-control-pyside-maya-2014/

Test files are timelineCtrl.zip


Older pyqt version
http://justinfx.com/2011/11/20/mixing-pyqt4-widgets-and-maya-ui-objects/
Sip could most likely be replaced with code above.
'''


'''
Loading direction from the ui file.
'''
from maya import OpenMayaUI as omui
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *
from shiboken import wrapInstance

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

loader = QUiLoader()
file = QFile("/Users/mclavan/Library/Preferences/Autodesk/maya/scripts/rig_interface/characterSelect_gui.ui")

file.open(QFile.ReadOnly)
ui = loader.load(file, parentWidget=mayaMainWindow)
file.close()

background_image = '/Users/mclavan/Library/Preferences/Autodesk/maya/scripts/rig_interface/icons/rabbit_face.png'
ui.label.setPixmap(QPixmap(background_image))

ui.setWindowFlags( Qt.Window )
ui.show()