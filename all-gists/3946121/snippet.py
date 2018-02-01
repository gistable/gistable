import sys
import colorsys
from colorz import colorz

WALLPAPER = '/home/james/.wallpaper'
COLORS = '/home/james/.colors'
XRESOURCES = '/home/james/.Xresources'

cols = ''
xres = """
URxvt.font: -*-unifont-medium-*-*-*-16-*-*-*-*-*-*-*
URxvt.boldFont: -*-unifont-medium-*-*-*-16-*-*-*-*-*-*-*
URxvt.perl-ext-common: default,keyboard-select,url-select,clipboard
URxvt.modifier: super

! Original Colors
! urxvt*color8:    #4DA869
! urxvt*color9:    #EF2929
! urxvt*color10:    #BDA2BF
! urxvt*color11:    #FFF391
! urxvt*color12:    #7587A6
! urxvt*color13:    #F0C47B
! urxvt*color14:    #FF4040
! urxvt*color15:    #EEEEEC
! urxvt*color0:    #2E3436
! !urxvt*color0:    #000000
! urxvt*color1:    #DD1144
! urxvt*color2:    #9B859D
! urxvt*color3:    #F9EE98
! urxvt*color4:    #424D5E
! urxvt*color5:    #CDA869
! urxvt*color6:    #E94444
! urxvt*color7:    #C2C2C2

! Keyboard select
URxvt.keysym.M-Escape: perl:keyboard-select:activate
URxvt.keysym.M-s: perl:keyboard-select:search

! URL select
URxvt.keysym.M-u: perl:url-select:select_next
URxvt.url-select.autocopy: true
URvxt.url-select.button: 1
URvxt.url-select.launcher: mimeo
URxvt.url-select.underline: true

! Clipboard
URxvt.keysym.M-c:   perl:clipboard:copy
URxvt.keysym.M-v:   perl:clipboard:paste
URxvt.keysym.M-C-v: perl:clipboard:paste_escaped


URxvt.foreground: #ffffff
URxvt.scrollBar: false
URxvt.depth: 32
URxvt.background: [85]#0E0E0E

! Colorz

"""

def normalize(hexv, minv=128, maxv=256):
    hexv = hexv[1:]
    r, g, b = (
        int(hexv[0:2], 16) / 256.0,
        int(hexv[2:4], 16) / 256.0,
        int(hexv[4:6], 16) / 256.0,
    )
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    minv = minv / 256.0
    maxv = maxv / 256.0
    if v < minv:
        v = minv
    if v > maxv:
        v = maxv
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return '#{:02x}{:02x}{:02x}'.format(int(r * 256), int(g * 256), int(b * 256))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        n = 16
    else:
        n = int(sys.argv[1])


    i = 0
    with open('colorz.html', 'w') as f:
        f.write("""<img src="file://{}" height=200/>""".format(WALLPAPER))
        for c in colorz(WALLPAPER, n=n):
            # if i == 8:
            #     i += 1
            if i == 0:
                c = normalize(c, minv=0, maxv=32)
            elif i == 8:
                c = normalize(c, minv=128, maxv=192)
            elif i < 8:
                c = normalize(c, minv=160, maxv=224)
            else:
                c = normalize(c, minv=200, maxv=256)
            f.write("""
                <div style="background-color: {0}; width: 100%; height: 50px">{1}: {0}</div>
                """.format(c, i)
            )
            xres += """urxvt*color{}: {}\n""".format(i, c)
            cols += """export COLOR{}="{}"\n""".format(i, c)
            i += 1

    with open(XRESOURCES, 'w') as f:
        f.write(xres)
    with open(COLORS, 'w') as f:
        f.write(cols)
