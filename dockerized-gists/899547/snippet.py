# -*- coding:utf-8 -*-
"""
Backup Google Reader Items to WordPress eXtended RSS (Wordpress Export Format)

Download Feeds from http://www.google.com/reader/atom/feed/http://yourblogdomain.com/yourfeed?n=1000
(1000 = number of items)

Usage: reader2wordpress.py google_atom.xml http://yourblogdomain.com/

Licensed under BSD.
By Stefan Wehrmeyer
http://stefanwehrmeyer.com/

"""
import sys
import re
from datetime import datetime
from lxml import etree

WORDPRESS_EXPORT_NS = "http://wordpress.org/export/1.1/"
WP = "{%s}" % WORDPRESS_EXPORT_NS

ATOM_NS = "http://www.w3.org/2005/Atom"
ATOM = "{%s}" % ATOM_NS

GATOM_NS = "http://www.google.com/schemas/reader/atom/"
GATOM = "{%s}" % GATOM_NS

DUBLIN_CORE_NS = "http://purl.org/dc/elements/1.1/"
DC = "{%s}" % DUBLIN_CORE_NS

CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
CONTENT = "{%s}" % CONTENT_NS

EXCERPT_NS = "http://wordpress.org/export/1.1/excerpt/"
EXCERPT = "{%s}" % EXCERPT_NS

NSMAP = {
    "wp" : WORDPRESS_EXPORT_NS,
    "dc": DUBLIN_CORE_NS,
    "content": CONTENT_NS,
    "excerpt": EXCERPT_NS
}

def generate(filename, SITE_URL):
    def get(root, xpath, ns=ATOM):
        return etree.ETXPath(xpath % {"ns": ns})(root)
    
    def convert_atom_to_rss_date(date):
        """Code taken from Django (BSD)"""
        # 2011-03-23T15:06:50Z
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            # We can't use strftime() because it produces locale-dependant results, so
        # we have to map english month and day names manually
        months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',)
        days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        # We do this ourselves to be timezone aware, email.Utils is not tz aware.
        dow = days[date.weekday()]
        month = months[date.month - 1]
        time_str = date.strftime('%s, %%d %s %%Y %%H:%%M:%%S ' % (dow, month))
        return time_str + '-0000'

    rss = etree.Element("rss", nsmap=NSMAP) # lxml only!
    rss.attrib["version"] = "2.0"

    channel = etree.SubElement(rss, "channel")

    root = etree.fromstring(file(filename).read())
    authors = dict([(k, i) for i, k in enumerate(list(set(get(root, '//%(ns)sauthor/%(ns)sname/text()'))))])

    etree.SubElement(channel, "title").text = get(root, "//%(ns)stitle/text()")[0]
    etree.SubElement(channel, "link").text = SITE_URL
    etree.SubElement(channel, "description").text = get(root, "//%(ns)ssubtitle/text()")[0]
    etree.SubElement(channel, "pubDate").text = 'Sat, 02 Apr 2011 11:33:16 +0000'
    etree.SubElement(channel, "language").text = 'en'
    etree.SubElement(channel, "%swxr_version" % WP).text = '1.1'
    etree.SubElement(channel, "%sbase_site_url" % WP).text = SITE_URL
    etree.SubElement(channel, "%sbase_blog_url" % WP).text = SITE_URL

    for author, i in authors.items():
        authorelem = etree.SubElement(channel, "%sauthor" % WP)
        etree.SubElement(authorelem, "%sauthor_id" % WP).text = str(i)
        etree.SubElement(authorelem, "%sauthor_login" % WP).text = re.sub(r'[^\w-]', '', author.lower())
        etree.SubElement(authorelem, "%sauthor_email" % WP).text = ''
        etree.SubElement(authorelem, "%sauthor_display_name" % WP).text = author
        etree.SubElement(authorelem, "%sauthor_first_name" % WP).text = ''
        etree.SubElement(authorelem, "%sauthor_last_name" % WP).text = ''
    counter = 0
    for item in reversed(get(root, "//%(ns)sentry")):
        counter += 1
        itemelem = etree.SubElement(channel, "item")
        etree.SubElement(itemelem, "title").text = get(item, "%(ns)stitle/text()")[0]
        link = get(item, "%(ns)slink")[0].attrib["href"]
        etree.SubElement(itemelem, "link").text = link
        date = get(item, "%(ns)spublished/text()")[0]
        etree.SubElement(itemelem, "pubDate").text = convert_atom_to_rss_date(date)
        author = get(item, '%(ns)sauthor/%(ns)sname/text()')
        etree.SubElement(itemelem, "%screator" % DC).text = re.sub(r'[^\w-]', '', author[0].lower())
        guid = etree.SubElement(itemelem, "guid")
        gid = get(item, "%(ns)sid")[0]
        guid.text = gid.attrib["%soriginal-id" % GATOM]
        guid.attrib["isPermaLink"] = "false"
        etree.SubElement(itemelem, "description")
        content = get(item, "%(ns)scontent/text()")
        summary = ""
        if not content:
            content = get(item, "%(ns)ssummary/text()")
            summary = content[0]
        content = content[0].replace("&lt;", "<").replace("&gt;", ">")
        etree.SubElement(itemelem, "%sencoded" % CONTENT).text = "%s" % content
        etree.SubElement(itemelem, "%sencoded" % EXCERPT).text = "%s" % summary
    
        etree.SubElement(itemelem, "%spost_id" % WP).text = str(counter)
        post_date = date[:-1].replace("T", " ")
        etree.SubElement(itemelem, "%spost_date" % WP).text = post_date
        etree.SubElement(itemelem, "%spost_date_gmt" % WP).text = post_date
        etree.SubElement(itemelem, "%scomment_status" % WP).text = 'open'
        etree.SubElement(itemelem, "%sping_status" % WP).text = 'open'
        etree.SubElement(itemelem, "%spost_name" % WP).text = link.split('/')[-2]
        etree.SubElement(itemelem, "%sstatus" % WP).text = 'publish'
        etree.SubElement(itemelem, "%spost_parent" % WP).text = '0'
        etree.SubElement(itemelem, "%smenu_order" % WP).text = '0'
        etree.SubElement(itemelem, "%spost_type" % WP).text = 'post'
        etree.SubElement(itemelem, "%spost_password" % WP).text = ''
        etree.SubElement(itemelem, "%sis_sticky" % WP).text = '0'
        categories = get(item, "%(ns)scategory[@term]")
        for category in categories:
            if "scheme" in category.attrib:
                continue
            category = category.attrib["term"]
            catelem = etree.SubElement(itemelem, "category")
            catelem.attrib["domain"] = "category"
            catelem.attrib["nicename"] = re.sub(r'[^\w-]', '', category.lower())
            catelem.text = '%s' % category
        postmeta = etree.SubElement(itemelem, "%spostmeta" % WP)
        etree.SubElement(postmeta, "%smeta_key" % WP).text = '_edit_last'
        etree.SubElement(postmeta, "%smeta_value" % WP).text = '3'
    print etree.tostring(rss)

if __name__ == '__main__':
    generate(sys.argv[1], sys.argv[2])