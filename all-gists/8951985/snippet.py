import logging
import pylibmc

from werkzeug.contrib.cache import MemcachedCache

from flask import request
from flask.ext.cache import Cache

log = logging.getLogger(__name__)

mc = MemcachedCache()


class GrovemadeCache(Cache):
    '''
    Grovemade specific caching

    '''
    def get_generation(self):
        '''
        Incremenent generation to invalidate all keys.
        '''
        return mc.get('GENERATION-KEY')

    def inc_generation(self):
        try:
            mc.inc('GENERATION-KEY')
        except pylibmc.NotFound:
            mc.set('GENERATION-KEY', '1')  # memcached increments string integers


    def get_group_key(self, group):
        return u'GROUP-KEY:%s' % group

    def get_groups_key(self, groups):
        '''
        Get a generation key for a list of groups
        '''
        # groups_key = u''
        key_values = []
        for group in groups:
            group_key = self.get_group_key(group)
            group_version = mc.get(group_key)
            if group_version is None:
                group_version = '1'
                mc.set(group_key, group_version)
            key_values.append(group_version)
        groups_key = u':'.join(key_values)
        return groups_key

    def inc_group(self, group):
        '''
        Increment group. Call to invalidate cache for entire group.
        '''
        try:
            mc.inc(self.get_group_key(group))
        except pylibmc.NotFound:
            mc.set(self.get_group_key(group), '1')  # memcached increments string integers

    def build_group_key_prefix(self, groups=None):
        '''
        Generational caching strategy.
        Generation is global to all groups
        Groups are local to arbitrary groupings, such as "product" and "collection"
        All may be expired at will.
        '''
        if groups is None:
            groups = []
        return u'{generation}:{groups}'.format(
            groups=self.get_groups_key(groups),
            generation=self.get_generation(),
        )

    # def cached(self, timeout=None, key_prefix='view/%s', unless=None):
    def cached_generational(self, timeout=None, groups=None, key_prefix='view/%s', unless=None):
        '''
        Build generational cache key. Always vary on PJAX.
        '''
        def build_key():
            if callable(key_prefix):
                cache_key = key_prefix()
            elif '%s' in key_prefix:
                cache_key = key_prefix % request.path
            else:
                cache_key = key_prefix
             
            key = cache_key + self.build_group_key_prefix(groups) + request.headers.get('X-PJAX', '')
            return key
            # log.debug(u"Built group key: %s" % key)

        return self.cached(timeout=timeout, key_prefix=build_key, unless=None)

