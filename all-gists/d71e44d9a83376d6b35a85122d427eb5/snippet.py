"""
This project was moved to https://github.com/kageru/Irrational-Encoding-Wizardry.
Don't expect this gist to be updated regularly.
"""


import vapoursynth as vs
import mvsfunc as mvf
import fvsfunc as fvf
from functools import partial

core = vs.core  # R37 or newer

# TODO fixedge port

def inverse_scale(source: vs.VideoNode, width=None, height=720, kernel='bilinear', kerneluv='blackman', taps=4, a1=1/3, a2=1/3, invks=True, mask_detail=False,
                  masking_areas=None, mask_highpass=0.3, denoise=False, bm3d_sigma=1, knl_strength=0.4, use_gpu=True) -> vs.VideoNode:
    """
    source = input clip
    width, height, kernel, taps, a1, a2 are parameters for resizing
    mask_detail, masking_areas, mask_highpass are parameters for masking; mask_detail = False to disable
    masking_areas takes frame tuples to define areas which will be masked (e.g. opening and ending)
    masking_areas = [[1000, 2500], [30000, 32000]]. Start and end frame are inclusive.
    mask_highpass is used to remove small artifacts from the mask. Value must be normalized.
    denoise, bm3d_sigma, knl_strength, and use_gpu are parameters for denoising; denoise = False to disable
    use_gpu = True -> chroma will be denoised with KNLMeansCL (faster)
    """
    if source.format.bits_per_sample != 32:
        source = core.fmtc.bitdepth(source, bits=32)
    if width is None:
        width = getw(height, ar=source.width/source.height)
    planes = clip_to_plane_array(source)
    if denoise and use_gpu:
        planes[1], planes[2] = [core.knlm.KNLMeansCL(plane, a=2, h=knl_strength, d=3, device_type='gpu', device_id=0)
                                for plane in planes[1:]]
        planes = inverse_scale_clip_array(planes, width, height, kernel, kerneluv, taps, a1, a2, invks)
        planes[0] = mvf.BM3D(planes[0], sigma=bm3d_sigma, radius1=1)
    else:
        planes = inverse_scale_clip_array(planes, width, height, kernel, kerneluv, taps, a1, a2, invks)
    scaled = plane_array_to_clip(planes)
    if denoise and not use_gpu:
        scaled = mvf.BM3D(scaled, radius1=1, sigma=bm3d_sigma)
    if mask_detail:
        mask = generate_mask(source, width, height, kernel, taps, a1, a2, mask_highpass)
        if masking_areas is None:
            scaled = apply_mask(source, scaled, mask)
        else:
            scaled = apply_mask_to_area(source, scaled, mask, masking_areas)
    return scaled


# the following 6 functions are mostly called from inside inverse_scale
def inverse_scale_clip_array(planes, w, h, kernel, kerneluv, taps, a1, a2, invks=True):
    if hasattr(core, 'descale') and invks:
        planes[0] = get_descale_filter(kernel, b=a1, c=a2, taps=taps)(planes[0], w, h)
    elif kernel == 'bilinear' and hasattr(core, 'unresize') and invks:
        planes[0] = core.unresize.Unresize(planes[0], w, h)
    else:
        planes[0] = core.fmtc.resample(planes[0], w, h, kernel=kernel, invks=invks, invkstaps=taps, a1=a1, a2=a2)
    planes[1], planes[2] = [core.fmtc.resample(plane, w, h, kernel=kerneluv, sx=0.25) for plane in planes[1:]]
    return planes


def clip_to_plane_array(clip):
    return [core.std.ShufflePlanes(clip, x, colorfamily=vs.GRAY) for x in range(clip.format.num_planes)]


def plane_array_to_clip(planes, family=vs.YUV):
    return core.std.ShufflePlanes(clips=planes, planes=[0]*len(planes), colorfamily=family)


def generate_mask(source, w=None, h=720, kernel='bilinear', taps=4, a1=0.15, a2=0.5, highpass=0.3, unresize=False):
    if w is None: w = getw(h)
    mask = mask_detail(source, w, h, kernel=kernel, taps=taps, invkstaps=taps, a1=a1, a2=a2, cutoff=highpass,
                       unresize=unresize)
    return mask


def apply_mask(source, scaled, mask):
    noalias = core.fmtc.resample(source, scaled.width, scaled.height, css=get_subsampling(scaled),
                                 kernel='blackmanminlobe', taps=5)
    masked = core.std.MaskedMerge(scaled, noalias, mask)
    return masked


def apply_mask_to_area(source, scaled, mask, area):
    if len(area) == 2 and isinstance(area[0], int):
        area = [[area[0], area[1]]]
    noalias = core.fmtc.resample(source, scaled.width, scaled.height, css=get_subsampling(scaled),
                                 kernel='blackmanminlobe', taps=5)
    for a in area:  # TODO: use ReplaceFrames
        source_cut = core.std.Trim(noalias, a[0], a[1])
        scaled_cut = core.std.Trim(scaled, a[0], a[1])
        mask_cut = core.std.Trim(mask, a[0], a[1])
        masked = apply_mask(source_cut, scaled_cut, mask_cut)
        scaled = insert_clip(scaled, masked, a[0])
    return scaled


# less typing == more time to encode
split = clip_to_plane_array
join = plane_array_to_clip


def getY(c: vs.VideoNode) -> vs.VideoNode:
    return core.std.ShufflePlanes(c, 0, vs.GRAY)


# TODO: currently, this should fail for non mod4 subsampled input.
# Not really relevant, though, as 480p, 576p, 720p, and 1080p are all mod32
def generate_keyframes(clip: vs.VideoNode, out_path=None) -> None:
    """
    probably only useful for fansubbing
    generates qp-filename for keyframes to simplify timing
    disclaimer: I don't actually know why -1 is forced. I just ported the avisynth script
    """
    import os
    clip = core.resize.Bilinear(clip, 640, 360)  # speed up the analysis by resizing first
    clip = core.wwxd.WWXD(clip)
    out_txt = ""
    for i in range(clip.num_frames):
        if clip.get_frame(i).props.Scenechange == 1:
            out_txt += "%d I -1\n" % i
        if i % 1000 == 0:
            print(i)
    if out_path is None:
        out_path = os.path.expanduser("~") + "/Desktop/keyframes.txt"
    text_file = open(out_path, "w")
    text_file.write(out_txt)
    text_file.close()


def adaptive_grain(clip: vs.VideoNode, strength=0.25, static=True, luma_scaling=12, mask_bits=8, show_mask=False) -> vs.VideoNode:
    """
    generates grain based on frame and pixel brightness.
    details can be found here: https://kageru.moe/article.php?p=adaptivegrain
    strength is the strength of the grain generated by AddGrain, static=True for static grain
    luma_scaling manipulates the grain alpha curve. Higher values will generate less grain (especially in brighter scenes)
    while lower values will generate more grain, even in brighter scenes
    Please note that 8 bit should be enough for the mask; 10, if you want to do everything in 10 bit.
    It is technically possible to set it to up to 16 (float does not work), but you won't gain anything.
    An 8 bit mask uses 1 MB of RAM, 10 bit need 4 MB, and 16 bit use 256 MB.
    Lookup times might also increase (they shouldn't, but you never know), as well as the initial generation time.
    """
    import numpy as np

    def fill_lut(y):
        """
        Using horner's method to compute this polynomial:
        (1 - (1.124 * x - 9.466 * x ** 2 + 36.624 * x ** 3 - 45.47 * x ** 4 + 18.188 * x ** 5)) ** ((y ** 2) * luma_scaling) * 255
        Using the normal polynomial is about 2.5x slower during the initial generation.
        I know it doesn't matter as it only saves a few ms (or seconds at most), but god damn, just let me have some fun here, will ya?
        Just truncating (rather than rounding) the array would also half the processing time,
        but that would decrease the precision and is also just unnecessary.
        """
        x = np.arange(0, 1, 1 / (1 << mask_bits))
        z = (1 - (x * (1.124 + x * (-9.466 + x * (36.624 + x * (-45.47 + x * 18.188)))))) ** ((y ** 2) * luma_scaling)
        if clip.format.sample_type == vs.INTEGER:
            z = z * ((1 << mask_bits) - 1)
            z = np.rint(z).astype(int)
        return z.tolist()

    def generate_mask(n, f, clip):
        frameluma = round(f.props.PlaneStatsAverage * 999)
        table = lut[int(frameluma)]
        return core.std.Lut(clip, lut=table)

    clip8 = fvf.Depth(clip, mask_bits)
    bits = clip.format.bits_per_sample

    lut = [None] * 1000
    for y in np.arange(0, 1, 0.001):
        lut[int(round(y * 1000))] = fill_lut(y)

    luma = core.std.ShufflePlanes(clip8, 0, vs.GRAY)
    luma = core.std.PlaneStats(luma)
    grained = core.grain.Add(clip, var=strength, constant=static)

    mask = core.std.FrameEval(luma, partial(generate_mask, clip=luma), prop_src=luma)
    mask = core.resize.Spline36(mask, clip.width, clip.height)

    if bits != mask_bits:
        mask = core.fmtc.bitdepth(mask, bits=bits, dmode=1)

    if show_mask:
        return mask

    return core.std.MaskedMerge(clip, grained, mask)


# TODO: implement blending zone in which both clips are merged to aviod abrupt and visible kernel changes.
def conditional_resize(src: vs.VideoNode, kernel='bilinear', w=1280, h=720, thr=0.00015, debug=False) -> vs.VideoNode:
    """
    Fix oversharpened upscales by comparing a regular downscale with a blurry bicubic kernel downscale.
    Similar to the avisynth function. thr is lower in vapoursynth because it's normalized (between 0 and 1)
    """

    def compare(n, down, os, diff_default, diff_os):
        error_default = diff_default.get_frame(n).props.PlaneStatsDiff
        error_os = diff_os.get_frame(n).props.PlaneStatsDiff
        if debug:
            debugstring = "error when scaling with {:s}: {:.5f}\nerror when scaling with bicubic (b=0, c=1): " \
                          "{:.5f}\nUsing debicubic OS: {:s}".format(kernel, error_default, error_os,
                                                                    str(error_default - thr > error_os))
            os = os.sub.Subtitle(debugstring)
            down = down.sub.Subtitle(debugstring)
        if error_default - thr > error_os:
            return os
        return down

    src_w, src_h = src.width, src.height

    if hasattr(core, 'descale'):
        down = get_descale_filter(kernel)(w, h)
        os = core.descale.Debicubic(w, h, b=0, c=1)
    else:
        down = src.fmtc.resample(w, h, kernel=kernel, invks=True)
        os = src.fmtc.resample(w, h, kernel='bicubic', a1=0, a2=1, invks=True)

    # we only need luma for the comparison
    up = core.std.ShufflePlanes([down], [0], vs.GRAY).fmtc.resample(src_w, src_h, kernel=kernel)
    os_up = core.std.ShufflePlanes([os], [0], vs.GRAY).fmtc.resample(src_w, src_h, kernel='bicubic', a1=0, a2=1)

    src_luma = core.std.ShufflePlanes([src], [0], vs.GRAY)
    diff_default = core.std.PlaneStats(up, src_luma)
    diff_os = core.std.PlaneStats(os_up, src_luma)

    return core.std.FrameEval(down,
                              partial(compare, down=down, os=os, diff_os=diff_os, diff_default=diff_default))


def retinex_edgemask(src: vs.VideoNode, sigma=1) -> vs.VideoNode:
    """
    Use retinex to greatly improve the accuracy of the edge detection in dark scenes.
    sigma is the sigma of tcanny
    """
    luma = mvf.GetPlane(src, 0)
    ret = core.retinex.MSRCP(luma, sigma=[50, 200, 350], upper_thr=0.005)
    mask = core.std.Expr([kirsch(luma), ret.tcanny.TCanny(mode=1, sigma=sigma).std.Minimum(
        coordinates=[1, 0, 1, 0, 0, 1, 0, 1])], 'x y +')
    return mask


def kirsch(src: vs.VideoNode) -> vs.VideoNode:
    """
    Kirsch edge detection. This uses 8 directions, so it's slower but better than Sobel (4 directions).
    more information: https://ddl.kageru.moe/konOJ.pdf
    """
    w = [5] * 3 + [-3] * 5
    weights = [w[-i:] + w[:-i] for i in range(4)]
    c = [core.std.Convolution(src, (w[:4] + [0] + w[4:]), saturate=False) for w in weights]
    return core.std.Expr(c, 'x y max z max a max')

def fast_sobel(src: vs.VideoNode) -> vs.VideoNode:
    """
    Should behave similar to std.Sobel() but faster since it has no additional high-/lowpass, gain, or the sqrt.
    The internal filter is also a little brighter
    """
    sx = src.std.Convolution([-1, -2, -1, 0, 0, 0, 1, 2, 1], saturate=False)
    sy = src.std.Convolution([-1, 0, 1, -2, 0, 2, -1, 0, 1], saturate=False)
    return core.std.Expr([sx, sy], 'x y max')


def get_descale_filter(kernel: str, **kwargs):
    """
    Stolen from a declined pull request.
    Originally written by @stuxcrystal on Github.
    """
    FILTERS = {
        'bilinear': (lambda **kwargs: core.descale.Debilinear),
        'spline16': (lambda **kwargs: core.descale.Despline16),
        'spline36': (lambda **kwargs: core.descale.Despline36),
        'bicubic': (lambda b, c, **kwargs: partial(core.descale.Debicubic, b=b, c=c)),
        'lanczos': (lambda taps, **kwargs: partial(core.descale.Delanczos, taps=taps)),
    }
    return FILTERS[kernel](**kwargs)


def hardsubmask(clip: vs.VideoNode, ref: vs.VideoNode, mode='default', expandN=None) -> vs.VideoNode:
    """
    Uses multiple techniques to mask the hardsubs in video streams like Anime on Demand or Wakanim.
    Might (should) work for other hardsubs, too, as long as the subs are somewhat close to black/white.
    It's kinda experimental, but I wanted to try something like this.
    It works by finding the edge of the subtitle (where the black border and the white fill color touch),
    and it grows these areas into a regular brightness + difference mask via hysteresis.
    This should (in theory) reliably find all hardsubs in the image with barely any false positives (or none at all).
    Output is 32bit float for mode default, input depth for mode fast
    """
    if expandN is None:
        expandN = clip.width // 200
    if mode in ['default', None]:

    def skip(n, f):
        if f.props.PlaneStatsMaximum == 0:
            return core.std.BlankClip(clip, format=vs.GRAYS, color=[0])
        else:
            subedge = core.std.Expr(c444, 'x y z min min')
            diff = core.std.Expr([getY(clip).std.Convolution([1]*9), getY(ref).std.Convolution([1]*9)], 'x 0.8 > x 0.2 < or x y - abs 0.1 > and 1 0 ?').std.Maximum().std.Maximum()
            mask = core.misc.Hysteresis(subedge, diff)
            mask = iterate(mask, core.std.Maximum, expandN)
            return mask.std.Inflate().std.Inflate().std.Convolution([1]*9)
                
        clip = fvf.Depth(clip, 32)
        ref = fvf.Depth(ref, 32)
        right = core.resize.Point(clip, src_left=4)    # right shift by 4 pixels
        subedge = core.std.Expr([clip, right], ['x y - abs 0.7 > 1 0 ?', 'x abs 0.1 < y abs 0.1 < and 1 0 ?'])
        c444 = split(subedge.resize.Bilinear(format=vs.YUV444PS))
        luma = c444[0].std.PlaneStats()
        mask = core.std.FrameEval()
        
    elif mode == 'fast':
        bits = clip.format.bits_per_sample
        clip, ref = getY(clip), getY(ref)
        edge = clip.std.Sobel()
        diff = core.std.Expr(clip, ref, 'x y - abs {:d} < 0 {:d} ?'.format(highpass << (bits-8), (1 << bits) - 1))
        mask = core.misc.Hysteresis(edge, diff)
        mask = iterate(mask, core.std.Maximum, expandN)
        mask = mask.std.Convolution([1]*9)
    else:
        raise ValueError('hardsubmask: Unknown mode')
    return mask

# TODO: add as mode to hardsubmask
def hardsubmask_fades(clip, ref, expandN=8, highpass=5000):
    """
    Uses Sobel edge detection to find edges that are only present in the main clip.
    These should (theoretically) be the subtitles.
    The video is blurred beforehand to prevent compression artifacts from being recognized as subtitles.
    This may create more false positives than the other hardsubmask,
    but it is capable of finding subtitles of any color and subtitles during fadein/fadeout.
    Setting highpass to a lower value may catch very slight changes (e.g. the last frame of a low-contrast fade),
    but it will make the mask more susceptible to artifacts.
    """
    clip = core.fmtc.bitdepth(clip, bits=16).std.Convolution([1]*9)
    ref = core.fmtc.bitdepth(ref, bits=16).std.Convolution([1]*9)
    clipedge = getY(clip).std.Sobel()
    refedge = getY(ref).std.Sobel()
    mask = core.std.Expr([clipedge, refedge], 'x y - {} < 0 65535 ?'.format(highpass)).std.Median()
    mask = iterate(mask, core.std.Maximum, expandN)
    mask = iterate(mask, core.std.Inflate, 4)
    return mask


def crossfade(clipa, clipb, duration):
    """
    Crossfade clipa into clipb. Duration is the length of the blending zone.
    For example, crossfade(a, b, 100) will fade the last 100 frames of a into b.
    """
    def fade_image(n, clipa, clipb):
        return core.std.Merge(clipa, clipb, weight=n/clipa.num_frames)
    # lol, >error handling
    if clipa.format.id != clipb.format.id or clipa.height != clipb.height or clipa.width != clipb.width:
        raise ValueError('Crossfade: Both clips must have the same dimensions and format.')
    fade = core.std.FrameEval(clipa[-duration:], partial(fade_image, clipa=clipa[-duration:], clipb=clipb[:duration]))
    return clipa[:-duration] + fade + clipb[duration:]


def hybriddenoise(src, knl=0.5, sigma=2, radius1=1):
    """
    denoise luma with BM3D (CPU-based) and chroma with KNLMeansCL (GPU-based)
    sigma = luma denoise strength
    knl = chroma denoise strength. The algorithm is different, so this value is different from sigma
    BM3D's sigma default is 5, KNL's is 1.2, to give you an idea of the order of magnitude
    radius1 = temporal radius of luma denoising, 0 for purely spatial denoising
    """
    planes = clip_to_plane_array(src)
    planes[0] = mvf.BM3D(planes[0], radius1=radius1, sigma=sigma)
    planes[1], planes[2] = [core.knlm.KNLMeansCL(plane, a=2, h=knl, d=3, device_type='gpu', device_id=0)
                            for plane in planes[1:]]
    return core.std.ShufflePlanes(clips=planes, planes=[0, 0, 0], colorfamily=vs.YUV)


def insert_clip(ep, op, startframe):
    """
    convenience function to insert things like Non-credit OP/ED into episodes
    """
    if startframe == 0:
        return op + ep[op.num_frames:]
    pre = ep[:startframe]
    if startframe + op.num_frames == ep.num_frames - 1:
        return pre + op
    post = ep[startframe + op.num_frames:]
    return pre + op + post


# helpers

def get_subsampling(src):
    """
    returns string to be used with fmtc.resample
    """
    if src.format.subsampling_w == 1 and src.format.subsampling_h == 1:
        css = '420'
    elif src.format.subsampling_w == 1 and src.format.subsampling_h == 0:
        css = '422'
    elif src.format.subsampling_w == 0 and src.format.subsampling_h == 0:
        css = '444'
    elif src.format.subsampling_w == 2 and src.format.subsampling_h == 2:
        css = '410'
    elif src.format.subsampling_w == 2 and src.format.subsampling_h == 0:
        css = '411'
    elif src.format.subsampling_w == 0 and src.format.subsampling_h == 1:
        css = '440'
    else:
        raise ValueError('Unknown subsampling')
    return css


def iterate(base, filter, count):
    for _ in range(count):
        base = filter(base)
    return base


def is16bit(clip):
    """
    returns bool. Yes, I was lazy enough to write a function that saves ~20 characters
    """
    return clip.format.bits_per_sample == 16


def getw(h, ar=16 / 9, only_even=True):
    """
    returns width for image
    """
    w = h * ar
    w = int(round(w))
    if only_even:
        w = w // 2 * 2
    return w


def shiftl(x, bits):
    return x << bits if bits >= 0 else x >> -bits


def fit_subsampling(x, sub):
    """
    Makes a value (e.g. resolution or crop value) compatible with the specified subsampling.
    sub is given by the properties (clip.format.subsampling_w/_h)
    The number is then truncated to be a compatible resolution.
    """
    return (x >> bits) << bits
    #return x & (0xffffffff - 1 << sub -1);


# TODO: some more clean-up
def mask_detail(startclip, final_width, final_height, cutoff=16384, kernel='bilinear', invkstaps=4, taps=4, a1=0.15,
                a2=0.5):
    """
    Credits to MonoS @github: https://github.com/MonoS/VS-MaskDetail
    His version is not compatible with the new name spaces of vapoursynth R33+, so I included this 'fixed' version here
    I also removed all features and subfunctions that are not used by inverse_scale
    """
    def luma16(x):
        x <<= 4
        value = x & 0xFFFF
        return 0xFFFF - value if x & 0x10000 else value

    def f16(x):
        if x < cutoff:
            return 0

        result = x * 0.75 * (0x10000 + x) / 0x10000
        return min(0xFFFF, int(result))

    original = (startclip.width, startclip.height)
    target = (final_width, final_height, 0, 0, 0, 0)

    if kernel == 'bilinear' and hasattr(core, 'unresize'):
        temp = core.unresize.Unresize(startclip, *target[:2])
    else:
        temp = core.fmtc.resample(startclip, *target[:2], kernel=kernel,
                                  invks=True, invkstaps=invkstaps, taps=taps, a1=a1, a2=a2)
    temp = core.fmtc.resample(temp, *original, kernel=kernel, taps=taps, a1=a1, a2=a2)
    diff = core.std.MakeDiff(startclip, temp, 0)

    mask = core.std.Lut(diff, function=luma16).rgvs.RemoveGrain(mode=[3])
    mask = core.std.Lut(mask, function=f16)

    for i in range(4):
        mask = core.std.Maximum(mask, planes=[0])
    mask = core.std.Inflate(mask, planes=[0])

    mask = core.fmtc.resample(mask, *target, taps=taps)

    mask = core.std.ShufflePlanes(mask, planes=0, colorfamily=vs.GRAY)
    return core.fmtc.bitdepth(mask, bits=16, dmode=1)
