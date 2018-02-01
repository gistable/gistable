"""
Apply any filter on any view. 

CIFilter reference: https://developer.apple.com/library/mac/documentation/GraphicsImaging/Reference/CoreImageFilterReference/index.html#//apple_ref/doc/filter/ci/CIAccordionFoldTransition

"""

from mojo.UI import CurrentSpaceCenter
from AppKit import *

from vanilla import *

class Blurryfyer(object):
    
    def __init__(self):
        # create a window
        self.w = Window((250, 60), "Blurryfyer")
        # create a slider
        self.w.s = Slider((10, 10, -10, 22), callback=self.blurryfyerCallback, continuous=False)
        # open the window
        self.w.open()
    
    def blurryfyerCallback(self,sender):
        # get the value from the slider
        value = sender.get()
        # get the current space center
        sp = CurrentSpaceCenter()
        # if there is no space center
        if sp is None:
            # do nothing
            return
        # get the line view (this is embedded into a scroll view)
        view = sp.glyphLineView.contentView()
        # create the filter
        blur = CIFilter.filterWithName_("CIGaussianBlur")
        # set the filter defaults
        blur.setDefaults()
        # change the input radius for the blur
        blur.setValue_forKey_(value, "inputRadius")
        # collect all filters in a list
        filters = [blur]
        # tel the view to use layers
        view.setWantsLayer_(True)
        # set the filters into the view
        view.setContentFilters_(filters)

Blurryfyer()
