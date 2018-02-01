import c4d
from c4d import gui

def main():
    doc = c4d.documents.GetActiveDocument()
    op = doc.GetActiveObject()

    if op is None or op.GetType() != c4d.Opolygon: return

    bs = op.GetPointS()
    print bs
    if bs.GetCount() != 1:
      print "None"
      start_point = 0
    else:
      start_point = None

    for pt in xrange(op.GetPointCount()):
      if start_point is None and bs.IsSelected(pt):
        start_point = pt
      if start_point is not None:
        if (pt - start_point) % 2 == 0:
          bs.Select(pt)
        else:
          if bs.IsSelected(pt):
            bs.Toggle(pt)

    c4d.EventAdd()

if __name__=='__main__':
    main()
