import networkx as nx
from networkx.readwrite import d3_js

mikedewar = nx.read_graphml('mikedewar_rec.graphml')
	
# We need to relabel nodes as Twitter name if we want to show the names in the plot
label_dict = dict(map(lambda i : (mikedewar.nodes()[i], mikedewar.nodes(data=True)[i][1]['Label']), xrange(mikedewar.number_of_nodes())))
mikedewar_d3 = nx.relabel_nodes(mikedewar, label_dict)	

# Export 
d3_js.export_d3_js(mikedewar_d3, files_dir="mikedewar", graphname="mikedewar", group="REC", node_labels=False)