# based on https://github.com/google/seq2seq/blob/master/bin/tools/generate_beam_viz.py

# extracts probabilities and sequences from .npz file generated during beam search. 
# and pickles a list of the length n_samples that has beam_width most probable tuples 
# (path, logprob, prob) 
# where probs are scaled to 1. 

import numpy as np
import networkx as nx
import pickle
import tqdm

import os


def draw_graph(graph):
    from string import Template
    import shutil
    from networkx.readwrite import json_graph
    import json
    
    HTML_TEMPLATE = Template("""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Beam Search</title>
        <link rel="stylesheet" type="text/css" href="tree.css">
        <script src="http://d3js.org/d3.v3.min.js"></script>
      </head>
      <body>
        <script>
          var treeData = $DATA
        </script>
        <script src="tree.js"></script>
      </body>
    </html>""")
    
    seq2seq_path = '/scratch/make_build/gram_as_foreight_lang/seq2seq'
    vis_path = base_path+'/vis/graph_beam/'
    os.makedirs(base_path+'/vis/graph_beam/', exist_ok=True)
    shutil.copy2(seq2seq_path+"/bin/tools/beam_search_viz/tree.css", vis_path)
    shutil.copy2(seq2seq_path+"/bin/tools/beam_search_viz/tree.js", vis_path)
    
    json_str = json.dumps(json_graph.tree_data(graph, (0, 0)), ensure_ascii=False)

    html_str = HTML_TEMPLATE.substitute(DATA=json_str)
    output_path = os.path.join(vis_path, "graph.html")
    with open(output_path, "w") as file:
        file.write(html_str)
    print(output_path)


def _add_graph_level(graph, level, parent_ids, names, scores):
    """Adds a levelto the passed graph"""
    for i, parent_id in enumerate(parent_ids):
        new_node = (level, i)
        parent_node = (level - 1, parent_id)
        graph.add_node(new_node)
        graph.node[new_node]["name"] = names[i]
        graph.node[new_node]["score"] = str(scores[i])
        graph.node[new_node]["size"] = 100
        # Add an edge to the parent
        graph.add_edge(parent_node, new_node)


def create_graph(predicted_ids, parent_ids, scores, vocab=None):
    def get_node_name(pred):
        return vocab[pred] if vocab else str(pred)
    
    seq_length = predicted_ids.shape[0]
    graph = nx.DiGraph()
    for level in range(seq_length):
        names = [get_node_name(pred) for pred in predicted_ids[level]]
        _add_graph_level(graph, level + 1, parent_ids[level], names, scores[level])
    graph.node[(0, 0)]["name"] = "START"
    return graph


def get_path_to_root(graph, node):
    p = graph.predecessors(node)
    assert len(p) <= 1
    self_seq = [graph.node[node]['name'].split('\t')[0]]
    if len(p) == 0:
        return self_seq
    else:
        return self_seq + get_path_to_root(graph, p[0])
    

def main(data_fn, vocab_fn, output_fn, target_fn):
    beam_data = np.load(data_fn)
    to_dump = []
    
    # Optionally load vocabulary data
    vocab = None
    if vocab_fn:
        with open(vocab_fn) as file:
            vocab = file.readlines()
        vocab = [_.strip() for _ in vocab]
        vocab += ["UNK", "SEQUENCE_START", "SEQUENCE_END"]
        
    data_len = len(beam_data["predicted_ids"])
    print(data_len)
    
    with open(target_fn) as f_target:
        targets = f_target.readlines()

    data_iterator = zip(beam_data["predicted_ids"],
                        beam_data["beam_parent_ids"],
                        beam_data["scores"],
                        targets)
    
    def _tree_node_predecessor(pos):
        return graph.node[graph.predecessors(pos)[0]]
    
    n_correct_top_5 = 0
    correct_probs = []
    for predicted_ids, parent_ids, scores, target in tqdm.tqdm(data_iterator, total=data_len):
        graph = create_graph(
                predicted_ids=predicted_ids,
                parent_ids=parent_ids,
                scores=scores,
                vocab=vocab)
        
        pred_end_node_names = {pos for pos, d in graph.node.items()
                               if d['name'] == 'SEQUENCE_END'
                               and len(graph.predecessors(pos)) > 0
                               and _tree_node_predecessor(pos)['name'] != 'SEQUENCE_END'}

        result = [(tuple(get_path_to_root(graph, pos)[1:-1][::-1]), 
                   float(graph.node[pos]['score']))
                  for pos in pred_end_node_names]
        
        filtered_result = filter(lambda x: 'SEQUENCE_END' not in x[0], result)

        s_result = sorted(filtered_result, key=lambda x: x[1], reverse=True)
        nn_probs = np.exp(np.array(list(zip(*s_result))[1]))
        probs = nn_probs / np.sum(nn_probs)
        result_w_prob = [(path, score, prob) for (path, score), prob in zip(s_result, probs)]
        if len(result_w_prob) < 5:
            result_w_prob.extend([(('SEQUENCE_END', ), np.nan, 0)]*(5-len(result_w_prob)))
        to_dump.append(result_w_prob[:5])
    
    with open(output_fn, 'wb') as f_out:
        pickle.dump(to_dump, f_out)
