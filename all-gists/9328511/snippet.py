
g = CurrentGlyph()

f = CurrentFont()

for g in f:

    box = g.box
    
    if box is None:
        continue
    offset = 10

    minx, miny, maxx, maxy = box
    minx -= offset
    miny -= offset
    maxx += offset
    maxy += offset



    w = maxx - minx
    h = maxy - miny

    cut1 = RGlyph()

    pen = cut1.getPen()

    pen.moveTo((minx, miny))
    pen.lineTo((minx+w, miny))
    pen.lineTo((minx+w, miny+h/2))
    pen.lineTo((minx, miny+h/2))
    pen.closePath()

    cut2 = RGlyph()
    pen = cut2.getPen()

    pen.moveTo((minx, miny+h/2))
    pen.lineTo((minx+w, miny+h/2))
    pen.lineTo((minx+w, miny+h))
    pen.lineTo((minx, miny+h))
    pen.closePath()


    r1 = g % cut1
    r2 = g % cut2

    g.clearContours()


    g.appendGlyph(r1, (0, -h/2 + offset*2))
    g.appendGlyph(r2, (0, h/2 - offset*2))



