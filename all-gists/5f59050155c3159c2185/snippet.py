# Check if Maya is running in Batch mode or with a GUI
# A return value of 1 means Batch Mode, 0 means GUI mode
def checkMayaGuiBatchMode():  
  """
  Maya tip on detecting Maya Batch mode is from Michael Scarpa's blog post "MEL Sillyness":
  http://www.scarpa.name/2010/12/16/mel-sillyness/
  """

  # Check if Maya is running in batch mode or with a GUI
  import maya.OpenMaya
  isMayaInBatchMode = maya.OpenMaya.MGlobal.mayaState() == maya.OpenMaya.MGlobal.kBatch

  return isMayaInBatchMode;
  

# Check if Maya is running in Batch mode or with a GUI
# 1 means Batch Mode, 0 means GUI mode
isMayaInBatchMode = checkMayaGuiBatchMode()