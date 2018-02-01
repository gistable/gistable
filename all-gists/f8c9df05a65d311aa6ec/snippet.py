import wx
from wx import glcanvas
import pyglet

# this line is very important, we're tricking pyglet into thinking there is a context avalible
# but we can't make it work with the shadow window that alows sharing of
# object between contexts
pyglet.options['shadow_window'] = False

# now that that is set we can import gl and get on our way
from pyglet import gl


class PygletGLPanel(wx.Panel):

    '''A simple class for using pyglet OpenGL with wxPython.'''

    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        # Forcing a no full repaint to stop flickering
        style = style | wx.NO_FULL_REPAINT_ON_RESIZE
        self.FIRST_PAINT = False
        # call super function
        super(PygletGLPanel, self).__init__(parent, id, pos, size, style)
        # init gl canvas data
        self.GLinitialized = False
        attribList = (glcanvas.WX_GL_RGBA,  # RGBA
                      glcanvas.WX_GL_DOUBLEBUFFER,  # Double Buffered
                      glcanvas.WX_GL_DEPTH_SIZE, 24)  # 24 bit
        # Create the canvas
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvas = glcanvas.GLCanvas(self, attribList=attribList)
        if wx.VERSION >= (2, 9):
            self.context = glcanvas.GLContext(self.canvas)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()
        # bind events
        self.canvas.Bind(
            wx.EVT_ERASE_BACKGROUND, self.processEraseBackgroundEvent)
        self.canvas.Bind(wx.EVT_SIZE, self.processSizeEvent)
        self.canvas.Bind(wx.EVT_PAINT, self.processPaintEvent)

    #==========================================================================
    # Canvas Proxy Methods
    #==========================================================================

    def GetGLExtents(self):
        '''Get the extents of the OpenGL canvas.'''
        return self.canvas.GetClientSize()

    def SwapBuffers(self):
        '''Swap the OpenGL buffers.'''
        self.canvas.SwapBuffers()

    #==========================================================================
    # wxPython Window Handlers
    #==========================================================================

    def processEraseBackgroundEvent(self, event):
        '''Process the erase background event.'''
        pass  # Do nothing, to avoid flashing on MSWin

    def processSizeEvent(self, event):
        '''Process the resize event.'''

        if wx.VERSION >= (2, 9):
            wx.CallAfter(self.doSetViewport)
        else:
            self.doSetViewport()
        event.Skip()

    def doSetViewport(self):
        if wx.VERSION >= (2, 9):
            self.Show()
            self.PrepareGL()
            # Make sure the frame is shown before calling SetCurrent.
            self.canvas.SetCurrent(self.context)
            size = self.GetGLExtents()
            self.winsize = (size.width, size.height)
            self.width, self.height = size.width, size.height
            if self.width < 0:
                self.width = 1
            if self.height < 0:
                self.height = 1
            self.OnReshape(size.width, size.height)
            self.canvas.Refresh(False)
        else:
            if self.canvas.GetContext():
                # Make sure the frame is shown before calling SetCurrent.
                self.Show()
                self.PrepareGL()
                self.canvas.SetCurrent()
                size = self.GetGLExtents()
                self.winsize = (size.width, size.height)
                self.width, self.height = size.width, size.height
                if self.width < 0:
                    self.width = 1
                if self.height < 0:
                    self.height = 1
                self.OnReshape(size.width, size.height)
                self.canvas.Refresh(False)

    def PrepareGL(self):
        if wx.VERSION >= (2, 9):
            self.canvas.SetCurrent(self.context)
        else:
            self.canvas.SetCurrent()

        # initialize OpenGL only if we need to
        if not self.GLinitialized:
            self.OnInitGL()
            self.GLinitialized = True
            size = self.GetGLExtents()
            self.OnReshape(size.width, size.height)

        self.pygletcontext.set_current()

    def processPaintEvent(self, event):
        '''Process the drawing event.'''
        if not self.FIRST_PAINT:
            self.FIRST_PAINT = True
        self.PrepareGL()
        self.OnDraw()
        event.Skip()

    def Destroy(self):
        # clean up the pyglet OpenGL context
        self.pygletcontext.destroy()
        # call the super metho
        super(wx.Panel, self).Destroy()

    #==========================================================================f
    # GLFrame OpenGL Event Handlers
    #==========================================================================

    def OnInitGL(self):
        '''Initialize OpenGL for use in the window.'''
        # create a pyglet context for this panel
        #self.pygletcontext = gl.Context(gl.current_context)
        if pyglet.version > "1.1.4":
            self.pygletcontext = PygletWXContext()
        else:
            self.pygletcontext = gl.Context()
        self.pygletcontext.set_current()
        # normal gl init
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glClearColor(1, 1, 1, 1)

        # create objects to draw
        self.create_objects()

    def OnReshape(self, width, height):
        '''Reshape the OpenGL viewport based on the dimensions of the window.'''
        # CORRECT WIDTH AND HEIGHT
        if width <= 0:
            width = 1
        if height <= 0:
            height = 1
        if self.GLinitialized:
            self.pygletcontext.set_current()
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, 0, height, 1, -1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        if self.GLinitialized:
            self.update_object_resize(width, height)

    def OnDraw(self, *args, **kwargs):
        "Draw the window."
        # clear the context
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # draw objects
        self.draw_objects()
        # update screen
        self.SwapBuffers()

    #==========================================================================
    # To be implemented by a sub class
    #==========================================================================

    def create_objects(self):
        '''create opengl objects when opengl is initialized'''
        pass

    def update_object_resize(self, width, height):
        '''called when the window receives only if opengl is initialized'''
        pass

    def draw_objects(self):
        '''called in the middle of ondraw after the buffer has been cleared'''
        pass


class PygletWXContext(gl.Context):

    def __init__(self, config=None, context_share=None):
        self.config = config
        self.context_share = context_share
        self.canvas = None

        if context_share:
            self.object_space = context_share.object_space
        else:
            self.object_space = gl.ObjectSpace()

    def attach(self, canvas=None):
        pass

    def detach(self):
        pass

    def set_current(self):
        # XXX not per-thread
        gl.current_context = self

        # XXX
        gl.gl_info.set_active_context()
        gl.glu_info.set_active_context()

        # Implement workarounds
        if not self._info:
            self._info = gl.gl_info.GLInfo()
            self._info.set_active_context()
            for attr, check in self._workaround_checks:
                setattr(self, attr, check(self._info))

        # Release textures and buffers on this context scheduled for deletion.
        # Note that the garbage collector may introduce a race condition,
        # so operate on a copy of the textures/buffers and remove the deleted
        # items using list slicing (which is an atomic operation)
        if self.object_space._doomed_textures:
            textures = self.object_space._doomed_textures[:]
            textures = (gl.GLuint * len(textures))(*textures)
            gl.glDeleteTextures(len(textures), textures)
            self.object_space._doomed_textures[0:len(textures)] = []
        if self.object_space._doomed_buffers:
            buffers = self.object_space._doomed_buffers[:]
            buffers = (gl.GLuint * len(buffers))(*buffers)
            gl.glDeleteBuffers(len(buffers), buffers)
            self.object_space._doomed_buffers[0:len(buffers)] = []

#-------------------------------------------------------------------------
# EditorGLPanel
#-------------------------------------------------------------------------


class EditorGLPanel(PygletGLPanel):

    def __init__(self, parent, id=wx.ID_ANY, rows=1, columns=1, coord=(0, 0), drawmode=1):
        """Basic constructor for the wxGLCanvas

        Arguments:
        parent -- The wxWindow instance to set as this panel's parent
        id -- The ID of the panel
        rows -- The number of horizontal rows used for tiles
        columns -- The number of vertical columns used for tiles
        coord -- The coordinate of the tile that the image will draw from the source
        drawmode -- An integer to decide what drawing mode will be used.
            0: CropAndShrink -- Images will be both scaled down and cropped to fit
            1: Shrink -- Scales image down if too large, else the image is simply centered
            2: StretchAspect -- The image will be stretched to fill panel while maintaining aspect ratio
            3: Cropped -- Oversized images too large for the panel will simply be cropped
            4: Stretch -- The entire image is stretched, and aspect ratio is ignored
            5: TopLeft -- Image is anchored to top left corner and cropped
        Returns:
        None

        """
        super(EditorGLPanel, self).__init__(parent, id)
        self._rows = rows
        self._columns = columns
        self._coord = coord
        self._drawmode = drawmode
        self._image = None
        self.draw_objects()
        self._contextMenu = None
        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.canvas_RightClicked)

    def SetRows(self, rows):
        if rows < 1:
            rows = 1
        self._rows = rows

    def SetColumns(self, columns):
        if columns < 1:
            columns = 1
        self._columns = columns

    def canvas_RightClicked(self, event):
        """Creates the context menu if necessary, then displays it"""
        if self._contextMenu is None:
            self._createContextMenu()
        self._contextMenu.Check(self._drawmode, True)
        self.canvas.PopupMenu(self._contextMenu, event.GetPosition())

    def menuItem_SelectionChanged(self, event):
        """updates the draw mode"""
        self.SetDrawMode(event.GetId())

    def _createContextMenu(self):
        """Creates the context menu on demand"""
        self._contextMenu = wx.Menu()
        self.menuItemCropAndShrink = wx.MenuItem(
            self._contextMenu, 0, "Crop and Shrink", "Oversized images will be scaled and cropped evenly", wx.ITEM_RADIO)
        self._contextMenu.AppendItem(self.menuItemCropAndShrink)
        self.menuItemCropAndShrink.Check(True)
        self.menuItemShrink = wx.MenuItem(
            self._contextMenu, 1, "Shrink", "Oversized images will scale to the windows size while maintaining aspect ratio", wx.ITEM_RADIO)
        self._contextMenu.AppendItem(self.menuItemShrink)
        self.menuItemStretchAspect = wx.MenuItem(
            self._contextMenu, 2, "Stretch Aspect", "Images will expand to fill the window while maintaining aspect ratio", wx.ITEM_RADIO)
        self._contextMenu.AppendItem(self.menuItemStretchAspect)
        self.menuItemCrop = wx.MenuItem(
            self._contextMenu, 3, "Crop", "Image will be cropped to the window's size", wx.ITEM_RADIO)
        self._contextMenu.AppendItem(self.menuItemCrop)
        self.menuItemStretch = wx.MenuItem(
            self._contextMenu, 4, "Stretch", "Image will be stretched to fill the window and ignore the aspect ratio", wx.ITEM_RADIO)
        self._contextMenu.AppendItem(self.menuItemStretch)
        self.menuItemNone = wx.MenuItem(
            self._contextMenu, 5, "None", "No resizing, cropping, or centering will be performed", wx.ITEM_RADIO)
        self._contextMenu.AppendItem(self.menuItemNone)
        self.Bind(wx.EVT_MENU, self.menuItem_SelectionChanged,
                  id=self.menuItemCropAndShrink.GetId())
        self.Bind(wx.EVT_MENU, self.menuItem_SelectionChanged,
                  id=self.menuItemShrink.GetId())
        self.Bind(wx.EVT_MENU, self.menuItem_SelectionChanged,
                  id=self.menuItemStretchAspect.GetId())
        self.Bind(wx.EVT_MENU, self.menuItem_SelectionChanged,
                  id=self.menuItemCrop.GetId())
        self.Bind(wx.EVT_MENU, self.menuItem_SelectionChanged,
                  id=self.menuItemStretch.GetId())
        self.Bind(wx.EVT_MENU, self.menuItem_SelectionChanged,
                  id=self.menuItemNone.GetId())

    def ChangeImage(self, pilImage):
        """Changes the displayed image"""
        self._image = pilImage
        del (pilImage)
        if self.FIRST_PAINT:
            self.PrepareGL()
            self.OnDraw()

    def GetDrawMode(self):
        """Returns the integer value that represents the current drawing mode"""
        return self._drawmode

    def SetDrawMode(self, drawmode):
        """Sets the drawing mode and refreshes the display"""
        self._drawmode = drawmode
        if self.FIRST_PAINT:
            self.PrepareGL()
            self.OnDraw()

    def draw_objects(self):
        """Draws the objects on the canvas"""
        if not self.GLinitialized:
            return

        # clear the screen
        gl.glClearColor(0.93, 0.93, 0.93, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        if self._image is None:
            return
        # Convert PIL image to pyglet image
        srcImage = pyglet.image.create(*self._image.size).get_image_data()
        pitch = -len('RGBA') * srcImage.width
        data = self._image.tostring()
        srcImage.set_data('RGBA', pitch, data)
        # Clear the canvas and calculate the region to draw
        tile_width = srcImage.width // self._rows
        tile_height = srcImage.height // self._columns
        x = self._coord[0] * tile_width
        y = self._coord[1] * tile_height
        y = srcImage.height - y - tile_height
        subimage = srcImage.get_region(x, y, tile_width, tile_height)
        subimage.align_x = subimage.align_y = 0
        # Branch by what mode is selected to draw
        if self._drawmode == 0:
            self.CropAndShrink(subimage)
        elif self._drawmode == 1:
            self.Shrink(subimage)
        elif self._drawmode == 2:
            self.StretchAspect(subimage)
        elif self._drawmode == 3:
            self.Cropped(subimage)
        elif self._drawmode == 4:
            self.Stretch(subimage)
        else:
            self.TopLeft(subimage)
        del (srcImage)

    #---------------------------------------------------------------
    # Draw Modes
    #---------------------------------------------------------------
    def CropAndShrink(self, pygletimage):
        """Images will be both scaled down and cropped to fit"""
        width, height = self.GetClientSize()
        w, h = pygletimage.width, pygletimage.height
        x, y, = (width - w) // 2, (height - h) // 2
        if width < w or height < h:
            diff_w = (w - width) // 2
            diff_h = (h - height) // 2
            pygletimage.blit(x // 2, y // 2, 0, w - diff_w, h - diff_h)
        else:
            pygletimage.blit(x, y, 0, w, h)
        del (pygletimage)

    def Shrink(self, pygletimage):
        """Scales image down if too large, else the image is simply centered"""
        width, height = self.GetClientSize()
        w, h = pygletimage.width, pygletimage.height
        x, y, = (width - w) // 2, (height - h) // 2
        if width < w or height < h:
            self.StretchAspect(pygletimage)
        else:
            pygletimage.blit(x, y, 0, w, h)
        del (pygletimage)

    def StretchAspect(self, pygletimage):
        """The image will be stretched to fill panel while maintaining aspect ratio"""
        width, height = self.GetClientSize()
        w, h = pygletimage.width, pygletimage.height
        x_ratio = float(width) / w
        y_ratio = float(height) / h
        if y_ratio > x_ratio:
            ch = h * x_ratio
            pygletimage.blit(0, (height - ch) // 2, 0, width, ch)
        else:
            cw = w * y_ratio
            pygletimage.blit((width - cw) // 2, 0, 0, cw, height)
        del (pygletimage)

    def Cropped(self, pygletimage):
        """Oversized images too large for the panel will simply be cropped"""
        width, height = self.GetClientSize()
        w, h = pygletimage.width, pygletimage.height
        x, y = (width - w) // 2, (height - h) // 2
        if w > width:
            x = (width - w) // 2
        if h > height:
            y = (height - h) // 2
        pygletimage.blit(x, y, 0, w, h)
        del (pygletimage)

    def Stretch(self, pygletimage):
        """The entire image is stretched, and aspect ratio is ignored"""
        width, height = self.GetClientSize()
        pygletimage.blit(0, 0, 0, width, height)

    def TopLeft(self, pygletimage):
        """Image is anchored to top left corner and cropped"""
        y = self.GetClientSize()[1] - pygletimage.height
        pygletimage.blit(0, y, 0, pygletimage.width, pygletimage.height)
        del (pygletimage)
