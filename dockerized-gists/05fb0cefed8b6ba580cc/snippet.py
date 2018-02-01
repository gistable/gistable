#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from bs4 import BeautifulSoup
import hashlib
import logging
import json
import os
import sys
import re
import time
import urlparse
import zipfile

INDEX_RDF = '''<?xml version="1.0" encoding="UTF-8"?>
<RDF:RDF xmlns:MAF="http://maf.mozdev.org/metadata/rdf#"
         xmlns:NC="http://home.netscape.com/NC-rdf#"
         xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <RDF:Description RDF:about="urn:root">
    <MAF:originalurl RDF:resource="%(url)s"/>
    <MAF:title RDF:resource="%(title)s"/>
    <MAF:archivetime RDF:resource="%(time)s"/>
    <MAF:indexfilename RDF:resource="index.html"/>
    <MAF:charset RDF:resource="UTF-8"/>
  </RDF:Description>
</RDF:RDF>
'''


def main(argv):
    log = logging.getLogger('har_maff')
    logging.basicConfig(level=logging.INFO)

    filename = argv[1]
    maff_fn = os.path.join(os.path.dirname(filename),
                           re.sub(r'\.har$', '.maff', os.path.basename(filename)))
    print('Saving to %s' % maff_fn)

    maff_fh = open(maff_fn, 'wb')
    zf = zipfile.ZipFile(maff_fh, mode='w')

    with open(filename, 'rb') as fh:
        har_body = fh.read()

    har = json.loads(har_body, encoding='utf-8')
    har_log = har['log']
    har_version = har_log['version']
    if '1.2' != har_version:
        log.error('I only support version 1.2, not %s' % har_version)
        return 1
    har_pages = har_log['pages']
    if not har_pages:
        log.error('Har has no "pages", that is fatal')
        return 1
    page0 = har_pages[0]

    ## this is in full ISO8601, including millis which
    ## python 2.7 does not support
    started_dt = re.sub(r'\.\d+Z$', 'Z', page0['startedDateTime'])

    save_time = time.strptime(started_dt, '%Y-%m-%dT%H:%M:%SZ')
    rdf_time = time.strftime('%a, %d %b %Y %H:%M:%S -0000', save_time)
    out_dir = '%s' % int(time.mktime(save_time))
    start_page = page0['title']  # yup, "title"
    entries = har_log['entries']

    page_title = None
    #: :type: dict[unicode, unicode]
    mime_types = {}
    for en in entries:
        req = en['request']
        req_url = req['url']
        resp = en['response']
        contents = resp['content']
        #: :type: unicode
        media_type = contents['mimeType']
        mime_types[req_url] = media_type

    for en in entries:
        req = en['request']
        req_method = req['method']
        req_url = req['url']
        resp = en['response']
        contents = resp['content']
        media_type = mime_types[req_url]

        if 'GET' != req_method:
            log.warn('Skipping non-GET url: %s \"%s\"' % (req_method, req_url))
            continue
        if start_page == req_url:
            out_fn = 'index.html'
        else:
            out_fn = hashlib.md5(req_url.encode('utf-8')).hexdigest()
            if 'image/gif' in media_type:
                out_fn = '%s.gif' % out_fn
            elif 'image/jpeg' in media_type:
                out_fn = '%s.jpeg' % out_fn
            elif 'image/png' in media_type:
                out_fn = '%s.png' % out_fn
            elif '/javascript' in media_type:
                out_fn = '%s.js' % out_fn
            elif 'text/css' in media_type:
                out_fn = '%s.css' % out_fn

        if 'text' not in contents:
            continue
        #: :type: unicode
        text_content = contents['text']

        if start_page == req_url:
            soup = BeautifulSoup(text_content)
            page_title = soup.select('title')[0].text

            def make_re(linky):
                #: :type: unicode
                safe_link = re.escape(linky)
                # BS does not allow us to know if the href contained the "&amp" or not
                # so here we update the regex to permit either
                link_re = re.compile(safe_link.replace('\&', '\&(?:amp;)?'))
                return link_re

            def update_entries_to_req_url(to_url):
                """
                Finds the request URL in the HAR, independent of port number,
                and if they are different from the provided :py:param:`to_url`
                then I will update the **global** `entries` dict.

                Turns out, HAR does not store the **accurate** URL.
                For example, ``https://example.com:443/``
                is stored in the har as ``https://example.com/``

                :param unicode to_url: the URL used in the document
                :return: the URL as stored in the HAR
                :rtype: unicode | None
                """
                result = None
                urlp = urlparse.urlparse(to_url)
                ## this is, after all, the whole problem here
                # noinspection PyProtectedMember
                urlp = urlp._replace(netloc=re.sub(r':\d+', '', urlp.netloc))
                for url2 in mime_types.iterkeys():
                    url2p = urlparse.urlparse(url2)
                    # noinspection PyProtectedMember
                    url2p = url2p._replace(netloc=re.sub(r':\d+', '', url2p.netloc))
                    if urlp == url2p:
                        log.debug('matched "%s" and "%s" ...', to_url, url2)
                        result = url2
                        if url2 != to_url:
                            for en2 in entries:
                                if url2 == en2['request']['url']:
                                    mime_types[to_url] = mime_types[url2]
                                    en2['request']['url'] = to_url
                                    log.warn('Replaced "%s" with "%s" because HAR was wrong', url2, to_url)
                        break
                return result

            for css in soup.select('link[rel=stylesheet]'):
                css_href = css.attrs.get('href')
                update_entries_to_req_url(css_href)
                css_href2 = '%s.css' % hashlib.md5(css_href).hexdigest()
                log.debug('replacing css href %s => %s', css_href, css_href2)
                text_content = make_re(css_href).sub(css_href2, text_content)

            for js in soup.select('script[src]'):
                js_href = js.attrs.get('src')
                update_entries_to_req_url(js_href)
                js_href2 = '%s.js' % hashlib.md5(js_href).hexdigest()
                log.debug('replacing js src %s => %s' % (js_href, js_href2))
                text_content = make_re(js_href).sub(js_href2, text_content)

            for img in soup.select('img[src]'):
                img_href = img.attrs.get('src')
                # we need the HAR url in order to look up the URL
                # in the mime-types dict
                har_url = update_entries_to_req_url(img_href)
                ## turns out, the .har doesn't capture *every* <img>
                if not har_url:
                    log.debug('Skipping non-HAR img.src "%s"', img_href)
                    continue
                img_mt = mime_types.get(har_url)
                if 'image/png' in img_mt:
                    img_ext = 'png'
                elif 'image/jpeg' in img_mt:
                    img_ext = 'jpeg'
                elif 'image/gif' in img_mt:
                    img_ext = 'gif'
                else:
                    log.error('Unrecognized img media type: %s for %s', img_mt, img_href)
                    img_ext = ''
                img_href2 = '%s.%s' % (hashlib.md5(img_href).hexdigest(), img_ext)
                log.debug('replacing img src %s => %s' % (img_href, img_href2))
                text_content = make_re(img_href).sub(img_href2, text_content)

        # I'm sure this is documented and I'm sure I didn't look it up
        compress = contents.get('compression', -1)
        if 36 == compress or 0 == compress:
            the_bytes = text_content.decode('base64')
        else:
            the_bytes = text_content.encode('utf-8')
        log.debug('URL:"%s" => "%s"' % (req_url, out_fn))
        zf.writestr(os.path.join(out_dir, out_fn), the_bytes)

    rdf = INDEX_RDF % {
        'url': re.sub(re.escape('&'), '&amp;', start_page),
        'title': page_title,
        'time': rdf_time,
    }
    zf.writestr(os.path.join(out_dir, 'index.rdf'), rdf.encode('utf-8'))
    zf.close()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))