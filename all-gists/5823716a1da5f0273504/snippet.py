#!/usr/bin/python2.7
"""Quick hack of 'modern' OpenGL example using pysdl2 and pyopengl
that shows a textured triangle; assumes there is a 'hazard.png' image
file in working directory.

Based on:

pysdl2 OpenGL example
http://www.tomdalling.com/blog/modern-opengl/02-textures/
http://www.arcsynthesis.org/gltut/Basics/Tut02%20Vertex%20Attributes.html
http://schi.iteye.com/blog/1969710
https://www.opengl.org/wiki/Vertex_Specification_Best_Practices#Vertex_Layout_Specification
http://docs.gl/gl3/glVertexAttribPointer
https://gist.github.com/jawa0/4003034
https://github.com/tomdalling/opengl-series/blob/master/linux/02_textures/source/main.cpp
"""
import sys
import ctypes
import numpy

from OpenGL import GL, GLU
from OpenGL.GL import shaders
from OpenGL.arrays import vbo

import PIL
from PIL import Image
import sdl2
from sdl2 import video
from numpy import array

shaderProgram = None
VAO = None
VBO = None
sampleTexture = None
texUnitUniform = None


def loadTexture(path):
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
    img_data = numpy.fromstring(img.tostring(), numpy.uint8)
    width, height = img.size

    # glTexImage2D expects the first element of the image data to be the
    # bottom-left corner of the image.  Subsequent elements go left to right,
    # with subsequent lines going from bottom to top.

    # However, the image data was created with PIL Image tostring and numpy's
    # fromstring, which means we have to do a bit of reorganization. The first
    # element in the data output by tostring() will be the top-left corner of
    # the image, with following values going left-to-right and lines going
    # top-to-bottom.  So, we need to flip the vertical coordinate (y). 
    texture = GL.glGenTextures(1)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0,
        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_data)
    GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
    return texture


def initialize():
    global shaderProgram
    global VAO
    global VBO
    global texUnitUniform
    global sampleTexture

    vertexShader = shaders.compileShader("""
#version 330

layout (location=0) in vec3 position;
layout (location=1) in vec2 texCoords;

out vec2 theCoords;

void main()
{
    gl_Position = vec4(position, 1);
    theCoords = texCoords;
}
""", GL.GL_VERTEX_SHADER)

    fragmentShader = shaders.compileShader("""
#version 330

uniform sampler2D texUnit;

in vec2 theCoords;

out vec4 outputColour;

void main()
{
    outputColour = texture(texUnit, theCoords);
}
""", GL.GL_FRAGMENT_SHADER)

    shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)

    vertexData = numpy.array([
         # X,    Y,   Z     U,   V
         0.0,  0.8, 0.0,  0.5, 1.0,
        -0.8, -0.8, 0.0,  0.0, 0.0,
         0.8, -0.8, 0.0,  1.0, 0.0,
    ], dtype=numpy.float32)

    # Core OpenGL requires that at least one OpenGL vertex array be bound
    VAO = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(VAO)

    # Need VBO for triangle vertices and texture UV coordinates
    VBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, vertexData.nbytes, vertexData,
        GL.GL_STATIC_DRAW)

    # enable array and set up data
    positionAttrib = GL.glGetAttribLocation(shaderProgram, 'position')
    coordsAttrib = GL.glGetAttribLocation(shaderProgram, 'texCoords')

    GL.glEnableVertexAttribArray(0)
    GL.glEnableVertexAttribArray(1)
    GL.glVertexAttribPointer(positionAttrib, 3, GL.GL_FLOAT, GL.GL_FALSE, 20,
        None)
    # the last parameter is a pointer
    GL.glVertexAttribPointer(coordsAttrib, 2, GL.GL_FLOAT, GL.GL_TRUE, 20,
        ctypes.c_void_p(12))

    # load texture and assign texture unit for shaders
    sampleTexture = loadTexture('hazard.png')
    texUnitUniform = GL.glGetUniformLocation(shaderProgram, 'texUnit')

    # Finished
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    GL.glBindVertexArray(0)


def render():
    global sampleTexture
    global shaderProgram
    global texUnitUniform
    global VAO
    GL.glClearColor(0, 0, 0, 1)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    # active shader program
    GL.glUseProgram(shaderProgram)

    try:
        # Activate texture
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, sampleTexture)
        GL.glUniform1i(texUnitUniform, 0)

        # Activate array
        GL.glBindVertexArray(VAO)

        # draw triangle
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
    finally:
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)


def run():
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
        print(sdl2.SDL_GetError())
        return -1

    window = sdl2.SDL_CreateWindow(b"OpenGL demo",
                                   sdl2.SDL_WINDOWPOS_UNDEFINED,
                                   sdl2.SDL_WINDOWPOS_UNDEFINED, 800, 600,
                                   sdl2.SDL_WINDOW_OPENGL)
    if not window:
        print(sdl2.SDL_GetError())
        return -1

    # Force OpenGL 3.3 'core' context.
    # Must set *before* creating GL context!
    video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
    video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MINOR_VERSION, 3)
    video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_PROFILE_MASK,
        video.SDL_GL_CONTEXT_PROFILE_CORE)
    context = sdl2.SDL_GL_CreateContext(window)

    # Setup GL shaders, data, etc.
    initialize()

    event = sdl2.SDL_Event()
    running = True
    while running:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                running = False
            elif (event.type == sdl2.SDL_KEYDOWN and
                event.key.keysym.sym == sdl2.SDLK_ESCAPE):
                running = False

        render()

        sdl2.SDL_GL_SwapWindow(window)
        sdl2.SDL_Delay(10)

    sdl2.SDL_GL_DeleteContext(context)
    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(run())
