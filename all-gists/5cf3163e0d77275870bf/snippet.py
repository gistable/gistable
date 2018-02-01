""" pipelines.py """
import collections
import scrapy
import scrapy.contrib.exporter
import myproject


class SitemapPipeline(object):
    """
    Sitemap builder

    Wait until all items have been scraped and then build a complete sitemap of
    all URLs and add it to the Items.
    """
    items = []

    def __init__(self):
        self.exporter = scrapy.contrib.exporter.PythonItemExporter(
            fields_to_export=('url', 'depth', 'referer'))

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        pipeline.crawler = crawler

        crawler.signals.connect(
            pipeline._spider_idle_handler, scrapy.signals.spider_idle)

        return pipeline

    def _spider_idle_handler(self, spider):
        self.crawler.signals.disconnect(
            self._spider_idle_handler, scrapy.signals.spider_idle)

        self._process_tree(spider)

    def _process_tree(self, spider):
        sitemap = self._get_sitemap()
        self._add_sitemap_item(sitemap, spider)

    def _get_sitemap(self):
        sitemap = []

        def add_nodes(depth, referers):
            """ Recursive """
            _depth = depth + 1
            for referer in referers:
                referer_key = '{}{}{}'.format(_depth, '-'*_depth, referer)
                sitemap_key = '{}{}{}'.format(_depth-1, '-'*(_depth-1), referer)
                sitemap.append(sitemap_key)
                add_nodes(_depth, referers_map[referer_key])

        max_depth = 0
        root_nodes = []
        for d in self.items:
            depth = d['depth']
            if depth > max_depth:
                max_depth = depth
            if depth == 1:
                root_nodes.append(d['url'])

        referers_map = collections.defaultdict(list)
        for d in self.items:
            if 'referer' in d:
                referer_key = '{}{}{}'.format(d['depth'], '-'*d['depth'], d['referer'])
                referers_map[referer_key].append(d['url'])

        add_nodes(1, root_nodes)

        return sitemap

    def _add_sitemap_item(self, sitemap, spider):
        request = response = None
        scraper = self.crawler.engine.scraper
        item = myproject.items.SitemapItem(dict(sitemap=sitemap))
        scraper._process_spidermw_output(item, request, response, spider)

    def process_item(self, item, spider):
        self.items.append(self.exporter.export_item(item))
        return item
