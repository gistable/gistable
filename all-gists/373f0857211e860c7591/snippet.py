from scrapy.selector import Selector

selector = Selector(text="""
<div itemscope itemtype ="http://schema.org/Movie">
  <h1 itemprop="name">Avatar</h1>
  <span>Director: <span itemprop="director">James Cameron</span> (born August 16, 1954)</span>
  <span itemprop="genre">Science fiction</span>
  <a href="../movies/avatar-theatrical-trailer.html" itemprop="trailer">Trailer</a>
</div>""", type="html")

for item in selector.xpath('.//*[@itemscope]'):
    print item.xpath('@itemtype').extract()
    for property in item.xpath('.//*[@itemprop]'):
        print property.xpath('@itemprop').extract(),
        print property.xpath('string(.)').extract(),
        print property.xpath('@*').extract()

print
selector = Selector(text="""
<div itemscope itemtype="http://schema.org/Movie">
  <h1 itemprop="name">Avatar</h1>
  <div itemprop="director" itemscope itemtype="http://schema.org/Person">
  Director: <span itemprop="name">James Cameron</span> 
(born <time itemprop="birthDate" datetime="1954-08-16">August 16, 1954</time>)
  </div>
  <span itemprop="genre">Science fiction</span>
  <a href="../movies/avatar-theatrical-trailer.html" itemprop="trailer">Trailer</a>
</div>""", type="html")


for item in selector.xpath('.//*[@itemscope]'):
    print item.xpath('@itemtype').extract()
    for property in item.xpath('.//*[@itemprop]'):
        print property.xpath('@itemprop').extract(),
        print property.xpath('string(.)').extract(),
        print property.xpath('@*').extract()

print

for item in selector.xpath('.//*[@itemscope]'):
    print "Item:", item.xpath('@itemtype').extract()
    for property in item.xpath('.//*[@itemprop]'):
        print "Property:",
        print property.xpath('@itemprop').extract(),
        print property.xpath('string(.)').extract()
        for position, attribute in enumerate(property.xpath('@*'), start=1):
            print "attribute: name=%s; value=%s" % (
                property.xpath('name(@*[%d])' % position).extract(),
                attribute.extract())
        print
    print


for item in selector.xpath('.//*[@itemscope]'):
    print "Item:", item.xpath('@itemtype').extract()
    for property in item.xpath(
            """set:difference(.//*[@itemprop],
                              .//*[@itemscope]//*[@itemprop])"""):
        print "Property:", property.xpath('@itemprop').extract(),
        print property.xpath('string(.)').extract()
        for position, attribute in enumerate(property.xpath('@*'), start=1):
            print "attribute: name=%s; value=%s" % (
                property.xpath('name(@*[%d])' % position).extract(),
                attribute.extract())
        print
    print

for item in selector.xpath('.//*[@itemscope]'):
    print "Item:", item.xpath('@itemtype').extract()
    print "ID:", item.xpath("""count(preceding::*[@itemscope])
                             + count(ancestor::*[@itemscope])
                             + 1""").extract()


import pprint
items = []
for itemscope in selector.xpath('//*[@itemscope][@itemtype]'):
    item = {"itemtype": itemscope.xpath('@itemtype').extract()[0]}
    item["item_id"] = int(float(itemscope.xpath("""count(preceding::*[@itemscope])
                                                 + count(ancestor::*[@itemscope])
                                                 + 1""").extract()[0]))
    properties = []
    for itemprop in itemscope.xpath("""set:difference(.//*[@itemprop],
                                                      .//*[@itemscope]//*[@itemprop])"""):
        property = {"itemprop": itemprop.xpath('@itemprop').extract()[0]}
        if itemprop.xpath('@itemscope'):
            property["value_ref"] = {
                "item_id": int(float(itemprop.xpath("""count(preceding::*[@itemscope])
                                                     + count(ancestor::*[@itemscope])
                                                     + 1""").extract()[0]))
            }
        else:
            value = itemprop.xpath('normalize-space(.)').extract()[0]
            if value:
                property["value"] = value
        attributes = []
        for index, attribute in enumerate(itemprop.xpath('@*'), start=1):
            propname = itemprop.xpath('name(@*[%d])' % index).extract()[0]
            if propname not in ("itemprop", "itemscope"):
                attributes.append((propname, attribute.extract()))
        if attributes:
            property["attributes"] = dict(attributes)
        properties.append(property)
    item["properties"] = properties
    items.append(item)
pprint.pprint(items)
