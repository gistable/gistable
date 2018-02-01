import fiona
import os

data_path = './transaction_simulator/shapefiles/gadm28_levels.gdb'

for layer_index, layer_name in enumerate(fiona.listlayers(data_path)):
    with fiona.open(data_path, layer=layer_index) as collection:
        print "Layer {0}, with Index {1} there are {2} features".format(layer_name, layer_index, len(collection))
