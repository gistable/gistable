# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import os
import re
import yaml
import urllib
import codecs
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup, Comment

# save markdown to single LOGFILE
DEBUG = False
XML = "wordpress.2011-09-19.xml"
EXPORT_ROOT = 'source/'
MARKDOWN_FORMAT = '%04d-%02d-%02d-%s.markdown'
LOGFILE = "log.markdown"
EXCLUDE_METAS = [
    u'_edit_last',
    u'superawesome',
    u'delicious',
    u'_wp_page_template',
]
EXCLUDE_CATEGORIES = [
    u'Uncategorized',
]
EXCLUDE_TAGS = []

def to_markdown(txt):
    matches = [
    	[r'</?strong>', '**'],
    	[r'</?em>', '*'],
    	[r'<h1>', '# '],
    	[r'<h2>', '## '],
    	[r'<h3>', '### '],
    	[r'<h4>', '#### '],
    	[r'<h5>', '##### '],
    	[r'<h6>', '###### '],
    	[r'</h\d>', '\n'],
    	[r'</?p[^>]*>', '\n'], # <p class=blahblah>..</p>
    	[r'</?span[^>]*>',''], # <span class=blahblah>..</span>
    	[r'<br\s*/?>', '  '],
    	[r' {3,}', '  '],
    	[r'<a.+?href="([^"]+)"[^>]*>([^<]+)</a>', r'[\2](\1)'],
    	[r'<li>', '- '],
    	[r'</li>', ''],
    	[r'</?ul>', ''],
    	[r'</?ol>', ''],
    	[r'\n{3}', '\n\n'],
    	[r'&amp;', '&'],
    	[r'&lt;', '<'],
    	[r'&gt;', '>'],
    	[r'&nbsp;', ' '],
    	[r'&quot;', '"'],
    	[r'&#\d+;',''], # &#NNNN; some html entities

    	# remove custom tags found in xml
    	[r'<div class="blogger-post-footer">.+</div>',''],

        # liquid tag conflict. but {{}} is manually fixed :P
        [r'{%(.+?)%}', r'{{ "{% \1 "}} %}'],    	

        # octopress plugin
    	[r'<img(.+?)src="([^"]+)"\s+alt="([^"]+)"[^>]*/>', r'{% img \2 \3 %}'],
    	[r'<img(.+?)src="([^"]+)"[^>]*/>', r'{% img \2 %}'],
    	[r'\[sourcecode language=["\']([^"\']+)["\']\]', r'{% codeblock lang:\1 %}'],
    	[r'\[/sourcecode\]', r'{% endcodeblock %}'],
    	[r'\[cpp\]', r'{% codeblock lang:cpp %}'],
    	[r'\[/cpp\]', r'{% endcodeblock %}'],
    	[r'\[python\]', r'{% codeblock lang:python %}'],
    	[r'\[/python\]', r'{% endcodeblock %}'],
    	[r'\[code\]', r'```\n'],
    	[r'\[/code\]', r'```'],
        [r'<pre><code>', r'```\n'],
        [r'</code></pre>', r'```'],
    	[r'<pre>', r'```\n'],
    	[r'</?pre>', r'```'],
    	#[r'</?code>', r'```'],
        [r'<blockquote>', r'{% blockquote %}'],
        [r'</blockquote>', r'{% endblockquote %}'],
    ]

    for match in matches:
        txt = re.sub(match[0], match[1], txt)

    return txt
    
def slugify(title):
    # this may break permlink.... please checkout removal of some chars.
    title = title.strip().lower()
    matches = [
    	[r"[,.]", ''],
    	[r" ", '-'],
    ]
    for match in matches:
        title = re.sub(match[0], match[1], title)
    
    return title

def parse_item(item):
    # pub_date = item.find("pubDate") # some old posts have missing year. ex> Wed, 30 Nov -0001 00:00:00 +0000 
    # creator = item.find("dc:creator") # always me
    # guid = item.find("guid") # original imported URL. can be None. isPermaLink alwase false
    # description = item.find("description") # i never use this :P
    # excerpt = item.find("excerpt:encoded") # i never use this :P
    # wp_post_id = item.find("wp:post_id") # integer
    # wp_post_date_gmt = item.find("wp:post_date_gmt") # sometimes 0000-00-00 00:00:00
    # wp_ping_status = item.find("wp:ping_status") # open, closed
    # wp_post_parent = item.find("wp:post_parent") # wp:post_id
    # wp_menu_order = item.find("wp:menu_order") # integer?
    # wp_is_stiky = item.find("wp:is_sticky") # 0 or 1 ?
    
    def _(node):
        if not node or not node.string:
            return u''            
        u = unicode(node.string)
        if u.startswith(u'<![CDATA['):
            u = u[9:-3]
        return u
    
    # ex> post, page, attachment, custom_dns(for dns service)
    wp_post_type = _(item.find("wp:post_type")) 
    if wp_post_type not in (u'post', u'page'):
        return
    
    # ex> draft, auto-draft, private, publish, attachment, inherit(for attachment)
    wp_status = _(item.find("wp:status")) 
    if wp_status == u'attachment':
        return

    title = _(item.find("title"))
    title = title.replace("\\","") # backslash raise error on yaml string

    wp_post_date = _(item.find("wp:post_date")) 
    post_date = datetime.strptime(wp_post_date,"%Y-%m-%d %H:%M:%S")

    # slug can be null or quoted already (if cjk title)
    slug = _(item.find("wp:post_name"))
    if not slug:
        slug = slugify(title)
    else:
        slug = urllib.unquote(slug.encode('utf-8')).decode('utf-8')
        
    assert isinstance(slug, unicode), 'slug should be unicode'
        
    filename = u'%04d-%02d-%02d-%s.markdown'%(post_date.year, post_date.month, post_date.day, slug)

    if DEBUG:
        out = codecs.open( LOGFILE, "a", "utf-8")
        out.write(u'\n_%ss/%s\n'% (wp_post_type, filename))
    else:
        path = os.path.join(u"source", u"_%ss"% wp_post_type)
        if not os.access( path, os.F_OK ):
            os.mkdir( path )
        try:
            out = codecs.open( os.path.join(path, filename), "w", "utf-8")
        except UnicodeDecodeError, e:
            print 'UnicodeDecodeError:', str(e), 'in', post_date, _(item.find("title"))
            print 'slug', type(slug), 'filename', type(filename), 'path', type(path)
            return

    # starting yaml header
    out.write(u'---\n')
    
    # post or page layout template
    out.write(u'layout: %s\n'% wp_post_type)

    # sometimes title contains html entities like &amp; &lt; &gt; ...
    out.write(u'title: "%s"\n'% title)

    # NOTE bulk-imported posts have same datetime!
    out.write(u'date: %s\n'% post_date)

    # perm link? normally contains original link.
    link = _(item.find("link"))
    out.write(u'link: %s\n'% link)

    tags = []
    for tag in item.findAll("category",{"domain":"tag"}):
        tags.append(_(tag))
    tags = list(set([t for t in tags if t not in EXCLUDE_TAGS]))
    if tags:
        out.write(u'tags:\n')
        for tag in tags:
            out.write(u'- %s\n'% tag)

    categories = []
    for category in item.findAll("category",{"domain":"category"}):
        categories.append(_(category))
    categories = list(set([c for c in categories if c not in EXCLUDE_CATEGORIES]))
    if categories:
        out.write(u'categories:\n')
        for category in categories:
            out.write(u'- %s\n'% category)

    # some metas are useless...
    metas = {}
    for meta in item.findAll("wp:post_meta"):
        meta_key = _(meta.find("wp:meta_key"))
        meta_value = _(meta.find("wp:meta_value"))
        if meta_key not in EXCLUDE_METAS:
            metas[meta_key] = meta_key
    if metas:
        out.write(u'meta:\n')
        for k, v in metas:
            out.write(u'  %s: %s\n'% (k, v))

    #out.write(u'status: %s\n'% wp_status)

    # octopress will skip unpublished posts.
    out.write(u'published: %s\n'% ('true' if wp_status == u'publish' else 'false'))

    # octopress will not show comment input??
    # ex> open, closed
    wp_comment_status = _(item.find("wp:comment_status")) 
    out.write(u'comments: %s\n'% ('true' if wp_comment_status == u'open' else 'false'))
    
    # end of yaml header
    out.write(u'---\n')

    content = _(item.find("content:encoded"))
    content = to_markdown(content.strip())
    out.write(content)

    out.close()    
        
if __name__ == '__main__':

    if DEBUG:
        if os.access(LOGFILE, os.F_OK ):
            os.remove(LOGFILE)
        
    # if len(sys.argv) > 1:
    #     XML = sys.argv[1]
        
    print 'loading...'
    soup = BeautifulStoneSoup(open(XML))
    print 'parsing...'
    for item in soup.findAll("item"):
        parse_item(item)
    print 'done'
        