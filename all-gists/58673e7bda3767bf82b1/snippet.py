#MenuTitle: Compare Fonts
# -*- coding: utf-8 -*-
__doc__="""
- Compare 2 open files and opens a new tab (in the current font) for each master showing the glyphs that are different between the 2 files.

- A decomposed copy of each different glyph from the other file will also be pasted in the background of each glyph in the current file. 

*** WARNING *** This will clear the background in the current font. Uncomment the "doNotCopyToBackground" line to disable it.

"""

import GlyphsApp
from objectsGS import RFont
from robofab.pens.digestPen import DigestPointPen

doNotCopyToBackground = 0

# Uncomment the following line to disable the script from copying over the background.
# doNotCopyToBackground = 1

def copyPathsAndAnchorsFromLayerToLayer( sourceLayer, targetLayer ):
    # Copy Paths
    numberOfPathsInSource  = len( sourceLayer.paths )

    if numberOfPathsInSource > 0:
        for thisPath in sourceLayer.paths:
            newPath = thisPath.copy()
            targetLayer.paths.append( newPath )

    # Copy Anchors
    numberOfAnchorsInSource = len( sourceLayer.anchors )

    if numberOfAnchorsInSource > 0:
        for thisAnchor in sourceLayer.anchors:
            newAnchor = thisAnchor.copy()
            targetLayer.anchors.append( newAnchor )
            # print "   %s (%i, %i)" % ( thisAnchor.name, thisAnchor.position.x, thisAnchor.position.y )

for thisMasterIndex in range( len(Glyphs.fonts[0].masters) ):

    # fonts = AllFonts()
    # f1 = RFont(Glyphs.fonts[0])
    # f2 = RFont(Glyphs.fonts[1])

    f1 = RFont(Glyphs.documents[0].font, thisMasterIndex)
    f2 = RFont(Glyphs.documents[1].font, thisMasterIndex)

    f1_glyphset = set(f1.keys())
    f2_glyphset = set(f2.keys())

    commonGlyphs = list(f1_glyphset.intersection(f2_glyphset))
    notSameGlyphsList = []
    sameGlyphsList = []
    blankGlyphsList = []
    blankGlyphsString = ""
    notSameGlyphsString = ""
    sameGlyphsString = ""

    for g in commonGlyphs:
        g1 = f1[g]
        g2 = f2[g]

        p1 = DigestPointPen()
        g1.drawPoints(p1)
        d1 = p1.getDigest()

        p2 = DigestPointPen()
        g2.drawPoints(p2)
        d2 = p2.getDigest()

        if d1 != d2:
            notSameGlyphsList += [g]
            if d1 == () or d2 == ():
                blankGlyphsList += [g]
        else:
            sameGlyphsList += [g]

    blankGlyphsString = '/{0}'.format('/'.join(blankGlyphsList))
    notSameGlyphsString = '/{0}'.format('/'.join(notSameGlyphsList))
    sameGlyphsString = '/{0}'.format('/'.join(sameGlyphsList))

    print "\n%s" % Glyphs.fonts[0].masters[thisMasterIndex].name
    print "\tDifferent Glyphs\n%s" % notSameGlyphsString
    print "\n\tDifference is that one file is blank Glyphs\n%s" % blankGlyphsString
    ## print "\n\tSame Glyphs\n%s" % sameGlyphsString

    if doNotCopyToBackground == 0:
        # Figure out which font is Glyphs.font and set thisFont as the file that is open
        if Glyphs.font.filepath == Glyphs.fonts[1].filepath:
            thisFont = Glyphs.fonts[1]
            otherFont = Glyphs.fonts[0]
        else:
            thisFont = Glyphs.fonts[0]
            otherFont = Glyphs.fonts[1]

        # Add glyphs to background
        thisFontMasterID = thisFont.masters[thisMasterIndex].id

        for thisGlyphName in notSameGlyphsList:
            if thisGlyphName not in blankGlyphsList:

                # Get the current layer for the current glyph
                thisLayerInOtherFont = otherFont.glyphs[thisGlyphName].layerForKey_(thisFontMasterID)
                thisLayerInThisFont = thisFont.glyphs[thisGlyphName].layerForKey_(thisFontMasterID)
                thisGlyphInThisFontLayerBackground = thisLayerInThisFont.background
                sourceLayer = otherFont.glyphs[thisGlyphName].layerForKey_(thisFontMasterID).copyDecomposedLayer()

                # Clear the background and copy the paths, components and anchors
                thisLayerInThisFont.background.clear()
                copyPathsAndAnchorsFromLayerToLayer(sourceLayer, thisGlyphInThisFontLayerBackground)

    # Open new tabs with different glphs
    if notSameGlyphsList != []:
        Glyphs.font.newTab(notSameGlyphsString)
        # Change to the correct master
        Glyphs.font.currentTab.setMasterIndex_(thisMasterIndex)