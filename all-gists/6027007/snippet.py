def adj_iter(network, x):
    u"""network のノード x に隣接するエッジのイテレータを返す。
    素の edges_iter は存在しないノードに対してエラーを吐き面倒なので
    このジェネレータ関数で回避する。
    """

    if network.has_node(x):
        for t in network.edges_iter(x):
            yield t
    else:
        raise StopIteration