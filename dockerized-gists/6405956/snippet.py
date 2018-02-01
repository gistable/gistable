import sys
from grapefruit import Color
from fabulous.xterm256 import rgb_to_xterm

new_vim_color = []


def html2xterm256(color):
    r, g, b = Color.HtmlToRgb(html_color)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return rgb_to_xterm(r, g, b)

for line in open(sys.argv[1]):
    _tmp = line.split()
    _tmp_line = []
    for _t in _tmp:
        if 'guifg=' in _t:
            html_color = _t.split('guifg=')[1]
            if html_color[0] != '#':
                continue
            c = html2xterm256(html_color)
            _tmp_line.append("ctermfg=%d" % c)
        if 'guibg=' in _t:
            html_color = _t.split('guibg=')[1]
            if html_color[0] != '#':
                continue
            c = html2xterm256(html_color)
            _tmp_line.append("ctermbg=%d" % c)
        if 'gui=' in _t:
            _term = _t.split('gui=')[1]
            _tmp_line.append("cterm=%s" % _term)
        _tmp_line.append(_t)
    new_vim_color.append(" ".join(_tmp_line))

print("\n".join(new_vim_color))
