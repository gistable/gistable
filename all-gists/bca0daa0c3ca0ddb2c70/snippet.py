"""
Example command for removing zero rotations from a locator item.
Clears the zero rotation offset while maintaining the pose. Acts on all selected locator items.

Limitation: Only works if the rotation item's location is subsequent to the zero rotation item
            (As by default when using the skeleton tool)
            
            Existing animation curves are removed
            
Simplified example, no argument handling or command helps/configs added.
"""

import lx
import lxifc
import lxu.command
import modo

class CmdClearZeroRotation(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)                        

        # Adding an optional argument 'clear'. 
        # If True, the zero rotation is cleared,
        # if False, the rotation is cleared instead.

        self.dyna_Add('clear', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(0, lx.symbol.fCMDARG_OPTIONAL)  

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO 

    def basic_Execute(self, msg, flags):

	# Get the value of our 'clear' argument, defaulting to 1 if it was not passed
	doClear = self.dyna_Int(0, 1)
	
	# Get the current scene
	scn = modo.Scene()
	
	# Iterate all selected items that have locator as super type
	for loc in scn.selectedByType(modo.c.LOCATOR_TYPE, superType=True):
	
		# Create list of rotation items
		# We assume the rotation item's index is the one following the the zero's index
		rotationItems = [t for t in loc.transforms if t.type=='rotation']
		
		# Find the zero rotation item
		zeroItem = next((t for t in rotationItems if 'Rotation Zero' in t.name), None)
		
		if zeroItem:
			index = rotationItems.index(zeroItem)
			
			# Find the next transform item and verify that it is a rotation
			if len(rotationItems) >= index:
				rotation = rotationItems[index+1]			
				if not rotation.type == 'rotation':
					continue

				matZero = modo.Matrix4( zeroItem.channel('matrix').get() )
				matRot  = modo.Matrix4( rotation.channel('matrix').get() )	

				if doClear:
					
					# Multiply the matrices to get a single rotation
					matResult = matRot * matZero
					
					# Clear the zero item's rotation and set the rotation item values
					zeroItem.set( (0,0,0) )
					rotation.set( matResult.asEuler() )

				else:
					# Multiply the matrices to get a single rotation
					matResult = matRot * matZero
					
					# Clear the rotation and apply the values to the zero rotation
					rotation.set( (0,0,0) )
					zeroItem.set( matResult.asEuler() )
					
lx.bless(CmdClearZeroRotation, "test.clearZero")