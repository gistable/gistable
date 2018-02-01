#!/usr/bin/env python
# -*- coding: utf-8 -*-


import misaka


def gfm(str_md = ''):
    '''
    transform the markdown text to html, using github favoured markdown
    usage: str_html = gfm(str_md)
    '''
    str_html = ''
    str_html = misaka.html(str_md,
        extensions = misaka.EXT_NO_INTRA_EMPHASIS | misaka.EXT_FENCED_CODE |
            misaka.EXT_AUTOLINK | misaka.EXT_LAX_HTML_BLOCKS | 
            misaka.EXT_TABLES,
        render_flags = misaka.HTML_TOC | misaka.HTML_USE_XHTML |
            misaka.HTML_HARD_WRAP)
    return str_html

