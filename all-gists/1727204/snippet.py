# -*- coding: utf-8 -*-

"""
Whoosh backend for haystack that implements character folding, as per 
http://packages.python.org/Whoosh/stemming.html#character-folding .

Tested with Haystack 2.4.0 and Whooch 2.7.0

To use, put this file on your path and add it to your haystack settings, eg.

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'folding_whoosh_backend.FoldingWhooshEngine',
            'PATH': 'path-to-whoosh-index',
        },
    }
"""

from haystack.backends.whoosh_backend import WhooshEngine, WhooshSearchBackend
from whoosh.analysis import CharsetFilter, StemmingAnalyzer
from whoosh.support.charset import accent_map
from whoosh.fields import TEXT


class FoldingWhooshSearchBackend(WhooshSearchBackend):
    
    def build_schema(self, fields):
        schema = super(FoldingWhooshSearchBackend, self).build_schema(fields)
        
        for name, field in schema[1].items():
            if isinstance(field, TEXT):
                field.analyzer = StemmingAnalyzer() | CharsetFilter(accent_map)
                
        return schema


class FoldingWhooshEngine(WhooshEngine):
    backend = FoldingWhooshSearchBackend
