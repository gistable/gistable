import maya.cmds as mc

# check if there are unsaved changes
fileCheckState = mc.file(q=True, modified=True)

# if there are, save them first ... then we can proceed 
if fileCheckState:
  print 'Need to save.'
  # This is maya's native call to save, with dialogs, etc.
  # No need to write your own.
  mc.SaveScene()
  pass
else:
  print 'No new changes, proceed."
  pass