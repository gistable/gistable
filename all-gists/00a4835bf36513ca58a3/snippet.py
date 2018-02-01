import c4d
# Slightly modified version of Lennart's (tca studios) script from this thread: 
# http://www.plugincafe.com/forum/forum_posts.asp?TID=6600&KW=&PID=27379#27379

def main():

    if op is None: return False

    oldm   = op.GetMg()
    points = op.GetAllPoints()
    pcount = op.GetPointCount()

    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, op)

    op.SetAbsPos(c4d.Vector(0,0,0)) #Comment out this to keep original position
    op.SetAbsRot(c4d.Vector(0,0,0)) #Comment out this to keep original rotation
    op.SetAbsScale(c4d.Vector(1,1,1)) #Comment out this to keep original scale
    op.Message(c4d.MSG_UPDATE)

    newm    = op.GetMg()

    for p in xrange(pcount):
        op.SetPoint(p,~newm*oldm*points[p])

    op.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()
    doc.EndUndo()

if __name__=='__main__':
    main()