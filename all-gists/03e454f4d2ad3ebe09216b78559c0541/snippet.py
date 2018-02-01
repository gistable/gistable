# hax hax hax hax hax

import ctypes, os, sys
newstderr = os.dup(2)                          # This is to mute dyld LC_RPATH warnings
os.dup2(os.open('/dev/null', os.O_WRONLY), 2)  # because we're loading Xcode frameworks from python
CM = ctypes.CDLL('/Applications/Xcode.app/Contents/SharedFrameworks/DVTMarkup.framework/Versions/A/Frameworks/CommonMark.framework/CommonMark')
sys.stderr = os.fdopen(newstderr, 'w')         # This restores stderr

cmark_markdown_to_html = CM.cmark_markdown_to_html
cmark_markdown_to_html.restype = ctypes.c_char_p

def markdown_to_html(markdown):
    mc = ctypes.create_string_buffer(markdown)
    return cmark_markdown_to_html(mc, len(mc)-1, 0)
