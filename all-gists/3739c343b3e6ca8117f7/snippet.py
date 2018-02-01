""" port oit, copied from glumpy """
import numpy as np

from vispy import app, gloo
from vispy.util.transforms import translate, perspective, rotate

vert_quads = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

attribute vec4 a_color;
attribute vec3 a_position;

varying vec4 v_color;
varying float v_depth;

void main()
{
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
    v_depth = - (u_view * u_model * vec4(a_position, 1.0)).z;
    v_color = a_color;
}
"""

frag_quads = """
uniform float u_pass;

varying vec4 v_color;
varying float v_depth;

void main()
{
    float z = abs(v_depth);
    float alpha = v_color.a;

    float weight = pow(alpha, 2.0f) *
                   clamp(0.002f/(1e-5f + pow(z/200.0f, 4.0f)), 1e-2, 3e3);

    if( u_pass < 0.5 )
        gl_FragColor = vec4(v_color.rgb * alpha, alpha) * weight;
    else
        gl_FragColor = vec4(alpha);
}
"""

vert_post = """
attribute vec2 a_position;
varying vec2 v_texcoord;

void main(void)
{
    gl_Position = vec4(a_position, 0, 1);
    v_texcoord = (a_position + 1.0)/2.0;
}
"""

frag_post = """
uniform sampler2D tex_accumulation;
uniform sampler2D tex_revealage;

varying vec2 v_texcoord;

void main(void)
{
    vec4 accum = texture2D(tex_accumulation, v_texcoord);
    float r = texture2D(tex_revealage, v_texcoord).r;
    if( r == 1.0)
        discard;
    gl_FragColor = vec4(accum.rgb / clamp(accum.a, 1e-5f, 5e4f), 1-r);
}
"""

C0 = (0.75, 0.75, 0.75, 1.00)
C1 = (1.00, 0.00, 0.00, 0.75)
C2 = (1.00, 1.00, 0.00, 0.75)
C3 = (0.00, 0.00, 1.00, 0.75)


class Canvas(app.Canvas):
    """ build canvas class for this demo """

    def __init__(self):
        """ initialize the canvas """
        app.Canvas.__init__(self,
                            size=(512, 512),
                            title='oit-multipass',
                            keys='interactive')

        # RGBA32F float texture size[0]=height, size[1]=width
        accum = np.zeros((self.size[0], self.size[1], 4), np.float32)
        accum_texture = gloo.Texture2D(accum)

        # R32F float texture
        reveal = np.zeros((self.size[0], self.size[1]), np.float32)
        reveal_texture = gloo.Texture2D(reveal)

        # store textures
        self.accum = accum_texture
        self.reveal = reveal_texture

        # Framebuffer with two color targets
        framebuffer = gloo.FrameBuffer(color=self.accum)

        # build programs
        quads = gloo.Program(vert_quads, frag_quads, count=12)
        pos = [(-1, -1, -1), (-1, +1, -1), (+1, -1, -1), (+1, +1, -1),
               (-1, -1,  0), (-1, +1,  0), (+1, -1,  0), (+1, +1,  0),
               (-1, -1, +1), (-1, +1, +1), (+1, -1, +1), (+1, +1, +1)]
        quads["a_position"] = np.array(pos) * 10

        quads["a_color"] = C1, C1, C1, C1, C2, C2, C2, C2, C3, C3, C3, C3
        quads['u_pass'] = 0
        indices = np.zeros((3, 6), dtype=np.uint32)
        indices[0] = 0 + np.array([0, 1, 2, 1, 2, 3])
        indices[1] = 4 + np.array([0, 1, 2, 1, 2, 3])
        indices[2] = 8 + np.array([0, 1, 2, 1, 2, 3])
        indices = gloo.IndexBuffer(indices)

        # Post composition
        post = gloo.Program(vert_post, frag_post)
        post['tex_accumulation'] = self.accum
        post['tex_revealage'] = self.reveal
        post['a_position'] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # set view
        view = translate((0, 0, -50))

        # set rotate
        theta = 45
        phi = -45
        model = np.dot(rotate(theta, (0, 0, 1)),
                       rotate(phi, (1, 0, 0)))

        # projection
        projection = perspective(45.0, 1.0, 0.1, 200.0)

        # matrix
        quads['u_model'] = model
        quads['u_view'] = view
        quads['u_projection'] = projection

        # bind
        self.framebuffer = framebuffer
        self.quads = quads
        self.post = post
        self.indices = indices

        # config and set viewport
        gloo.set_viewport(0, 0, *self.physical_size)

        # show the canvas
        self.show()

    def on_resize(self, event):
        """ canvas resize callback """
        gloo.set_viewport(0, 0, *event.physical_size)
        # ratio = event.physical_size[0] / float(event.physical_size[1])
        # self.quads['u_projection'] = perspective(50.0, ratio, 0.1, 100.0)

    def on_draw(self, event):
        """ canvas update callback """

        # config
        gloo.clear(color=C0)
        gloo.set_state(preset=None,
                       depth_test=True,
                       blend=True,
                       depth_mask=False)

        # draw framebuffers
        # pass 0
        self.quads['u_pass'] = 0.0
        self.framebuffer.color_buffer = self.accum
        self.framebuffer.activate()
        gloo.clear(color=(0, 0, 0, 0))
        gloo.set_blend_func('one', 'one')
        self.quads.draw('triangles', self.indices)
        self.framebuffer.deactivate()

        # pass 1
        self.quads['u_pass'] = 1.0
        self.framebuffer.color_buffer = self.reveal
        self.framebuffer.activate()
        gloo.clear(color=(1, 1, 1, 1))
        gloo.set_blend_func('zero', 'one_minus_src_color')
        self.quads.draw('triangles', self.indices)
        self.framebuffer.deactivate()

        # render
        gloo.set_blend_func('src_alpha', 'one_minus_src_alpha')
        self.post.draw('triangles', self.indices)

# Finally, we show the canvas and we run the application.
c = Canvas()
app.run()
