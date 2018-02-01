#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
__docformat__ = 'reStructureText'
import logging
import re
import sys

import html5lib
from xml.etree.ElementTree import tostring

logging.basicConfig(level=logging.NOTSET)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

DISPLAY_NONE_RE = re.compile(r'(?m)^\.(\S+)\s*\{\s*display\s*:\s*none\s*\}')


def find_display_none_classes(css_text):
    """
    Finds the class names in the given css style text
    that are ``display:none``.

    For example, feeding this::

        thing { display:inline }
        other { display:none }

    will return::

        ['other']

    :rtype: list[unicode]
    """
    return DISPLAY_NONE_RE.findall(css_text)


def test_parse_css():
    print(find_display_none_classes("""
.s-Aw{display:none}
.zJsC{display:inline}
.IQvs{display:none}
.yBZq{display:inline}
.CyxL{display:none}
.dt09{display:inline}
"""))


def extract_proxy_info(tr_el):
    """
    Yields an (ip:port, proxy type, anon level) tuple
    from the provided table row element.

    :type tr_el: xml.etree.ElementTree.Element
    :rtype: (unicode, unicode, unicode)
    """
    port = None
    kind = None
    level = None

    for td_num, td_el in enumerate(tr_el):
        if not td_el.text:
            continue
        if re.match(r'(?m)\s*\d+\s*', td_el.text):
            if port is not None:
                raise Exception('Cannot cope with multiple ports: port=%s text=<<%s>>'
                                % (port, td_el.text))
            port = int(re.sub(r'\s*', '', td_el.text))
        elif re.match(r'HTTPS?|SOCKS[45]', td_el.text):
            kind = td_el.text
        elif 7 == td_num:  # re.match(r'(?i)low|high')
            level = td_el.text

    if port is None:
        raise ValueError('Expected port, found None')

    # we have to grab the style's parent because ElementTree
    # doesn't permit .parentNode and "dom" doesn't have .findall :-/
    #: :type: list[xml.etree.ElementTree.Element]
    style_parent_nl = tr_el.findall('.//*[style]')
    if not style_parent_nl:
        LOG.error('Expected "style" parent, found None in %s', tostring(tr_el))
        return
    if 1 != len(style_parent_nl):
        LOG.warning('Expected only one style parent, found %d of them',
                    len(style_parent_nl))
    style_parent = style_parent_nl[0]

    #: :type: xml.etree.ElementTree.Element
    sty = style_parent.find('.//style')
    if sty is None:
        LOG.warning('Expected "style" child, found None: %s',
                    tostring(style_parent))
        return
    bad_classes = find_display_none_classes(sty.text)
    LOG.debug('style[%s] -= %s', sty.text, bad_classes)

    #: :type: list[unicode]
    parts = []

    for ip_el in style_parent:
        LOG.debug('IP_EL=((%s))', tostring(ip_el))
        if 'style' == ip_el.tag:
            # don't continue or you'll eat the .tail text
            # which very well could contain a number or dot
            pass
        elif 'class' in ip_el.attrib:
            sp_class = ip_el.attrib['class']
            css = []
            if sp_class:
                css = sp_class.split(' ')
            ok = reduce(lambda a, b: a and b,
                        [x not in bad_classes for x in css],
                        True)
            if ok:
                LOG.debug('#class(%s)=%s', css, ip_el.text)
                parts.append(ip_el.text)
        elif 'style' in ip_el.attrib:
            st = ip_el.attrib['style']
            if 'x' not in find_display_none_classes('.x{%s}' % st):
                LOG.debug('#style(%s)=%s', st, ip_el.text)
                parts.append(ip_el.text)
        else:
            if ip_el.text:
                LOG.warning('??=<<%s>>' % ip_el.text)
        if ip_el.tail:
            parts.append(ip_el.tail)

    if not parts:
        LOG.warning('Your TD contained no IP parts')
        return

    ip_addr = u''.join(parts)
    if not re.match(r'\d+\.\d+\.\d+\.\d+', ip_addr):
        raise ValueError('That does not appear to be an IP: %s' % ip_addr)
    ip_port = '%s:%d' % (ip_addr, port)
    LOG.debug('ip=%s', ip_port)
    return ip_port, kind, level


def run_body(body):
    """
    Enumerate and print the proxies found in `body`.

    :type body: unicode
    """
    # dom: :type: xml.dom.minidom.Document
    # but using it means giving up .find and friends

    #: :type: xml.etree.ElementTree.Element
    html_el = html5lib.parse(body, namespaceHTMLElements=False)

    #: :type: xml.etree.ElementTree.Element
    tab = html_el.find('.//*[@id="listable"]')

    #: :type: list[xml.etree.ElementTree.Element]
    tr_nl = tab.findall('.//tr[@rel]')
    for tr_el in tr_nl:
        info = extract_proxy_info(tr_el)
        if not info:
            continue
        ip = info[0]
        proxy_kind = info[1]
        anon_level = info[2]
        print('%s\t%s\t%s' % (ip, proxy_kind, anon_level))


def main(argv):
    from getopt import getopt
    opts, args = getopt(argv[1:], 'v', ['verbose'])

    is_verbose = ('-v', '') in opts or ('--verbose', '') in opts
    if is_verbose:
        LOG.setLevel(logging.DEBUG)

    filename = args[0]
    if '-' == filename:
        body = sys.stdin.read().decode('utf-8')
    else:
        with open(filename) as fh:
            body = fh.read().decode('utf-8')
    run_body(body)

if __name__ == '__main__':
    main(sys.argv)
