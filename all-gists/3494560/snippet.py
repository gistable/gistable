from glfwpy.glfw import *
from glfwpy.utils.obj_loader import ObjGeometry
import sys
from OpenGL.GL import *
from OpenGL.arrays import ArrayDatatype
import time

vertex = """
#version 330
in vec3 vin_position;
in vec3 vin_normal;
out vec3 vout_normal;

void main(void)
{
    vout_normal = vin_normal;
    gl_Position = vec4(vin_position.xyz, 1.0);
}
"""


fragment = """
#version 330
in vec3 vout_normal;
out vec4 fout_color;

void main(void)
{
    fout_color = vec4(vout_normal, 1.0);

}
"""

geom = ObjGeometry('../art/bunny_with_normals.obj')

vertex_data = geom.vertex_arr
index_data = geom.index_arr
normal_data = geom.normal_arr


class ShaderProgram(object):

    def __init__(self, vertex, fragment, geometry=None):
        self.program_id = glCreateProgram()
        vs_id = self.add_shader(vertex, GL_VERTEX_SHADER)
        frag_id = self.add_shader(fragment, GL_FRAGMENT_SHADER)

        glAttachShader(self.program_id, vs_id)
        glAttachShader(self.program_id, frag_id)
        glLinkProgram(self.program_id)

        if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.program_id)
            glDeleteProgram(self.program_id)
            glDeleteShader(vs_id)
            glDeleteShader(frag_id)
            raise RuntimeError('Error linking program: %s' % (info))
        glDeleteShader(vs_id)
        glDeleteShader(frag_id)

    def add_shader(self, source, shader_type):
        try:
            shader_id = glCreateShader(shader_type)
            glShaderSource(shader_id, source)
            glCompileShader(shader_id)
            if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
                info = glGetShaderInfoLog(shader_id)
                raise RuntimeError('Shader compilation failed: %s' % (info))
            return shader_id
        except:
            glDeleteShader(shader_id)
            raise

    def uniform_location(self, name):
        return glGetUniformLocation(self.program_id, name)

    def attribute_location(self, name):
        return glGetAttribLocation(self.program_id, name)


def foo(x, y):
    print x, y


def main():
    if not Init():
        print 'GLFW initialization failed'
        sys.exit(-1)

    OpenWindowHint(OPENGL_VERSION_MAJOR, 3)
    OpenWindowHint(OPENGL_VERSION_MINOR, 2)
    OpenWindowHint(OPENGL_PROFILE, OPENGL_CORE_PROFILE)
    OpenWindowHint(OPENGL_FORWARD_COMPAT, GL_TRUE)
    if not OpenWindow(1400, 800, 0, 0, 0, 0, 32, 0, WINDOW):
        print "OpenWindow failed"
        Terminate()
        sys.exit(-1)

    SetKeyCallback(foo)

    SetWindowTitle("Modern opengl example")
    Enable(AUTO_POLL_EVENTS)

    print 'Vendor: %s' % (glGetString(GL_VENDOR))
    print 'Opengl version: %s' % (glGetString(GL_VERSION))
    print 'GLSL Version: %s' % (glGetString(GL_SHADING_LANGUAGE_VERSION))
    print 'Renderer: %s' % (glGetString(GL_RENDERER))

    glEnable(GL_DEPTH_TEST)
    glViewport(0, 0, 1400, 800)
    glClearColor(0.8, 1.0, 0.8, 1.0)
    program = ShaderProgram(fragment=fragment, vertex=vertex)

    vao_id = glGenVertexArrays(1)
    vbo_id = glGenBuffers(3)
    glBindVertexArray(vao_id)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_id[0])
    glBufferData(GL_ARRAY_BUFFER,
        ArrayDatatype.arrayByteCount(vertex_data),
        vertex_data, GL_STATIC_DRAW)
    glVertexAttribPointer(program.attribute_location('vin_position'),
        3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_id[1])
    glBufferData(GL_ARRAY_BUFFER,
        ArrayDatatype.arrayByteCount(normal_data),
        normal_data, GL_STATIC_DRAW)
    glVertexAttribPointer(program.attribute_location('vin_normal'),
        3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vbo_id[2])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
        ArrayDatatype.arrayByteCount(index_data),
        index_data, GL_STATIC_DRAW)

    glBindVertexArray(0)
    running = True

    while running:
        t1 = time.clock()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(program.program_id)
        glBindVertexArray(vao_id)
        glDrawElements(GL_TRIANGLES,
            index_data.shape[0] * index_data.shape[1],
            GL_UNSIGNED_INT, None)
        glUseProgram(0)
        glBindVertexArray(0)
        SwapBuffers()
        print time.clock() - t1
        running = running and GetWindowParam(OPENED)

if __name__ == "__main__":
    main()
