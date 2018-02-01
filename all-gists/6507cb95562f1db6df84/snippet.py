from OpenGL import GL
from PyQt5 import QtWidgets, QtCore, QtGui, QtOpenGL
from OpenGL.GL.ARB.texture_rg import GL_R32F
import numpy as np
import ctypes
import time

w, h = 400, 400

class TestWidget(QtOpenGL.QGLWidget):
    
    def __init__(self):
        QtOpenGL.QGLWidget.__init__(self)
        self.resize(w, h)

        self.t = time.time()        
        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self.update)        
        self._update_timer.start(1e3 / 60.)
    
    def initializeGL(self):
        # create an image
        Y, X = np.ogrid[-2.5:2.5:h*1j, -2.5:2.5:w*1j]
        image = np.empty((h, w), dtype=np.float32)
        image[:] = np.exp(- X**2 - Y**2)# * (1. + .5*(np.random.rand(h, w)-.5))
        image[-30:] = np.linspace(0, 1, w)
              
        # create pixel buffer object for transferring textures
        self._buffer_id = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self._buffer_id)
        GL.glBufferData(GL.GL_PIXEL_UNPACK_BUFFER, w*h*4, None, GL.GL_STREAM_DRAW)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)

        # map and modify pixel buffer
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self._buffer_id)
        pbo_addr = GL.glMapBuffer(GL.GL_PIXEL_UNPACK_BUFFER, GL.GL_WRITE_ONLY)
        # write to PBO using ctypes memmove
        ctypes.memmove(pbo_addr, image.ctypes.data, (w*h * image.itemsize))
        # write to PBO using numpy interface
        pbo_ptr = ctypes.cast(pbo_addr, ctypes.POINTER(ctypes.c_float))
        pbo_np = np.ctypeslib.as_array(pbo_ptr, shape=(h, w))
        pbo_np[:] = image
        GL.glUnmapBuffer(GL.GL_PIXEL_UNPACK_BUFFER)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)
        
        # create texture from pixel buffer object
        self._texture_id = GL.glGenTextures(1)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self._buffer_id)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL_R32F, w, h, 0, GL.GL_RED, GL.GL_FLOAT, None)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)
        
        # create a shader for coloring the texture
        shader_program = QtGui.QOpenGLShaderProgram()
        vertex_src = """
        void main() {
            gl_TexCoord[0] = gl_MultiTexCoord0;
            gl_Position = gl_Vertex;
        }
        """
        fragment_src = """
        uniform highp sampler2D tex;
        uniform float amp;
        uniform float r;
        
        float rand(vec2 co){
            return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453 * (1.+r));
        }
        
        void main() {
            float val = texture2D(tex, gl_TexCoord[0]).r;
            val *= .7 + .3*rand(gl_TexCoord[0].xx) + .8*rand(gl_TexCoord[0].xy);
            vec4 color1 = vec4(0., 0., 0., 1.);
            vec4 color2 = vec4(3., .5, .2, 1.);
            gl_FragColor = mix(color1, color2, 3.5 * val * amp);
        }
        """
        shader_program.addShaderFromSourceCode(QtGui.QOpenGLShader.Vertex, vertex_src)
        shader_program.addShaderFromSourceCode(QtGui.QOpenGLShader.Fragment, fragment_src)
        shader_program.link()
        self._shader_program = shader_program
        self._amp_location = shader_program.uniformLocation("amp")
        self._r_location = shader_program.uniformLocation("r")

    def paintGL(self):
        t = time.time()
        amp = .6 + .6*np.cos(t*np.pi)**10
        r = np.random.rand(1)[0]
        
        target = QtCore.QRectF(-1, -1, 2, 2)
        self._shader_program.bind()
        self._shader_program.setUniformValue(self._amp_location, amp)
        self._shader_program.setUniformValue(self._r_location, r)
        self.drawTexture(target, self._texture_id)
    
    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)


app = QtWidgets.QApplication([])
win = TestWidget()
win.show()
app.exec_()