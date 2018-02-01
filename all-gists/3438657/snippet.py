>>> import mapnik
>>> m = mapnik.Map(256,256)
>>> map_string = '''
... <Map>
...     <Layer name="layer" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
...         <Datasource>
...             <Parameter name="inline">
...             x,y,name
...             0,0,foo
...             1,1,foo
...             </Parameter>
...             <Parameter name="type">csv</Parameter>
...         </Datasource>
...     </Layer>
... </Map>
... '''
>>> mapnik.load_map_from_string(m,map_string)
>>> print len(m.layers)
1
>>> layer = m.layers[0]
>>> print layer
<mapnik._mapnik.Layer object at 0x105882950>
>>> print layer.datasource
<mapnik.Datasource object at 0x1058877d0>
>>> print dir(layer.datasource)
['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_c___module__', 'all_features', 'bind', 'describe', 'envelope', 'features', 'features_at_point', 'featureset', 'field_types', 'fields', 'geometry_type', 'params', 'type']
>>> print layer.datasource.all_features()[0].attributes
{'y': 0, 'x': 0, 'name': u'foo'}