# Draw cairo in a pyglet window - without an intermediate image file.

import ctypes
#import cairocffi as cairo # example will work with cairocffi instead too
import cairo
import time

from pyglet import app, clock, font, gl, image, window

WIDTH, HEIGHT = 400, 400

window = window.Window(width=WIDTH, height=HEIGHT)
ft = font.load('Arial', 24)
text = font.Text(ft, 'Hello World')

# create data shared by ImageSurface and Texture
data = (ctypes.c_ubyte * (WIDTH * HEIGHT * 4))()
stride = WIDTH * 4
surface = cairo.ImageSurface.create_for_data (data, cairo.FORMAT_ARGB32,
WIDTH, HEIGHT, stride); 
texture = image.Texture.create_for_size(gl.GL_TEXTURE_2D, WIDTH, HEIGHT, gl.GL_RGBA)

def update_surface(dt, surface):
    # draw a rotating red triangle
    ctx = cairo.Context(surface)
    ctx.translate(200, 200)
    ctx.rotate(time.time())

    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()

    ctx.set_line_width(15)
    ctx.set_source_rgb(1, 0, 0)
    ctx.move_to(0, -200)
    ctx.line_to(200, 200)
    ctx.rel_line_to(-400, 0)
    ctx.close_path()
    ctx.stroke()

@window.event
def on_draw():
    window.clear()

    gl.glEnable(gl.GL_TEXTURE_2D)
    
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, WIDTH, HEIGHT, 0, gl.GL_BGRA,
    gl.GL_UNSIGNED_BYTE,
    data)
    
    gl.glBegin(gl.GL_QUADS)
    gl.glTexCoord2f(0.0, 1.0)
    gl.glVertex2i(0, 0)
    gl.glTexCoord2f(1.0, 1.0)
    gl.glVertex2i(WIDTH, 0)
    gl.glTexCoord2f(1.0, 0.0)
    gl.glVertex2i(WIDTH, HEIGHT)
    gl.glTexCoord2f(0.0, 0.0)
    gl.glVertex2i(0, HEIGHT)
    gl.glEnd()

    text.draw()

    #print('FPS: %f' % clock.get_fps())


clock.schedule_interval(update_surface, 1/120.0, surface)
app.run()