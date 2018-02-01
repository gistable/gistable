import copy
from scrapy import Item

class ModelItem(Item):
    """
    Make Peewee models easily turn into Scrapy Items.

    >>> from models import Player
    >>> item = ModelItem(Player())
    """

    def __init__(self, model, **kwds):
        super(self.__class__, self).__init__()
        self._model = model
        for key in model._meta.fields.keys():
            self.fields[key] = Field()
        if kwds is not None:
            for key, processor in kwds.iteritems():
                self.fields[key] = Field(input_processor=MapCompose(
                    strip_whitespace, processor
                ))

    def __setitem__(self, key, value):
        if key not in self.fields:
            self.fields[key] = Field()
        self._values[key] = value

    def copy(self):
        return copy.deepcopy(self)

    @property
    def model(self):
        return self._model