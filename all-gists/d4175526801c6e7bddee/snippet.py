from drawBot import *
from drawBot.ui.drawView import DrawView

from vanilla import *

class DrawBotViewer(object):
    
    def __init__(self):
        # create a window        
        self.w = Window((400, 400), minSize=(200, 200))
        # add a slider
        self.w.slider = Slider((10, 10, -10, 22), callback=self.sliderCallback)
        # add a canvas
        self.w.drawBotCanvas = DrawView((0, 30, -0, -0))
        # draw something
        self.drawIt()
        # open the window
        self.w.open()
    
    def sliderCallback(self, sender):
        # slider chagned so redraw it
        self.drawIt()
        
    def drawIt(self):
        # get the value from the slider
        value = self.w.slider.get()
        # initiate a new drawing
        newDrawing()
        # add a page
        newPage(300, 300)
        # set a fill
        fill(1, value/100., 0)
        # draw a rectangle
        rect(10, 10, 100, 100)
        # set a font size
        fontSize(100 + value)
        # draw some text
        text("Hallo", (10, 120))
        # get the pdf document
        pdfData = pdfImage()
        # set the pdf document into the canvas
        self.w.drawBotCanvas.setPDFDocument(pdfData)
        
DrawBotViewer()