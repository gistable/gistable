#!/usr/bin/python

import sys
import time
import math

import gtk
import gobject
import pyglet
import pyglet.gl as gl


if sys.platform in ('win32', 'cygwin'):
    from pyglet.window.win32 import _user32
    from pyglet.gl import wgl
elif sys.platform == 'linux2':
    from pyglet.gl import glx


class GlDrawingArea(gtk.DrawingArea):
    config = None
    context = None

    def __init__(self, navigation=True):
        gtk.DrawingArea.__init__(self)
        self.gl_initialized = False
        self.set_double_buffered(False)

        self.connect('show', self.on_show)
        self.connect('hide', self.on_hide)
        self.connect('expose-event', self.on_expose)
        self.connect('configure-event', self.on_configure)

        if navigation:
            self.connect('motion_notify_event', self.on_motion_notify)
            self.connect('button_press_event', self.on_button_press)
            self.connect('scroll-event', self.on_mouse_scroll)

            self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                            gtk.gdk.POINTER_MOTION_MASK |
                            gtk.gdk.POINTER_MOTION_HINT_MASK |
                            gtk.gdk.SCROLL_MASK)

    def on_show(self, wid):
        self.get_config()

    def on_hide(self, wid):
        self.gl_initialized = False
        self.context = None
        self.config = None

    def get_config(self):
        if not self.config:
            platform = pyglet.window.get_platform()
            display = platform.get_default_display()
            self.screen = display.get_screens()[0]

            for template_config in [
                gl.Config(double_buffer=True, depth_size=32),
                gl.Config(double_buffer=True, depth_size=24),
                gl.Config(double_buffer=True, depth_size=16)]:
                try:
                    self.config = self.screen.get_best_config(template_config)
                    break
                except pyglet.window.NoSuchConfigException:
                    pass

            if not self.config:
                raise pyglet.window.NoSuchConfigException('No standard config '
                                                          'is available.')

            if not self.config.is_complete():
                print 'not complete'
                self.config = self.screen.get_best_config(self.config)

            if not self.context:
                cur_context = pyglet.gl.current_context
                self.context = self.config.create_context(cur_context)

    def switch_to(self):
        if sys.platform == 'darwin':
            gl.agl.aglSetCurrentContext(self._agl_context)
            gl._aglcheck()
        elif sys.platform in ('win32', 'cygwin'):
            self._dc = _user32.GetDC(self.window.handle)
            self.context._set_window(self)
            wgl.wglMakeCurrent(self._dc, self.context._context)
        else:
            glx.glXMakeCurrent(self.config._display, self.window.xid,
                               self.context._context)
        self.context.set_current()
        gl.gl_info.set_active_context()
        gl.glu_info.set_active_context()

    def flip(self):
        if sys.platform == 'darwin':
            gl.agl.aglSwapBuffers(self._agl_context)
            gl._aglcheck()
        elif sys.platform in ('win32', 'cygwin'):
            wgl.wglSwapLayerBuffers(self._dc, wgl.WGL_SWAP_MAIN_PLANE)
        else:
            glx.glXSwapBuffers(self.config._display, self.window.xid)

    def on_configure(self, wid, event):
        if not self.context:
            return

        width = wid.allocation.width
        height = wid.allocation.height
        if width > 1:
            # make the context current
            # and setup opengl
            #
            # **** this only can be with the window realized ****
            #
            self.switch_to()
            if not self.gl_initialized:
                self.setup()
                self.gl_initialized = 1
            gl.glViewport(0, 0, width, height)

    def on_expose(self, wid, event):
        width = wid.allocation.width
        height = wid.allocation.height
        self.display(width, height)

        if self.config.double_buffer:
            self.flip()
        else:
            gl.glFlush()
        return 0

    def navigate(self, state, dx, dy):
        if state & gtk.gdk.BUTTON1_MASK:
            # pan
            self.trans[0] -= dx / 100.0
            self.trans[1] += dy / 100.0
        elif state & gtk.gdk.BUTTON2_MASK:
            # zoom
            self.trans[2] += (dx + dy) / 100.0
        elif state & gtk.gdk.BUTTON3_MASK:
            # rotate
            self.rot[0] -= ((dy * 180.0) / 500.0) % 360
            self.rot[1] -= ((dx * 180.0) / 500.0) % 360

        self.queue_draw()

    def on_button_press(self, widget, event):
        self.old_x, self.old_y = event.x, event.y
        return True

    def on_motion_notify(self, widget, event):
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.state

        if not (state & (gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON2_MASK |
                         gtk.gdk.BUTTON3_MASK)):
            return True

        dx = self.old_x - x
        dy = self.old_y - y
        self.old_x, self.old_y = x, y

        self.navigate(state, dx, dy)
        return True

    def on_mouse_scroll(self, widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.navigate(gtk.gdk.BUTTON2_MASK, 50, 0)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.navigate(gtk.gdk.BUTTON2_MASK, -50, 0)

    def setup(self):
        pass

    def display(self, width, height):
        pass


class Torus(object):
    def __init__(self, radius, inner_radius, slices, inner_slices):
        # Create the vertex and normal arrays.
        vertices = []
        normals = []

        u_step = 2 * math.pi / (slices - 1)
        v_step = 2 * math.pi / (inner_slices - 1)
        u = 0.
        for i in range(slices):
            cos_u = math.cos(u)
            sin_u = math.sin(u)
            v = 0.
            for j in range(inner_slices):
                cos_v = math.cos(v)
                sin_v = math.sin(v)

                d = (radius + inner_radius * cos_v)
                x = d * cos_u
                y = d * sin_u
                z = inner_radius * sin_v

                nx = cos_u * cos_v
                ny = sin_u * cos_v
                nz = sin_v

                vertices.extend([x, y, z])
                normals.extend([nx, ny, nz])
                v += v_step
            u += u_step

        # Create ctypes arrays of the lists
        vertices = (gl.GLfloat * len(vertices))(*vertices)
        normals = (gl.GLfloat * len(normals))(*normals)

        # Create a list of triangle indices.
        indices = []
        for i in range(slices - 1):
            for j in range(inner_slices - 1):
                p = i * inner_slices + j
                indices.extend([p, p + inner_slices, p + inner_slices + 1])
                indices.extend([p,    p + inner_slices + 1, p + 1])
        indices = (gl.GLuint * len(indices))(*indices)

        # Compile a display list
        self.list = gl.glGenLists(1)
        gl.glNewList(self.list, gl.GL_COMPILE)

        gl.glPushClientAttrib(gl.GL_CLIENT_VERTEX_ARRAY_BIT)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, vertices)
        gl.glNormalPointer(gl.GL_FLOAT, 0, normals)
        gl.glDrawElements(gl.GL_TRIANGLES, len(indices), gl.GL_UNSIGNED_INT,
                          indices)
        gl.glPopClientAttrib()

        gl.glEndList()

    def draw(self):
        gl.glCallList(self.list)


class TorusExample(GlDrawingArea):
    def __init__(self, animated=True):
        super(TorusExample, self).__init__()

        self.torus = Torus(1, 0.3, 50, 30)
        self.rx = self.ry = self.rz = 0
        self.dt = 0.01

        self.trans = [0, 0, -4]
        self.rot = [0, 0]
        self.old_x = self.old_y = None
        self.animated = animated

    def on_show(self, wid):
        super(TorusExample, self).on_show(wid)
        self.handler_to = gobject.timeout_add(20, self.timeout)

    def on_hide(self, wid):
        gobject.source_remove(self.handler_to)
        super(TorusExample, self).on_hide(wid)

    def setup(self):
        # One-time GL setup
        gl.glClearColor(1, 1, 1, 0)
        gl.glColor3f(1, 0, 0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

        # Uncomment this line for a wireframe view
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Simple light setup.    On Windows GL_LIGHT0 is enabled by default,
        # but this is not the case on Linux or Mac, so remember to always
        # include it.
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_LIGHT1)

        # Define a simple function to create ctypes arrays of floats:
        def vec(*args):
            return (gl.GLfloat * len(args))(*args)

        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, vec(.5, .5, 1, 0))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, vec(.5, .5, 1, 1))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, vec(1, 1, 1, 1))
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, vec(1, 0, .5, 0))
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_DIFFUSE, vec(.5, .5, .5, 1))
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_SPECULAR, vec(1, 1, 1, 1))

        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE,
                        vec(0.5, 0, 0.3, 1))
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_SPECULAR, vec(1, 1, 1, 1))
        gl.glMaterialf(gl.GL_FRONT_AND_BACK, gl.GL_SHININESS, 50)

        if sys.platform in ('win32', 'cygwin'):
            font = 'Arial'
        else:
            font = 'DejaVu Sans Mono'

        self.lowerlabel = pyglet.text.Label('Hello, world', font_size=14,
                                            font_name=font, x=5, y=20,
                                            color=(0, 0, 0, 255))
        self.upperlabel = pyglet.text.Label('Hello, world', font_size=14,
                                            font_name=font, x=20, y=20,
                                            color=(0, 0, 0, 255))

    def display(self, width, height):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(60., width / float(height), .1, 1000.)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(self.trans[0], self.trans[1], self.trans[2])
        gl.glRotatef(self.rot[0], 1.0, 0.0, 0.0)
        gl.glRotatef(self.rot[1], 0.0, 1.0, 0.0)
        gl.glRotatef(self.rz, 0, 0, 1)
        gl.glRotatef(self.ry, 0, 1, 0)
        gl.glRotatef(self.rx, 1, 0, 0)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glColor3f(1, 0, 0)
        self.torus.draw()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, 0, height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glDisable(gl.GL_LIGHTING)
        gl.glColor3f(0, 1, 0)
        self.lowerlabel.text = 'Rx %.2f Ry %.2f Rz %.2f' % (self.rx, self.ry,
                                                            self.rz)
        self.lowerlabel.draw()
        self.upperlabel.text = time.strftime('Now is %H:%M:%S')
        self.upperlabel.x = width - self.upperlabel.content_width - 5
        self.upperlabel.y = height - self.upperlabel.content_height
        self.upperlabel.draw()

    def timeout(self):
        if self.animated:
            self.rx += self.dt * 1
            self.ry += self.dt * 80
            self.rz += self.dt * 30
            self.rx %= 360
            self.ry %= 360
            self.rz %= 360
        self.queue_draw()
        return True
