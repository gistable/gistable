"""

    If you're editing masters or whatever
    and you want to switch to the same glyph in the other master
    and you spend a lot of time moving glyph windows around
    Add this script to RF and wire it to a key command
    and then woosh woosh woosh cycle between the masters.
    
    Possible features, not included
        - some control over the direction, previous / next
        - maintain zoom
        - maintain display settings
    
    erik@letterror.com
    20160618
    v2

"""

from AppKit import *
from mojo.UI import *

def getGlyphWindowPosSize():
    w = CurrentGlyphWindow()
    if w is None:
        return
    x,y, width, height = w.window().getPosSize()
    settings = getGlyphViewDisplaySettings()
    return (x, y), (width, height), settings
    
def setGlyphWindowPosSize(glyph, pos, size, animate=False, settings=None):
    OpenGlyphWindow(glyph=glyph, newWindow=False)
    w = CurrentGlyphWindow()
    w.window().setPosSize((pos[0], pos[1], size[0], size[1]), animate=animate)
    if settings is not None:
        setGlyphViewDisplaySettings(settings)

def getOtherMaster(nextFont=True):
    # determining the order of the available ufos is a bit tricky.
    cf = CurrentFont()
    orderedFonts = []
    allFonts = AllFonts()
    allFonts.sort()
    for i in range(len(allFonts)):
        f = allFonts[i]
        prev = allFonts[i-1]
        nxt = allFonts[(i+1)%len(allFonts)]
        if f == cf:
            if nextFont:
                return nxt
            else:
                return prev

def switch():
    g = CurrentGlyph()
    if g is not None:
        f = CurrentFont()
        n = getOtherMaster()
        nextGlyph = n[g.name]
        if nextGlyph is not None:
            rr = getGlyphWindowPosSize()
            if rr is not None:
                p, s, settings = getGlyphWindowPosSize()
                setGlyphWindowPosSize(nextGlyph, p, s, settings=settings)

switch()
