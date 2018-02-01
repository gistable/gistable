# read in and display ImagePlus object(s)
from loci.plugins import BF
file = "/Users/curtis/data/tubhiswt4D.ome.tif"
imps = BF.openImagePlus(file)
for imp in imps:
    imp.show()

# read in and display ImagePlus(es) with arguments
from loci.common import Region
from loci.plugins.in import ImporterOptions
options = ImporterOptions()
options.setColorMode(ImporterOptions.COLOR_MODE_GRAYSCALE)
options.setCrop(True)
options.setCropRegion(0, Region(15, 25, 50, 70))
options.setId(file)
imps = BF.openImagePlus(options)
for imp in imps:
    imp.show()

# parse metadata
from loci.formats import ImageReader
from loci.formats import MetadataTools
reader = ImageReader()
omeMeta = MetadataTools.createOMEXMLMetadata()
reader.setMetadataStore(omeMeta)
reader.setId(file)
seriesCount = reader.getSeriesCount()
reader.close()

# print out series count from two different places (they should always match!)
from ij import IJ
imageCount = omeMeta.getImageCount()
IJ.log("Total # of image series (from BF reader): " + str(seriesCount))
IJ.log("Total # of image series (from OME metadata): " + str(imageCount))

# print out physical calibration for first image series
from ome.units import UNITS
physSizeX = omeMeta.getPixelsPhysicalSizeX(0)
physSizeY = omeMeta.getPixelsPhysicalSizeY(0)
physSizeZ = omeMeta.getPixelsPhysicalSizeZ(0)
IJ.log("Physical calibration:")
if (physSizeX is not None):
	IJ.log("\tX = " + str(physSizeX.value()) + " " + physSizeX.unit().getSymbol()
		+ " = " + str(physSizeX.value(UNITS.MICROM)) + " microns")
if (physSizeY is not None):
	IJ.log("\tY = " + str(physSizeY.value()) + " " + physSizeY.unit().getSymbol()
		+ " = " + str(physSizeY.value(UNITS.MICROM)) + " microns")
if (physSizeZ is not None):
	IJ.log("\tZ = " + str(physSizeZ.value()) + " " + physSizeZ.unit().getSymbol()
		+ " = " + str(physSizeZ.value(UNITS.MICROM)) + " microns")
