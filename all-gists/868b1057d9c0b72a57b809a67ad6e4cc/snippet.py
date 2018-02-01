from collections import defaultdict
from ete3 import PhyloTree, TreeStyle, SeqMotifFace, TextFace, RectFace

alg = """
>Dme_001
MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEAL--YYASQTDDIKDRREEAH
>Dme_002
MAEIPDATIQQFMALTNVSHNIAVQY--EFGDLNEALNSYYAYQTDDQKDRREEAH
>Cfa_001
MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
>Mms_001
MAEAPDETIQQFMALTNVSHNIAVQYLSEFGDLNEAL--------------REEAH
>Hsa_001
MAEIPDETIQQFMALT---HNIAVQYLSEFGDLNEALNSYYASQTDDIKDRREEAH
>Ptr_002
MAEIPDATIQ-FMALTNVSHNIAVQY--EFGDLNEALNSY--YQTDDQKDRREEAH
>Mmu_002
MAEIPDATIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
>Hsa_002
MAEAPDETIQQFM-LTNVSHNIAVQYLSEFGDLNEAL--------------REEAH
>Ptr_001
MAEIPDATIQ-FMALTNVSHNIAVQY--EFGDLNEALNSY--YQTDDQKDRREEAH
>Mmu_001
MAEIPDTTIQ---ALTNVSHNIAVQYLSEFGDLNEALNSYYASQTDDQPDRREEAH
"""

def mutation_columns(sequences):
    col2diffs = defaultdict(set)
    alg_length = len(sequences[0])
    for col in xrange(alg_length):
        for seq in sequences:
            col2diffs[col].add(seq[col])
        col2diffs[col].discard('-')
    subseqs = set()
    relevant_columns = []
    for col in xrange(alg_length):
        if len(col2diffs[col]) > 1:
            relevant_columns.append(col)
    for seq in sequences:
        subseqs.add(''.join([seq[col] for col in relevant_columns]))

    return subseqs, relevant_columns

def get_example_tree():
    # Performs a tree reconciliation analysis
    gene_tree_nw = '((Dme_001,Dme_002),(((Cfa_001,Mms_001),((Hsa_001,Ptr_001),Mmu_001)),(Ptr_002,(Hsa_002,Mmu_002))));'
    t = PhyloTree(gene_tree_nw)
    ts = TreeStyle()
    # disable default PhyloTree Layout
    ts.layout_fn = lambda x: True

    t.link_to_alignment(alg)
    node2content = t.get_cached_content()
    for node in t.traverse():
        node.img_style["size"] = 0

        if not node.is_leaf():
            leaves = node2content[node]
            # get columns with different aa
            subseqs, relevant_columns  = mutation_columns([lf.sequence for lf in leaves])
            for seq in subseqs:
                f = SeqMotifFace(seq, seq_format="seq", width=10, height=8)
                f.margin_top = 2
                f.margin_right = 6
                node.add_face(f, column=0, position="branch-bottom")
            for j, col in enumerate(relevant_columns):
                col_f = RectFace(10, 10, fgcolor=None, bgcolor=None,
                                 label={"text":str(col), "fonttype":"Courier", "color":"black", "fontsize":6})
                node.add_face(col_f, column=j, position="branch-top")
                col_f.margin_bottom = 2
        else:
            f = SeqMotifFace(node.sequence, seq_format="seq", width=6)
            node.add_face(f, column=0, position="aligned")

    alg_length = len(lf.sequence)
    ts.draw_aligned_faces_as_table = False
    for colnum in xrange(alg_length):
        col_f = RectFace(10, 10, fgcolor=None, bgcolor=None,
                         label={"text":str(colnum), "fonttype":"Courier", "color":"black", "fontsize":6})
        ts.aligned_header.add_face(col_f, column=colnum)
    return t, ts

if __name__ == "__main__":
    t, ts = get_example_tree()
    t.show(tree_style=ts)