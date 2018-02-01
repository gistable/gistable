import abc
import math
import collections

import six


@six.add_metaclass(abc.ABCMeta)
class Paginator(object):
    
    def __init__(self, cursor, size):
        self.cursor = cursor
        self.size = size

    @abc.abstractmethod
    def slice(self, offset, limit):
        pass

    @abc.abstractmethod
    def count(self):
        pass

    @property
    def pages(self):
        return int(math.ceil(self.count() / self.size))

    def has_page(self, index):
        return index > 0 and index <= self.pages

    def get_page(self, index):
        return Page(index, self.slice(self.size * (index - 1), self.size), self)


class Page(collections.Sequence):
    
    def __init__(self, index, contents, paginator):
        self.index = index
        self.contents = contents
        self.paginator = paginator

    def __len__(self):
        return len(self.contents)

    def __getitem__(self, index):
        return self.contents[index]

    @property
    def pages(self):
        return self.paginator.pages
        
    @property
    def prev(self):
        page = self.index - 1
        if self.paginator.has_page(page):
            return page
        return None

    @property
    def next(self):
        page = self.index + 1
        if self.paginator.has_page(page):
            return page
        return None



class SqlAlchemyPaginator(Paginator):
    
    def slice(self, offset, limit):
        return list(self.cursor.offset(offset).limit(limit))

    def count(self):
        return self.cursor.count()


class PymongoPaginator(Paginator):
    
    def slice(self, offset, limit):
        return list(self.cursor.clone()[offset:offset+limit])

    def count(self):
        return self.cursor.count()


###

import marshmallow as ma


class SerializerOpts(ma.schema.SchemaOpts):
    def __init__(self, meta):
        super(SerializerOpts, self).__init__(meta)
        try:
            self.contents_serializer_class = getattr(meta, 'contents_serializer_class')
        except AttributeError:
            raise ma.exceptions.MarshmallowError(
                'Must specify `contents_serializer_class` option '
                'in class `Meta` of `PaginationSerializer`.'
            )
        self.contents_field_name = getattr(meta, 'contents_field_name', 'contents')
        self.contents_serializer_options = getattr(meta, 'contents_serializer_options', {})


class PaginationSerializer(ma.Schema):

    OPTIONS_CLASS = SerializerOpts

    def __init__(self, *args, **kwargs):
        super(PaginationSerializer, self).__init__(*args, **kwargs)
        field = ma.fields.Nested(
            self.opts.contents_serializer_class, 
            many=True, 
            **self.opts.contents_serializer_options
        )
        self.declared_fields[self.opts.contents_field_name] = field

    next = ma.fields.Field()
    prev = ma.fields.Field()
    pages = ma.fields.Integer()


class PlayerSerializer(ma.Schema):
    name = ma.fields.String()


class PlayerPaginationSerializer(PaginationSerializer):
    
    class Meta:
        contents_field_name = 'contents'
        contents_serializer_class = PlayerSerializer