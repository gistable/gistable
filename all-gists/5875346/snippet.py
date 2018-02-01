from pyfbsdk import *

def getSelectedOrder():
    # selectionOrder selection order
    # Get the current selection
    lModelList = FBModelList()
    pParent = None
    pSelected = True
    pSortSelectedOrder = True
    FBGetSelectedModels( lModelList, pParent, pSelected, pSortSelectedOrder )    
    
    if not lModelList: return None
    else: return lModelList
    
lSelected = getSelectedOrder()
for i in range(len(lSelected)): print "%d: %s" % ( i, lSelected[i].Name )


##    FBGetSelectedModels(
##    tuple     pList,
##    FBModel 	pParent = None,
##    bool 	pSelected = True,
##    bool 	pSortBySelectOrder = False 
##    )	