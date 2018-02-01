# Usage: mpv --vf=vapoursynth=60fps.py --hwdec=no <file>

import vapoursynth as vs
core = vs.get_core()

src_fps = 24
dst_fps = 60

clip  = core.std.AssumeFPS(video_in, fpsnum=src_fps)
super = core.mv.Super(clip, pel=2)
bv    = core.mv.Analyse(super, isb=True, overlap=0)
fv    = core.mv.Analyse(super, isb=False, overlap=0)
# FlowFPS() is too slow to be run in real-time
#clip  = core.mv.FlowFPS(clip, super, bv, fv, dst_fps)
clip  = core.mv.BlockFPS(clip, super, bv, fv, dst_fps)

clip.set_output()