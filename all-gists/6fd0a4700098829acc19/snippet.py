# レンダリング用コマンドライン自動生成
# render_nodesを複数にするとフレームを分割してコマンドをprintする
# フレームの分割がたまにミスるのはご愛嬌（放置中）

from pymel.core import *
# settings
tmpl = '"%(render_path)s" -r %(renderer)s %(frame_range)s -proj "%(proj)s" "%(scene)s"'
render_path = r'C:\Program Files\Autodesk\Maya2014\bin\Render'
renderer = 'mr'
platform = 'win'
set_frame_range = True
s = SCENE.defaultRenderGlobals.startFrame.get()
e = SCENE.defaultRenderGlobals.endFrame.get()

render_nodes = 1

# procedural
nframes = e - s + 1.0
frames_per_node = nframes / render_nodes
scene = sceneName()
proj = '/'.join(scene.split('/')[:-2])
path_to_win = lambda path: '\\'.join(path.split('/'))
if platform == 'win':
    scene = path_to_win(scene)
    proj = path_to_win(proj)
_s = s
for i in range(render_nodes):
    if set_frame_range:
        _e = _s + frames_per_node - 1
        if set_frame_range:
            frame_range = '-s %d -e %d' % (_s, _e)
        _s = _e + 1
    else:
        frame_range = ''
    kwds = {'render_path': render_path, 'renderer': renderer, 'frame_range': frame_range, 'proj': proj, 'scene': scene}
    print tmpl % kwds
print('# Done')

