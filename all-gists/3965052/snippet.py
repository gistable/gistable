"""
A series of functions to extract just the text from html page articles

"""

from lxml import etree
default_encoding = "utf-8"

def newyorker_fp (html_text, page_encoding=default_encoding):
    """For the articles found on the 'Financial Page' section of the New Yorker's website
    (e.g., http://www.newyorker.com/talk/financial/2012/06/04/120604ta_talk_surowiecki)

    Article text is found in:

       <body>
            <div id="articletext"> <!-- there is only one of these -->
    """

    myparser = etree.HTMLParser(encoding=page_encoding)
    tree = etree.HTML(html_text, parser=myparser)
    data = []
    for node in tree.xpath('//div[@id="articletext"]'):
        data.append( ''.join(node.xpath('descendant-or-self::text()')) )
    return ''.join(data)


def facta_print (html_text, page_encoding=default_encoding):
    """For the articles found on Facta's free digital site
    (e.g., http://facta.co.jp/article/201211043-print.html)

    Article text is found in:

    <body>
       <div id="container">
        <div id="contents">
            <div class="content"> <!-- there is only one of these -->
    """

    myparser = etree.HTMLParser(encoding=page_encoding)
    tree = etree.HTML(html_text, parser=myparser)
    data = []
    for node in tree.xpath('//div[@class="content"]'):
        data.append( ''.join(node.xpath('descendant-or-self::text()')) )
    return ''.join(data)

