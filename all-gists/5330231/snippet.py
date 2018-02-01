'''
Copyright 2013 Lloyd Konneker

License: LGPL
'''
from PySide.QtCore import QSettings


class WindowSettable(object):
  '''
  Mixin behavior for MainWindow: window attributes persist as Settings
  
  See Qt Application Example, where these are called readSettings() and writeSettings().
  
  Assert that QSettings have been established on app startup:
  QCoreApplication.setOrganizationName("Foo")
  QCoreApplication.setOrganizationDomain("foo.com")
  QCoreApplication.setApplicationName("Bar")
  '''
  
  
  def _readAndApplyWindowAttributeSettings(self):
    '''
    Read window attributes from settings,
    using current attributes as defaults (if settings not exist.)
    
    Called at QMainWindow initialization, before show().
    '''
    qsettings = QSettings()

    qsettings.beginGroup( "mainWindow" )

    # No need for toPoint, etc. : PySide converts types
    self.restoreGeometry(qsettings.value( "geometry", self.saveGeometry())) 
    self.restoreState(qsettings.value( "saveState", self.saveState()))
    self.move(qsettings.value( "pos", self.pos()))
    self.resize(qsettings.value( "size", self.size()))
    if qsettings.value( "maximized", self.isMaximized()) :
        self.showMaximized()

    qsettings.endGroup()
  
  

  def _writeWindowAttributeSettings(self):
    '''
    Save window attributes as settings.
    
    Called when window moved, resized, or closed.
    '''
    qsettings = QSettings()

    qsettings.beginGroup( "mainWindow" )
    qsettings.setValue( "geometry", self.saveGeometry() )
    qsettings.setValue( "saveState", self.saveState() )
    qsettings.setValue( "maximized", self.isMaximized() )
    if not self.isMaximized() == True :
        qsettings.setValue( "pos", self.pos() )
        qsettings.setValue( "size", self.size() )
    qsettings.endGroup()