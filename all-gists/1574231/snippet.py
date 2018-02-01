from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exceptions import DropItem
from scrapy.utils.serialize import ScrapyJSONEncoder

from carrot.connection import BrokerConnection
from carrot.messaging import Publisher

from twisted.internet.threads import deferToThread

class MessageQueuePipeline(object):
    def __init__(self, host_name, port, userid, password, virtual_host, encoder_class):
        self.q_connection = BrokerConnection(hostname=host_name, port=port,
                        userid=userid, password=password,
                        virtual_host=virtual_host)
        self.encoder = encoder_class()
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    @classmethod
    def from_settings(cls, settings):
        host_name = settings.get('BROKER_HOST', 'localhost')
        port = settings.get('BROKER_PORT', 5672)
        userid = settings.get('BROKER_USERID', "guest")
        password = settings.get('BROKER_PASSWORD', "guest")
        virtual_host = settings.get('BROKER_VIRTUAL_HOST', "/")
        encoder_class = settings.get('MESSAGE_Q_SERIALIZER', ScrapyJSONEncoder)
        return cls(host_name, port, userid, password, virtual_host, encoder_class)

    def spider_opened(self, spider):
        self.publisher = Publisher(connection=self.q_connection,
                        exchange="", routing_key=spider.name)

    def spider_closed(self, spider):
        self.publisher.close()

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        self.publisher.send({"scraped_data": self.encoder.encode(dict(item))})
        return item