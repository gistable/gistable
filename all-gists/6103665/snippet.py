#finesharp.py - finesharp module for VapourSynth
#original author : Didee　(http://forum.doom9.org/showthread.php?t=166082)

# requirement: RemoveGrain.dll, Repair.dll
#              VapourSynth r19 or later

import vapoursynth as vs

class InvalidArgument(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def spline(x, coordinates):
    def get_matrix(px, py, l):
        matrix = []
        matrix.append([(i == 0) * 1.0 for i in range(l + 1)])
        for i in range(1, l - 1):
            p = [0 for t in range(l + 1)]
            p[i - 1] = px[i] - px[i - 1]
            p[i] = 2 * (px[i + 1] - px[i - 1])
            p[i + 1] = px[i + 1] - px[i]
            p[l] = 6 * (((py[i + 1] - py[i]) / p[i + 1]) - (py[i] - py[i - 1]) / p[i - 1])
            matrix.append(p)
        matrix.append([(i == l - 1) * 1.0 for i in range(l + 1)])
        return matrix

    def equation(matrix, dim):
        for i in range(dim):
            num = matrix[i][i]
            for j in range(dim + 1):
                matrix[i][j] /= num
            for j in range(dim):
                if i != j:
                    a = matrix[j][i]
                    for k in range(i, dim + 1):
                        matrix[j][k] -= a * matrix[i][k]

    if not isinstance(coordinates, dict):
        raise TypeError('coordinates must be a dict')

    length = len(coordinates)
    if length < 3:
        raise InvalidArgument('coordinates require at least three pairs')

    px = [key for key in coordinates.keys()]
    py = [val for val in coordinates.values()]
    matrix = get_matrix(px, py, length)
    equation(matrix, length)
    for i in range(length + 1):
        if x >= px[i] and x <= px[i + 1]:
            break
    j = i + 1
    h = px[j] - px[i]
    s = matrix[j][length] * (x - px[i]) ** 3
    s -= matrix[i][length] * (x - px[j]) ** 3
    s /= 6 * h
    s += (py[j] / h - h * matrix[j][length] / 6) * (x - px[i])
    s -= (py[i] / h - h * matrix[i][length] / 6) * (x - px[j])
    return s


def clamp(x, maximum):
    return max(0, min(round(x), maximum))


class FineSharp(object):
    def __init__(self):
        self.core = vs.get_core()
        self.rgrain = self.core.avs.RemoveGrain
        self.repair = self.core.avs.Repair
        self.std = self.core.std
        self.Expr = self.std.Expr
        self.Lut = self.std.Lut
        self.Lut2 = self.std.Lut2
        self.max = 255
        self.mid = 128

    def add_diff(self, c1, c2, planes=[0]):
        expr = ('x y + {mid} -').format(mid=self.mid)
        expr = [(i in planes) * expr for i in range(3)]
        return self.Expr([c1, c2], expr)

    def make_diff(self, c1, c2, planes=[0]):
        expr = ('x y - {mid} +').format(mid=self.mid)
        expr = [(i in planes) * expr for i in range(3)]
        return self.Expr([c1, c2], expr)

    def sharpen(self, clip, mode=1, sstr=2.0, cstr=None, xstr=0.19, lstr=1.49,
                 pstr=1.272, ldmp=None):

        if clip.format.color_family != vs.YUV or clip.format.bits_per_sample != 8:
            raise InvalidArgument('clip is not 8bit YUV.')

        mode = int(mode)
        if abs(mode) > 3 or mode == 0:
            raise InvalidArgument('mode must be 1, 2, 3, -1, -2 or -3.')

        sstr = float(sstr)
        if sstr < 0.0:
            raise InvalidArgument('sstr must be larger than zero.')

        if cstr is None:
            cstr = spline(sstr, {0:0, 0.5:0.1, 1:0.6, 2:0.9, 2.5:1, 3:1.09,
                                 3.5:1.15, 4:1.19, 8:1.249, 255:1.5})
            if mode > 0:
                cstr **= 0.8
        cstr = float(cstr)

        xstr = float(xstr)
        if xstr < 0.0:
            raise InvalidArgument('xstr must be larger than zero.')

        lstr = float(lstr)

        pstr = float(pstr)

        if ldmp is None:
            ldmp = sstr + 0.1
        ldmp = float(ldmp)

        rg = 20 - (mode > 0) * 9

        if sstr < 0.01 and cstr < 0.01 and xstr < 0.01:
            return clip

        orig = None
        if clip.format.id != vs.YUV420P8:
            orig = clip
            clip = self.core.resize.Point(clip, format=vs.YUV420P8)

        if abs(mode) == 1:
            c2 = self.rgrain(self.rgrain(clip, 11, -1), 4, -1)
        else:
            c2 = self.rgrain(self.rgrain(clip, 4, -1), 11, -1)
        if abs(mode) == 3:
            c2 = self.rgrain(c2, 4, -1)

        def expr(x, y):
            d = x - y
            absd = abs(d)
            e0 = ((absd / lstr) ** (1 / pstr)) * sstr
            e1 = d / (absd + 0.001)
            e2 = (d * d) / (d * d + ldmp)
            return clamp(e0 * e1 * e2 + 128, self.max)

        diff = self.Lut2([clip, c2], function=expr, planes=0)

        shrp = clip
        if sstr >= 0.01:
            shrp = self.add_diff(shrp, diff)

        if cstr >= 0.01:
            expr = lambda x: clamp((x - self.mid) * cstr + self.mid, self.max)
            diff = self.Lut(diff, planes=0, function=expr)
            diff = self.rgrain(diff, rg, -1)
            shrp = self.make_diff(shrp, diff)

        if xstr >= 0.01:
            expr = lambda x, y: clamp(x + (x - y) * 9.9, self.max)
            xyshrp = self.Lut2([shrp, self.rgrain(shrp, 20, -1)], planes=0,
                               function=expr)
            rpshrp = self.repair(xyshrp, shrp, 12, 0)
            shrp = self.std.Merge([rpshrp, shrp], [1 - xstr, 1.0, 1.0])

        if orig is not None:
            shrp = self.std.ShufflePlanes([shrp, orig], [0, 1, 2], vs.YUV)

        return shrp

    def usage(self):
        usage = '''
    Small and relatively fast realtime-sharpening function, for 1080p,
    or after scaling 720p -> 1080p during playback
    (to make 720p look more like being 1080p)
    It's a generic sharpener. Only for good quality sources!
    (If the source is crap, FineSharp will happily sharpen the crap.) ;)
    Noise/grain will be enhanced, too. The method is GENERIC.

    Modus operandi: A basic nonlinear sharpening method is performed,
    then the *blurred* sharp-difference gets subtracted again.


    sharpen(clip, mode=1, sstr=2.0, cstr=None, xstr=0.19, lstr=1.49,
            pstr=1.272, ldmp=None)
        mode: 1 to 3, weakest to strongest. When negative -1 to -3,
              a broader kernel for equalisation is used.
        sstr: strength of sharpening, 0.0 up to ??
        cstr: strength of equalisation, 0.0 to ? 2.0 ?
              (recomm. 0.5 to 1.25, default AUTO)
        xstr: strength of XSharpen-style final sharpening, 0.0 to 1.0
              (but, better don't go beyond 0.249 ...)
        lstr: modifier for non-linear sharpening
        pstr: exponent for non-linear sharpening
        ldmp: "low damp", to not overenhance very small differences
              (noise coming out of flat areas, default sstr+1)
'''
        return usage