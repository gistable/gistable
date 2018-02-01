"""
myapp/mymodule.py:

from django.core.cache import cache

def set_cache():
    cache.set('foo', 'bar')
    
def get_cache():
    return cache.get('foo')

"""
from myapp.mymodule import set_cache, get_cache


with patch('myapp.mymodule.cache') as mock_cache:
    cache = {}
    
    def get(key, default=None):
      return cache.get(key, default)
    
    def _set(key, value, timeout=60):
      cache[key] = value
    
    mock_cache.get = get
    mock_cache.set = _set
    
    set_cache()
    
    self.assertEqual(cache['foo'], 'bar')
    self.assertEqual(get_cache(), 'bar')
