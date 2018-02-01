import c4d
from c4d import gui, documents

def main():
    # BaseDraw
    bd = doc.GetActiveBaseDraw()
  
    # The camera view
    view = bd.GetSafeFrame()

    # Check if poly object
    if op is None:
        gui.MessageDialog('Please select an objcet')
        return
    if op.GetType() != c4d.Opolygon:
        gui.MessageDialog('Objcet needs to be of type polygon')
        return

    # Get all points in object
    bs = op.GetPointS()

    for pt in xrange(op.GetPointCount()):
      
        # Get global position of point 'pt'
        pointGlobal = op.GetMg() * op.GetPoint(pt)
      
        # Split pointGlobal
        pointX = bd.WS(pointGlobal)[0]
        pointY = bd.WS(pointGlobal)[1]
      
        # Check if point is inside SafeFrame 'view'
        if pointX > 0 and pointX < view['cr']:
            if pointY > view['ct'] and pointY < view['cb']:
                bs.Select(pt)

    c4d.EventAdd()
    
if __name__=='__main__':
    main()