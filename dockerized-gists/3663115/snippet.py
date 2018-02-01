#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<17175297.hk@gmail.com>
#         http://binux.me
# Created on 2012-09-06 22:22:21

import urlparse
import re

xmlhttprequest = '''XMLHttpRequest.prototype._open=XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(m,u,a,us,p) {
  var proxyurl='%s', baseurl='%s', a=document.createElement('a');
  a.href=u;u=a.href.replace(proxyurl,'');u=proxyurl+(u.indexOf('http')==0?u:baseurl+u);
  if(console&&console.log){console.log("XMLHTTPRequest:",u);}
  return this._open(m,u,a,us,p);
}'''
http_re = re.compile("https?://", re.I)
href_re1 = re.compile("((href|src|action)\s*=\s*\"([^\"<>]+)\")", re.I)
href_re2 = re.compile("((href|src|action)\s*=\s*\'([^\'<>]+)\')", re.I)
href_re3 = re.compile("((href|src|action)\s*=\s*([^\'\"\s<>]+))", re.I)
xmlhttprequest_re = re.compile("<script", re.I)
def rewrite(proxyurl, baseurl, content):
    #content = http_re.sub(proxyurl+"\g<0>", content)
    for all, href, url in href_re1.findall(content):
        rewrited_url = urlparse.urljoin(baseurl, url)
        if not rewrited_url.startswith(proxyurl) and rewrited_url.startswith("http"):
            content = content.replace(all, '%s="%s%s"' % (href, proxyurl, rewrited_url))
    for all, href, url in href_re2.findall(content):
        rewrited_url = urlparse.urljoin(baseurl, url)
        if not rewrited_url.startswith(proxyurl) and rewrited_url.startswith("http"):
            content = content.replace(all, '%s=\'%s%s\'' % (href, proxyurl, rewrited_url))
    for all, href, url in href_re3.findall(content):
        rewrited_url = urlparse.urljoin(baseurl, url)
        if not rewrited_url.startswith(proxyurl) and rewrited_url.startswith("http"):
            content = content.replace(all, '%s="%s%s"' % (href, proxyurl, rewrited_url))
    content = content.replace("</title>", "</title><script>%s</script>" % xmlhttprequest % (proxyurl, urlparse.urljoin(baseurl, "/")), 1)
    return content
