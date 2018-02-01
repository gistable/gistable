#!/usr/bin/python

import Image
import hashlib
from operator import itemgetter
import sys
import os.path

def convert(theImage, dimension = 0, sliceWidth = 1):
    theSliceLength = theImage.size[1 - dimension]

    # Compute hashes of all 1 pixel slices (either columns or rows) in the image
    theSlices = []
    for N in xrange(0, theImage.size[dimension], sliceWidth):
        slice = theImage.copy()
        if dimension == 0:
            slice = slice.crop((N, 0, N + sliceWidth, theSliceLength))
        else:
            slice = slice.crop((0, N, theSliceLength, N + sliceWidth))
        # Using hashlib to make printable values. Could just use raw string.
        theSlices.append(hashlib.md5(slice.tostring()).hexdigest())

    # Count frequency of all but first and last slices
    theSliceFrequencies = {}
    for theSlice in theSlices[sliceWidth:-sliceWidth]:
        if theSlice not in theSliceFrequencies:
            theSliceFrequencies[theSlice] = 0
        theSliceFrequencies[theSlice] += 1
    theSliceFrequencies = [(k, v) for k, v in theSliceFrequencies.items()]

    # Find the most common frequency
    theSliceFrequencies.sort(key=itemgetter(1), reverse=True)
    theMostFrequentSlice = theSliceFrequencies[0][0]

    # Compute the size of the new image
    theNewDimensionSize = 1
    for theSlice in theSlices:
        if theSlice != theMostFrequentSlice:
            theNewDimensionSize += 1
    theNewDimensionSize *= sliceWidth

    if dimension == 0:
        theNewSize = (theNewDimensionSize, theSliceLength)
    else:
        theNewSize = (theSliceLength, theNewDimensionSize)

    # Make a new image. Skipping over all but one of the most frequent slice.
    theNewImage = Image.new('RGBA', theNewSize)
    OUT = 0
    theFlag = False
    for IN, theSlice in enumerate(theSlices):
        IN *= sliceWidth
        if theSlice == theMostFrequentSlice:
            if theFlag == True:
                continue
            theFlag = True

        slice = theImage.copy()
        if dimension == 0:
            slice = slice.crop((IN, 0, IN + sliceWidth, theSliceLength))
            theNewImage.paste(slice, (OUT, 0, OUT + sliceWidth, theSliceLength))
        else:
            slice = slice.crop((0, IN, theSliceLength, IN + sliceWidth))
            theNewImage.paste(slice, (0, OUT, theSliceLength, OUT + sliceWidth))
            pass
        OUT += sliceWidth

    return theNewImage

if __name__ == '__main__':
    thePath = '/Users/schwa/Desktop/DoneButton.png'
    sliceWidth = 1
    if '@2x' in thePath:
        sliceWidth = 2
    theImage = Image.open(thePath)
    theImage = convert(theImage, dimension = 0, sliceWidth = sliceWidth)
    theImage = convert(theImage, dimension = 1, sliceWidth = sliceWidth)
    theNewPath = os.path.splitext(thePath)[0] + '_converted.png'
    theImage.save(theNewPath)
