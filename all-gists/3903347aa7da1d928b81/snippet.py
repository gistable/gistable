import dataset

class DatasetPipeline(object):

    def __init__(self, dataset_uri, dataset_table):
        self.dataset_uri = dataset_uri
        self.dataset_table = dataset_table

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            dataset_uri=crawler.settings.get('DATASET_URI'),
            dataset_table=crawler.settings.get('DATASET_TABLE', 'items')
        )

    def open_spider(self, spider):
        self.db = dataset.connect(self.dataset_uri)

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        self.db[self.dataset_table].insert(item)