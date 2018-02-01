#!/usr/bin/python
 
# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
 

class App:
  def __init__(self):
    # Create a Qt application
    self.app = QApplication(sys.argv)
    
    icon = QIcon("jenkins_favicon.png")
    menu = QMenu()
    settingAction = menu.addAction("setting")
    settingAction.triggered.connect(self.setting)
    exitAction = menu.addAction("exit")
    exitAction.triggered.connect(sys.exit)
    
    self.tray = QSystemTrayIcon()
    self.tray.setIcon(icon)
    self.tray.setContextMenu(menu)
    self.tray.show()
    self.tray.setToolTip("unko!")
    self.tray.showMessage("hoge", "moge")
    self.tray.showMessage("fuga", "moge")
    
  def run(self):
    # Enter Qt application main loop
    self.app.exec_()
    sys.exit()

  def setting(self):
    self.dialog = QDialog()
    self.dialog.setWindowTitle("Setting Dialog")
    self.dialog.show()

if __name__ == "__main__":
  app = App()
  app.run()