""" scoll.py +++ Script Collection for VapourSynth: ++++++++++++++++++++++++++++++++++++++++++++++
"""
import vapoursynth as vs
try:
    import havsfunc as haf
except:
    HAS_HAF = False
else:
    HAS_HAF = True
try:
    import vshelpers as vsh
except:
    raise ImportError('You need to install vshelpers module.')

""" misc /////////////////////////////////////////////////////////////////////////////////////////
"""


def ssaa(clip, thrmask=40, aamode=0, ssmode=1, mmode=2, sharpen=False, smask=False):
    """
    ssaa +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        Small antialiasing function for 1080p. Input must be vs.YUV420P8 or GRAY8.

        ssaa(clip, th_mask=11, sharpen=False, smask=False)
            th_mask: The lower the threshold, more pixels will be antialiased.
            aamode:  Antialiasing metoth: 0: SangNom; 1: nnedi3; 2: RemoveGrain.
            ssmode:  Supersampling metoth: 0:Spline36; 1: nnedi3_rpow2, 2: point
            sharpen: Performs contra-sharpening on the antialiased zones.
            smask:   Shows the zones antialiasing will be applied.

        Dependencies:
            SangNomMod
            Repair
            RemoveGrain
            fmtconv
            nnedi3

        Todo:
            - Make it work on 16bit mode when aviable.

        Changelog:
            3.0     Added RemoveGrain aamode and nnedi3 ssmode.
            2.0     Adapted to use native repair.
                Memory/speed optimizations.
            1.0     Initial release.
    """
    core = vs.get_core()

    fw = clip.width
    fh = clip.height

    if clip.format.num_planes > 1:
        if clip.format.color_family != vs.YUV:
            raise ValueError('Input video format should be 8 bits YUV or GRAY8.')
        else:
            clipl = vsh.get_luma(clip)
    else:
        clipl = clip

    cluma = core.rgvs.RemoveGrain(clipl, 1)
    if thrmask > 0:
        mask = vsh.build_mask(c=cluma, edgelvl=thrmask, mode=mmode)

    # Super Sampling
    if ssmode == 0:
        aac = core.fmtc.resample(clip=cluma, w=fw*2, h=fh*2)
        if aac.format.bits_per_sample != clip.format.bits_per_sample:
            aac = core.fmtc.bitdepth(aac, bits=clip.format.bits_per_sample)
    elif ssmode == 1:
        aac = core.nnedi3.nnedi3_rpow2(clip=cluma, rfactor=2, correct_shift=1, qual=2)
    elif ssmode == 2:
        aac = core.fmtc.resample(clip=cluma, kernel='point', w=fw*2, h=fh*2)
        if aac.format.bits_per_sample != clip.format.bits_per_sample:
            aac = core.fmtc.bitdepth(aac, bits=clip.format.bits_per_sample)
    else:
        raise ValueError('Wrong ssmode, it should be 0 (fmtc), 1 (nnedi3_rpow2) or 2 (point).')

    # Antialiasing
    if aamode == 0:
        aac = core.std.Transpose(core.sangnom.SangNomMod(clip=aac, aa=255, aac=-1))
        aac = core.std.Transpose(core.sangnom.SangNomMod(clip=aac, aa=255, aac=-1))
    elif aamode == 1:
        aac = core.std.Transpose(core.nnedi3.nnedi3(clip=aac, field=0, nns=2))
        aac = core.std.Transpose(core.nnedi3.nnedi3(clip=aac, field=0, nns=2))
    elif aamode == 2:
        aac = core.rgvs.RemoveGrain(aac, 5).rgvs.RemoveGrain(21).rgvs.RemoveGrain(19)
    elif aamode == 3:
        aac = core.rgvs.RemoveGrain(aac, 5).rgvs.RemoveGrain(21).rgvs.RemoveGrain(19).std.Transpose()
        aac = core.rgvs.RemoveGrain(aac, 5).rgvs.RemoveGrain(21).rgvs.RemoveGrain(19).std.Transpose()
    else:
        raise ValueError('Wrong aamode, it should be 0 (SangNomMod), 1 (nnedi3), 2 or 3 (RemoveGrain).')

    aac = core.fmtc.resample(clip=aac, w=fw, h=fh)
    if aac.format.bits_per_sample != clip.format.bits_per_sample:
        aac = core.fmtc.bitdepth(aac, bits=clip.format.bits_per_sample)

    if aamode == 2 or aamode == 3:
        aac = core.rgvs.RemoveGrain(aac, 22)

    # Sharpening
    if sharpen is True:
        aaD = core.std.MakeDiff(cluma, aac)
        shrpD = core.std.MakeDiff(aac, core.rgvs.RemoveGrain(aac, 20))
        DD = core.rgvs.Repair(clip=shrpD, repairclip=aaD, mode=13)
        aac = core.std.MergeDiff(aac, DD)

    # Merge chroma
    if smask is True and thrmask > 0:
        return mask
    else:
        if thrmask > 0:
            last = core.std.MaskedMerge(cluma, aac, mask, planes=0)
        else:
            last = aac

        if clip.format.num_planes > 1:
            last = vsh.merge_chroma(last, clip)

    return last


def nediaa(c, pm=2):
    """
    nediAA - antialiasing function using nnedi3 ++++++++++++++++++++++++++++++
        pm: parity mode, should be 2 or 3.
    """
    core = vs.get_core()

    pm = vsh.clamp(2, pm, 3)

    ret = core.nnedi3.nnedi3(c, field=pm)
    ret = core.std.Merge(ret[::2], ret[1::2])

    return ret


def naa(c, ss=2, chroma=False):
    """
    naa - antialiasing function using nnedi3 +++++++++++++++++++++++++++++++++
        ss: supersampling value, must be even.
        cp: if false chroma will not be altered.
    """
    core = vs.get_core()

    if ss % 2 != 0:
        raise ValueError('ss must be an even number.')

    src = c

    if chroma is False:
        c = vsh.get_luma(c)

    if c.format.bits_per_sample > 8:
        fapprox = 12
    else:
        fapprox = 7

    ret = core.nnedi3.nnedi3_rpow2(clip=c, rfactor=ss, correct_shift=1, qual=2, fapprox=fapprox, nsize=6)
    ret = core.nnedi3.nnedi3(clip=ret, field=0, nns=2, fapprox=fapprox, nsize=6)
    ret = core.std.Transpose(ret)
    ret = core.nnedi3.nnedi3(clip=ret, field=0, nns=2, fapprox=fapprox, nsize=6)
    ret = core.std.Transpose(ret)
    ret = core.fmtc.resample(ret, c.width, c.height)

    if ret.format.bits_per_sample != c.format.bits_per_sample:
        ret = core.fmtc.bitdepth(ret, bits=c.format.bits_per_sample)

    if chroma is False:
        ret = vsh.merge_chroma(ret, src)

    return ret


def daa3mod(src):
    """ From: http://forum.doom9.org/showthread.php?p=1639679#post1639679
    """
    core = vs.get_core()

    clip = core.resize.Spline36(src, src.width, vsh.m4(src.height*3/2))
    nn = core.nnedi3.nnedi3(clip, field=-2)
    dbl = core.std.Merge(nn[::2], nn[1::2])
    dblD = core.std.MakeDiff(clip, dbl)
    shrpD = core.std.MakeDiff(dbl, core.rgvs.RemoveGrain(dbl, 20 if clip.width > 1100 else 11))
    DD = core.rgvs.Repair(shrpD, dblD, 13)
    res = core.std.MergeDiff(dbl, DD).resize.Spline36(src.width, src.height)

    return res


def mcdaa3(src, csaa=None):
    """ From: http://forum.doom9.org/showthread.php?p=1639679#post1639679
    """
    core = vs.get_core()

    sup = core.mv.Super(src, pel=2, sharp=1)  # HQdn3d(src).FFT3DFilter().MSuper(pel=2, sharp=1) FIXME
    fv = core.mv.Analyse(sup, isb=False, delta=1, dct=2, truemotion=False)
    bv = core.mv.Analyse(sup, isb=True, delta=1, dct=2, truemotion=True)
    if csaa is None:
        csaa = daa3mod(src)
    momask1 = core.mv.Mask(src, fv, kind=1, ml=2)
    momask2 = core.mv.Mask(src, bv, kind=1, ml=3)
    momask = core.std.Merge(momask1, momask2)
    res = core.std.MaskedMerge(src, csaa, momask)

    return None


def edgecleaner(src, strength=8, smode=0, rmode=17, rep=True, hot=False):
    """ edgecleaner.py (2013-12-23)
    A simple edge cleaning and weak dehaloing function ported to vapoursynth. Ported from:
    http://pastebin.com/7TCR7W4x

    edgecleaner(src, strength=16, rep=True, rmode=17, smode=0, hot=False)
            strength (float)      - specifies edge denoising strength (8.0)
            rep (boolean)         - actives Repair for the aWarpSharped clip (true; requires Repair).
            rmode (integer)       - specifies the Repair mode; 1 is very mild and good for halos,
                                    16 and 18 are good for edge structure preserval
                                    on strong settings but keep more halos and edge noise,
                                    17 is similar to 16 but keeps much less haloing,
                                    other modes are not recommended (17; requires Repair).
            smode (integer)       - specifies what method will be used for finding small particles,
                                    ie stars; 0 is disabled, 1 uses RemoveGrain and 2 uses Deen
                                    (0; requires RemoveGrain/Repair/Deen).
            hot (boolean)         - specifies whether removal of hot pixels should take place (false).

    Dependencies:
                RemoveGrain (vs)
                GeneritFilters (vs)
                MaskTools2 (avs)
                deen (avs)
                aWarpSharp2 (avs)
    """
    core = vs.get_core()

    smode = vsh.clamp(0, smode, 2)

    if src.format.id != vs.YUV420P8:
        raise ValueError('Input video format should be YUV420P8.')

    if smode != 0:
        strength = strength + 2

    main = core.avs.aWarpSharp2(src, 128, 1, 0, strength)

    if rep is True:
        main = core.rgvs.Repair(main, src, rmode)

    mask = core.std.Prewitt(clip=src, min=4, max=32).std.Invert()
    mask = core.std.Convolution(clip=mask, matrix=[1, 1, 1, 1, 1, 1, 1, 1, 1])

    final = core.std.MaskedMerge(src, main, mask, planes=0)

    if hot is True:
        final = core.rgvs.Repair(final, src, 2)

    if smode != 0:
        stmask = vsh.starmask(src, smode)
        final = core.std.MaskedMerge(final, src, stmask)

    return final


def ezydegrain(src, tr=3, thsad=250, blksize=None, overlap=None, pel=None, limit=None, recalc=False, plane=4):
    core = vs.get_core()

    # Vars

    if blksize is None:
        if src.width < 1280 or src.height < 720:
            blksize = 8
        elif src.width >= 3840 or src.height >= 2160:
            blksize = 32
        else:
            blksize = 16

    if overlap is None:
        overlap = blksize // 2

    if pel is None:
        if src.width < 1280 or src.height < 720:
            pel = 2
        else:
            pel = 1

    if limit is None:
        limit = 2**src.format.bits_per_sample-1

    # Cheks

    if tr not in [1, 2, 3]:
        raise ValueError('tr must be 1, 2 or 3.')

    # Stuff

    last = src

    super_ = core.mv.Super(last, pel=pel, sharp=2, rfilter=4)

    mvbw3 = core.mv.Analyse(super_, isb=True, delta=3, overlap=overlap, blksize=blksize)
    mvbw2 = core.mv.Analyse(super_, isb=True, delta=2, overlap=overlap, blksize=blksize)
    mvbw1 = core.mv.Analyse(super_, isb=True, delta=1, overlap=overlap, blksize=blksize)
    mvfw1 = core.mv.Analyse(super_, isb=False, delta=1, overlap=overlap, blksize=blksize)
    mvfw2 = core.mv.Analyse(super_, isb=False, delta=2, overlap=overlap, blksize=blksize)
    mvfw3 = core.mv.Analyse(super_, isb=False, delta=3, overlap=overlap, blksize=blksize)

    if recalc is True:
        hoverlap = overlap // 2
        hblksize = blksize // 2
        hthsad = thsad // 2

        prefilt = core.rgvs.RemoveGrain(last, 4)
        super_r = core.mv.Super(prefilt, pel=pel, sharp=2, rfilter=4)

        mvbw3 = core.mv.Recalculate(super_r, mvbw3, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
        mvbw2 = core.mv.Recalculate(super_r, mvbw2, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
        mvbw1 = core.mv.Recalculate(super_r, mvbw1, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
        mvfw1 = core.mv.Recalculate(super_r, mvfw1, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
        mvfw2 = core.mv.Recalculate(super_r, mvfw2, overlap=hoverlap, blksize=hblksize, thsad=hthsad)
        mvfw3 = core.mv.Recalculate(super_r, mvfw3, overlap=hoverlap, blksize=hblksize, thsad=hthsad)

    if tr == 1:
        last = core.mv.Degrain1(clip=last, super=super_,
                                mvbw=mvbw1, mvfw=mvfw1, thsad=thsad, plane=plane)
    elif tr == 2:
        last = core.mv.Degrain2(clip=last, super=super_,
                                mvbw=mvbw1, mvfw=mvfw1, mvbw2=mvbw2, mvfw2=mvfw2,
                                thsad=thsad, plane=plane)
    elif tr == 3:
        last = core.mv.Degrain3(clip=last, super=super_,
                                mvbw=mvbw1, mvfw=mvfw1, mvbw2=mvbw2,
                                mvfw2=mvfw2, mvbw3=mvbw3, mvfw3=mvfw3,
                                thsad=thsad, plane=plane)

    return last


def removedirt(c, repmode=16):
    core = vs.get_core()

    if c.format.num_planes > 1:
        repmodes = [repmode, repmode, 1]
        greymode = 0
    else:
        repmodes = [repmode]
        greymode = 1

    cleansed = core.rgvs.Clense(c)
    sbegin = core.rgvs.ForwardClense(c)
    send = core.rgvs.BackwardClense(c)
    scenechange = core.rdvs.SCSelect(c, sbegin, send, cleansed)
    alt = core.rgvs.Repair(clip=scenechange, repairclip=c, mode=repmodes)
    restore = core.rgvs.Repair(clip=cleansed, repairclip=c, mode=repmodes)
    corrected = core.rdvs.RestoreMotionBlocks(cleansed, restore, neighbour=c, alternative=alt,
                                              gmthreshold=70, dist=1, dmode=2, noise=10, noisy=12,
                                              grey=greymode)

    return core.rgvs.RemoveGrain(corrected, mode=[17, 17, 1])


def unsharpmask(clip, strength=1.0, repair=False, repmode=16):
    core = vs.get_core()

    blur_clip = core.generic.GBlur(clip, sigma=strength, planes=[0])
    sharp_clip = core.std.Expr([clip, blur_clip], ['x x + y -', ''])

    if repair is True:
        rclip = core.rgvs.Repair(clip=sharp_clip, repairclip=clip, mode=repmode)
    else:
        rclip = sharp_clip

    return rclip


def detailsharpen(clip, sstr=1.01, estr=10, ethr=5, repair=False, rmode=12):
    core = vs.get_core()

    bd = clip.format.bits_per_sample
    max_ = 2 ** bd - 1
    mid = (max_ + 1) // 2
    scl = (max_ + 1) // 256

    src = clip
    clip = vsh.get_luma(clip)
    blur = core.rgvs.RemoveGrain(clip, 20)

    # "x y == x x x y - abs 0.25 ^ 4.24 * x y - 2 ^ x y - 2 ^ 2 + / * x y - x y - abs / * 1 x y - abs 16 / 4 ^ + / + ?"
    # "x x y - abs 0.25 ^ 4.24 * x y - x y - abs 2 + / * +"
    # 'x x y - abs 4 / 1 4 / ^ 4 * 1.5 * x y - x y - abs 2 + / * +'
    # 'x x y - abs 1 4 / ^ 2.83 * 1.5 * x y - x y - abs 2 + / * +'
    # expr = 'x x y - 1 x y - 16 / 4 ^ + / +'
    expr = '{x} {x} {y} - abs 4 / log 0.25 * exp 4 * {st} * {x} {y} - {x} {y} - abs 1.001 + / * + {sc}'.format(
           x='x {} /'.format(scl) if bd != 8 else 'x',
           y='y {} /'.format(scl) if bd != 8 else 'y',
           sc='{} *'.format(scl) if bd != 8 else '',
           st=sstr)

    clip = core.std.Expr([clip, blur], [expr])

    if estr > 0:
        tmp = clip
        clip = core.msmoosh.MSharpen(clip, threshold=ethr, strength=estr)
        if repair is True:
            clip = core.rgvs.Repair(clip=clip, repairclip=tmp, mode=rmode)

    clip = vsh.merge_chroma(clip, src)

    return clip


def assrenderwrapper(clip, data, charset=None, debuglevel=None, fontdir=None, linespacing=None,
                     margins=None, sar=None, scale=None):
    core = vs.get_core()

    subs = core.assvapour.AssRender(clip=clip, data=data, charset=charset, debuglevel=debuglevel,
                                    fontdir=fontdir, linespacing=linespacing, margins=margins, sar=sar,
                                    scale=scale)
    subs[0] = core.resize.Bicubic(subs[0], format=clip.format.id)
    subs[1] = core.resize.Bicubic(subs[1], format=clip.format.id)

    return core.std.MaskedMerge(clipa=clip, clipb=subs[0], mask=subs[1])


def subtitlewrapper(clip, text, debuglevel=None, fontdir=None, linespacing=None, margins=None,
                    sar=None, style=None):
    core = vs.get_core()

    subs = core.assvapour.Subtitle(clip=clip, text=text, debuglevel=debuglevel, fontdir=fontdir,
                                   linespacing=linespacing, margins=margins, sar=sar, style=style)
    subs[0] = core.resize.Bicubic(subs[0], format=clip.format.id)
    subs[1] = core.resize.Bicubic(subs[1], format=clip.format.id)

    return core.std.MaskedMerge(clipa=clip, clipb=subs[0], mask=subs[1])


def resamplehq(src, width=None, height=None, kernel="spline36", srcmatrix="709", dstmatrix=None,
               src_left=0, src_top=0, src_width=0, src_height=0, noring=False, sigmoid=False, dither=True):
    core = vs.get_core()

    # Var stuff

    clip = src

    if dstmatrix is None:
        dstmatrix = srcmatrix

    if src.format.bits_per_sample != 16:
        clip = core.fmtc.bitdepth(clip=clip, bits=16)
    tid = clip.format.id

    # Convert to RGB

    if src.format.color_family != vs.RGB:
        clip = core.fmtc.resample(clip=clip, css="444")
        clip = core.fmtc.matrix(clip=clip, mat=srcmatrix, col_fam=vs.RGB)

    # Do stuff

    clip = haf.GammaToLinear(clip, sigmoid=sigmoid)
    clip = haf.Resize(clip, w=width, h=height, kernel=kernel, noring=noring,
                      sx=src_left, sy=src_top, sw=src_width, sh=src_height)
    clip = haf.LinearToGamma(clip, sigmoid=sigmoid)

    # Back to original format

    if src.format.color_family != vs.RGB:
        clip = core.fmtc.matrix(clip=clip, mat=dstmatrix, col_fam=src.format.color_family)
        clip = core.fmtc.resample(clip=clip, csp=tid)

    # Dither as needed

    if dither is True and src.format.bits_per_sample != 16:
        clip = core.fmtc.bitdepth(clip=clip, bits=src.format.bits_per_sample)

    return clip


""" rangeutils ///////////////////////////////////////////////////////////////////////////////////
"""


def replace_range(clip1, clip2, start, end=None):
    """ Replaces a range of frames of a clip with the same range of
    frames from another clip.
    If no end frame is given, it will only replace the start frame.
    """
    core = vs.get_core()

    if end is None:
        end = start

    if start < 0 or start > clip1.num_frames - 1:
        raise ValueError('start frame out of bounds: {}.'.format(start))
    if end < start or end > clip1.num_frames - 1:
        raise ValueError('end frame out of bounds: {}.'.format(end))

    if start > 0:
        temp = 'core.std.Trim(clip1, 0, start - 1) + '
    else:
        temp = ''
    temp += 'core.std.Trim(clip2, start, end)'
    if end < clip1.num_frames - 1:
        temp += '+ core.std.Trim(clip1, end + 1)'

    final = eval(temp)

    if clip1.num_frames != final.num_frames:
        raise ValueError('input / output framecount missmatch (got: {}; expected: {}).'
                         .format(final.num_frames, clip1.num_frames))

    return final


def delete_range(src, start, end=None):
    """ Deletes a range of frames from a clip.
    If no end frame is given, it will only delete the start frame.
    """
    core = vs.get_core()

    if end is None:
        end = start

    if start < 0 or start > src.num_frames - 1:
        raise ValueError('start frame out of bounds: {}.'.format(start))
    if end < start or end > src.num_frames - 1:
        raise ValueError('end frame out of bounds: {}.'.format(end))

    if start != 0:
        final = src[:start]
        if end < src.num_frames - 1:
            final = final + src[end + 1:]
    else:
        final = src[end + 1:]

    if src.num_frames != final.num_frames + (end - start + 1):
        raise ValueError('output expected framecount missmatch.')

    return final


def freeze_loop(src, start, end, loopStart, loopEnd=None):
    """ Freezes a range of frames form start to end using the frames
    comprended between loopStart and loopEnd.
    If no end frames are provided for the range or the loop,
    start frames will be used instead.
    """
    core = vs.get_core()

    if loopEnd is None:
        loopEnd = loopStart

    if start < 0 or start > src.num_frames - 1:
        raise ValueError('start frame out of bounds: {}.'.format(start))
    if loopStart < 0 or loopStart > src.num_frames - 1:
        raise ValueError('loop start frame out of bounds: {}.'.format(loopStart))
    if end < start or end > src.num_frames - 1:
        raise ValueError('end frame out of bounds: {}.'.format(end))
    if loopEnd < loopStart or loopEnd > src.num_frames - 1:
        raise ValueError('loop end out of bounds: {}.'.format(loopEnd))

    loop = core.std.Loop(src[loopStart:loopEnd + 1], 0)

    span = end - start + 1

    if start != 0:
        final = src[:start] + loop[:span]
    else:
        final = loop[:span]
    if end < src.num_frames - 1:
        final = final + src[end + 1:]

    if src.num_frames != final.num_frames:
        raise ValueError(
            'input / output framecount missmatch (got: {}; expected: {}).'.format(
                final.num_frames, src.num_frames))

    return final


def blank_it(src, start, end=None, color='black'):
    """ Blanks a range of frames in a clip, by default to pure balck.
    If no endframe is provided start frame will be used.
    """
    core = vs.get_core()

    if end is None:
        end = start

    e = core.std.BlankClip(src, color=color)

    if start != 0:
        z = src[:start] + e[start:end + 1]
    else:
        z = e[start:end + 1]
    if end < src.num_frames - 1:
        z = z + src[end + 1:]

    if src.num_frames != z.num_frames:
        raise ValueError(
            'input / output framecount missmatch (got: {}; expected: {}).'.format(
                z.num_frames, src.num_frames))

    return z


def mkvcut(c, frag_tot, frag_req, base_name='frag', debug=False):
    """ mkvcut +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Description:
        Given a lossless video and an arbitrary number of segments of the same
        compresed video, it returns the selected segemnt from the lossless video.

    Dep:
        l-smash-works
    Use:
        mkvcut (lossless, frag_tot, frag_req, <base_name>)
        mkvcomp (losless, video_final)

    Options:
        frag_tot (-)
            Número de fragmentos totales en los que está partido el vídeo
            (mediante mkvmerge).

        frag_req (-)
            Fragmento que se desea reencodear.

        base_name ("frag")
            Nombre que se les dio a los fragmentos a la hora de cortarlos.
            También se puede especificar aquí una ruta alternativa si estos
            no se encuentran en el mismo directorio que el script.

    Examples:
        mkvcut(clip, 3, 1)
        mkvcut(clip, 3, 2, "another_name")
        mkvcut(clip, 7, 2, "another_dir/another_name")
    """
    core = vs.get_core()

    a = p = None

    vsource = vsh.get_decoder()

    if frag_req > frag_tot:
        raise AssertionError(
            'Requested fragment is out of range (req: {} tot: {}).'.format(frag_req, frag_tot))

    for i in range(1, frag_req):
        tmp = vsource(source=r'%s-%03d.mkv' % (base_name, i))
        if a is None:
            a = tmp
        else:
            a = a + tmp

    for i in range(frag_req+1, frag_tot+1):
        tmp = vsource(source=r'%s-%03d.mkv' % (base_name, i))
        if p is None:
            p = tmp
        else:
            p = p + tmp

    if c is not None:
        c_len = c.num_frames
    else:
        c_len = 0
    a_len = a.num_frames
    if p is not None:
        p_len = p.num_frames
    else:
        p_len = 0

    r = core.std.Trim(clip=c, first=a_len, last=(c_len-p_len)-1)

    if c_len != a_len + r.num_frames + p_len:
        raise AssertionError(
            'Internal error: source video and returned video number of frames missmatch.')
    if c.fps_num != r.fps_num or c.fps_den != r.fps_den:
        raise AssertionError(
            'Internal error: source video and returned video frame rate missmatch.')

    if debug:
        r = core.text.ClipInfo(clip=r)

    return r


def mkv_comp(c, a):
    core = vs.get_core()
    w2 = int(c.width/2)
    h2 = int(c.height/2)

    vsource = vsh.get_decoder()

    try:
        a = vsource(clip=r'{}'.format(a))
    except:
        a = a

    org = core.resize.Point(clip=c, width=w2, height=h2).text.ClipInfo().text.FrameNum(alignment=9)
    new = core.resize.Point(clip=a, width=w2, height=h2).text.ClipInfo().text.FrameNum(alignment=9)

    return core.std.StackHorizontal(clips=[org, new])


def overlay(c1, c2, x=0, y=0, mask=None, opacity=1.0, mode='blend', processing=None, matrix=None):
    """ TODO
            - check x, y offsets logic against avisynth ones.
    """
    core = vs.get_core()

    bd = c1.format.bits_per_sample
    max_ = (2 ** bd) - 1

    if matrix is None:
        matrix = '709'

    mode = mode.lower()
    modes = [
        'blend',
        'add',
        'substract',
        'difference',
        'multiply',
        'divide',
        'lighten',
        'darken'
        ]

    if mode not in modes:
        raise ValueError('"{}" is not a valid mode (valid modes: {}).'.format(mode, ', '.join(modes)))

    if mask is None:
        if isinstance(c2, list):
            clipb = c2[0]
            mask = c2[1]
        else:
            raise TypeError('No alpha clip supplied via "c2" or "mask" parameter.')
    else:
        clipb = c2
        mask = mask

    if c1.format.id != clipb.format.id:
        raise TypeError('Both clips should be in the same format.')

    clipa = c1
    clipb = vsh.fit(clipa, clipb)
    mask = vsh.fit(clipa, mask)

    if clipa.num_frames > clipb.num_frames:
        clipb = core.std.DuplicateFrames(clip=clipb,
                                         frames=[clipb.num_frames-1] * (clipa.num_frames-clipb.num_frames))
    if clipa.num_frames > mask.num_frames:
        mask = core.std.DuplicateFrames(clip=mask,
                                        frames=[mask.num_frames-1] * (clipa.num_frames-mask.num_frames))

    if x != 0 or y != 0:
        clips = vsh.move([clipb, mask], x, y)
        clipb = clips[0]
        mask = clips[1]

    if processing is not None:
        processing = processing.lower()
        if processing == 'yuv':
            if clipa.format.color_family != vs.YUV:
                clipa = core.fmtc.resample(clipa, kernel="lanczos", css="444")
                clipb = core.fmtc.resample(clipb, kernel="lanczos", css="444")
                clipa = core.fmtc.matrix(clipa, mat=matrix, col_fam=vs.YUV)
                clipb = core.fmtc.matrix(clipb, mat=matrix, col_fam=vs.YUV)

        elif processing == 'rgb':
            if clipa.format.color_family != vs.RGB:
                clipa = core.fmtc.resample(clipa, kernel="lanczos", css="444")
                clipb = core.fmtc.resample(clipb, kernel="lanczos", css="444")
                clipa = core.fmtc.matrix(clipa, mat=matrix, col_fam=vs.RGB)
                clipb = core.fmtc.matrix(clipb, mat=matrix, col_fam=vs.RGB)

        else:
            raise ValueError('Unsuported processing mode ("rgb" or "yuv", got: "{}").'.format(processing))

        if clipb.format.bits_per_sample != mask.format.bits_per_sample:
            mask = core.fmtc.bitdepth(mask, bits=clipb.format.bits_per_sample)

    merg = core.std.MaskedMerge(clipa=clipb, clipb=clipa, mask=mask)

    if mode != 'blend':
        if mode == 'add':
            merg = core.std.Expr(clips=[clipa, merg], expr=['x y + 255 min'.format(max_)])
            merg = core.std.MaskedMerge(clipa=merg, clipb=clipa, mask=mask)
        elif mode == 'substract':
            merg = core.std.Expr(clips=[clipa, merg], expr=['x y - 0 max'])
            merg = core.std.MaskedMerge(clipa=merg, clipb=clipa, mask=mask)
        elif mode == 'difference':
            merg = core.std.Expr(clips=[clipa, merg], expr=['x y - abs'])
            merg = core.std.MaskedMerge(clipa=merg, clipb=clipa, mask=mask)
        elif mode == 'multiply':
            merg = core.std.Expr(clips=[clipa, merg], expr=['x y * {} /'.format(max_)])
            merg = core.std.MaskedMerge(clipa=merg, clipb=clipa, mask=mask)
        elif mode == 'divide':
            merg = core.std.Expr(clips=[clipa, merg], expr=['{} x * y 1 + /'.format(max_ + 1)])
            merg = core.std.MaskedMerge(clipa=merg, clipb=clipa, mask=mask)
        elif mode == 'lighten':
            merg = core.std.Expr(clips=[clipa, merg], expr=['x y max'])
            merg = core.std.MaskedMerge(clipa=merg, clipb=clipa, mask=mask)
        elif mode == 'darken':
            merg = core.std.Expr(clips=[clipa, merg], expr=['x y min'])
            merg = core.std.MaskedMerge(clipa=merg, clipb=clipa, mask=mask)

    if opacity != 1:
        merg = core.std.Merge(clipa=clipa, clipb=merg, weight=opacity)

    return merg


def insertsign(src, ovr, start, end=None, x=0, y=0, opacity=1.0):
    """ insertsign  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        Description: Inserts an alpha video at the selected frames.
        Options:
                src:     base video.
                ovr:     overlayed video, this should be a list with the overlayed video and an alpha mask.
                start:   frame at the one the overlay will start.
                end:     frame at the one the overlay will end.
                x:       move the overlay video in the x axis, accepts negative and positive values.
                y:       move the overlay video in the y axis, accepts negative and positive values.
                opacity: blends the overlay video by the specified amount.
    """
    core = vs.get_core()

    if end is None:
        end = start + ovr[0].num_frames - 1
    if end >= src.num_frames:
        end = src.num_frames - 1

    if src.num_frames < end:
        raise ValueError('Out of bounds requested end frame (requested: {}; last frame: {}).'.format(
                         end, src.num_frames))

    e = overlay(c1=src[start:end + 1], c2=ovr[0], mask=ovr[1], x=x, y=y, opacity=opacity)

    if start != 0:
        z = src[:start] + e
    else:
        z = e
    if end < src.num_frames - 1:
        z = z + src[end + 1:]

    if src.num_frames != z.num_frames:
        raise ValueError('input / output framecount missmatch (got: {}; expected: {}).'.format(
                         z.num_frames, src.num_frames))
    return z
