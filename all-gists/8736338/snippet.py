import sys
import os
from collections import defaultdict
import calc_dists_to_top_of_GO
import calc_dists_to_top_of_GO_using_bfs

class Error (Exception): pass
      
#====================================================================#

# define a function to find the last common ancestor(s) of a pair of GO terms:

def find_lcas_of_pair_of_GO_terms(term1, term2, parents):
    """find the last common ancestor(s) of a pair of GO terms"""
    
    VERBOSE = False
    
    # make a set to store the last common ancestor(s) of the pair of GO terms:
    lcas = set()
    
    # calculate a dictionary with the minimum distance from term1 to each ancestor above it in the GO hierarchy (including itself):
    dist1 = calc_dists_to_top_of_GO_using_bfs.BFS_dist_from_node(term1, parents)
    # eg. for GO:0001578: {'GO:0008150': 5, 'GO:0009987': 4, 'GO:0001578': 0, 'GO:0071840': 5, 'GO:0000226': 1, 'GO:0044699': 4, 
    #                      'GO:0044763': 3, 'GO:0007017': 2, 'GO:0006996': 3, 'GO:0016043': 4, 'GO:0007010': 2}
    
    # calculate a dictionary with the minimum distance from term2 to each ancestor above it in the GO hierarchy (including itself):
    dist2 = calc_dists_to_top_of_GO_using_bfs.BFS_dist_from_node(term2, parents)
    # eg. for GO:0030036: {'GO:0008150': 4, 'GO:0044699': 3, 'GO:0071840': 4, 'GO:0007010': 1, 'GO:0030029': 1, 'GO:0044763': 2, 
    #                      'GO:0009987': 3, 'GO:0006996': 2, 'GO:0016043': 3, 'GO:0030036': 0}
    if VERBOSE:
        print("dist1=", dist1)
        print("dist2=", dist2)
        
    BIGNUM = 9999999999
    
    while True:
        bestnodes = []
        mindist = BIGNUM
        
        # find the set of common ancestors of term1 and term2 (if one is a parent of the other, it will be included in the intersection):
        common_ancestors = set(dist1.keys()) & set(dist2.keys())
        # eg. for GO:0001578 and GO:0030036, the first time around the while loop (before deleting any keys from the dist1 and dist2
        # dictionaries), we find the common ancestors: GO:0008150, GO:0009987, GO:0071840, GO:0044699, GO:0044763, GO:0006996, GO:0016043, GO:0007010
        if VERBOSE:
            print("common ancestors=",common_ancestors)
        
        # for each common ancestor of term1 and term2, find the distance to to the common ancestor: this is the
        # sum of the minimum distance from term1 to the ancestor and the minimum distance from term2 to the ancestor:
        for common_ancestor in common_ancestors:
            totdist = dist1[common_ancestor] + dist2[common_ancestor]
            if totdist < mindist: # if this ancestor is closer than the closest ancestor found so far
                bestnodes = [common_ancestor]
                mindist = totdist
            elif totdist == mindist: # this ancestor is as close as the closest ancestor found so far
                bestnodes.append(common_ancestor) 

        if mindist == BIGNUM: break # this occurs if we didn't find any common ancestor that was closer than BIGNUM
                                    # eg. this occurs the second time around the loop for GO:0001578 and GO:0030036. We quit then.

        # Add the 'bestnodes' found to the set 'lcas':
        lcas.update(bestnodes) 
        
        if VERBOSE: 
            print("Common ancestor(s):", bestnodes)
        # eg. for GO:0001578 and GO:0030036, the first time around the while loop (before deleting any keys from the dist1 and dist2
        # dictionaries), we find the bestnode to be GO:0007010. The ancestors of GO:0007010 are GO:0006996, GO:0016043, GO:0071840,
        # GO:0008150, GO0009987, GO:0007010, GO:0044763, GO:0044699.

        # wipe out the distance to the nodes in 'bestnodes' and all their ancestors from the dist1 and dist2 dictionaries:
        for bestnode in bestnodes:
            bestnode_ancestors = set(calc_dists_to_top_of_GO_using_bfs.BFS_dist_from_node(bestnode, parents).keys())
            for bestnode_ancestor in bestnode_ancestors:
                if bestnode_ancestor in dist1:
                    del dist1[bestnode_ancestor]
                if bestnode_ancestor in dist2:
                    del dist2[bestnode_ancestor]
        # eg. for GO:0001578 and GO:0030036, the first time around the while loop we get that 'bestnode = GO:0007010. When
        # we delete this term and its ancestors from the dist1 and dist2 dictionaries, we are left with:
        # dist1: {'GO:0001578': 0, 'GO:0000226': 1, 'GO:0007017': 2}
        # dist2: {'GO:0030029': 1, 'GO:0030036': 0}
          
        if VERBOSE:
            print("dist1 now=",dist1)
            print("dist2 now=",dist2)
            print("lcas=",lcas)
            
    return lcas
            
#====================================================================#

# define a function to find the common ancestor(s) of the GO terms for two genes, each of which has a list of GO terms:

def find_lcas_of_GO_terms_for_two_genes(gene1_terms, gene2_terms, parents):
    """find last common ancestor(s) of GO terms for two genes, each of which has a list of GO terms"""
    
    VERBOSE = False
        
    # define a set of the last common ancestor(s) of the GO terms in gene1_terms and gene2_terms:
    gene1_gene2_lcas = set() 
    
    for term1 in gene1_terms:
        for term2 in gene2_terms:
            # find the last common ancestor(s) of term1 and term2:
            term1_term2_lcas = find_lcas_of_pair_of_GO_terms(term1, term2, parents)
            if VERBOSE: 
                print("lcas for %s and %s=%s" % (term1, term2, term1_term2_lcas))
            # add the terms in 'term1_term2_lcas' to the set gene1_gene2_lcas:
            gene1_gene2_lcas.update(term1_term2_lcas)
    
    if VERBOSE:        
        print("gene1_gene2_lcas=",gene1_gene2_lcas)
        
    # remove any terms in gene1_gene2_lcas that are ancestors of other terms in the set: 
    # first make a copy of the set gene1_gene2_lcas:
    gene1_gene2_lcas2 = gene1_gene2_lcas.copy()
    
    for gene1_gene2_lca in gene1_gene2_lcas:
        # find all the ancestors of gene1_gene2_lca (also includes itself):
        gene1_gene2_ancestors = set(calc_dists_to_top_of_GO_using_bfs.BFS_dist_from_node(gene1_gene2_lca, parents).keys())
        for gene1_gene2_ancestor in gene1_gene2_ancestors:
            # remove gene1_gene2_ancestor from gene1_gene2_lcas2, if it is not the same term as gene1_gene2_lca:
            if gene1_gene2_ancestor in gene1_gene2_lcas2 and gene1_gene2_lca != gene1_gene2_ancestor:
                if VERBOSE: 
                    print("removing %s from gene1_gene2_lcas2 as it is an ancestor of %s" % (gene1_gene2_ancestor, gene1_gene2_lca) )
                gene1_gene2_lcas2.remove(gene1_gene2_ancestor)
        
    return gene1_gene2_lcas2
    
#====================================================================#

# define a function that, for several genes, each having a list of GO terms, finds
# the last common ancestor(s) of the GO terms for the list of genes:

def find_lcas_of_GO_terms_for_many_genes(gene_terms, parents):
    """find last common ancestor(s) of GO terms for many genes, each of which has a list of GO terms"""
    
    VERBOSE = False
    
    # find a list of the genes in dictionary gene_terms:
    genes = list(gene_terms.keys())
    assert(len(genes) > 0)

    # find the GO terms for a gene in the list 'genes':
    gene1 = genes.pop()
    gene1_terms = gene_terms[gene1] # note that gene1 is in dictionary gene_terms, as it's a key
    
    while len(genes) > 0:
        # get a gene from the list 'genes':
        gene2 = genes.pop()
        gene2_terms = gene_terms[gene2] # note that gene2 is in dictionary gene_terms, as it's a key
        # find the last common ancestor(s) of the GO terms of gene1 and gene2:
        gene1_gene2_lcas = find_lcas_of_GO_terms_for_two_genes(gene1_terms, gene2_terms, parents)
        if VERBOSE:
            print("lcas of GO terms %s and %s = %s" % (gene1_terms, gene2_terms, gene1_gene2_lcas))
        # set 'gene1_terms' to be a list of the terms in set gene1_gene2_lcas:
        gene1_terms = list(gene1_gene2_lcas)
        
    # define a set of the lcas of all the genes:
    lcas = set(gene1_terms)
    
    return lcas

#====================================================================#

def main():
    
    # check the command-line arguments:
    if len(sys.argv) != 2 or os.path.exists(sys.argv[1]) == False:
        print("Usage: %s go_desc_file" % sys.argv[0]) 
        sys.exit(1)
    go_desc_file = sys.argv[1]

    # read in the parents of each GO term in the GO hierarchy:
    (parents, terms) = calc_dists_to_top_of_GO.read_go_ancestors(go_desc_file)  
    
    # for a pair of GO terms of interest, find their last common ancestor(s):
    lcas = find_lcas_of_pair_of_GO_terms("GO:0001578", "GO:0030036", parents) # both are biological process terms
    print("lcas for GO:0001578 (microtubule bundle formation) and GO:0030036 (actin cytoskeleton organization)=",lcas)
    lcas2 = find_lcas_of_pair_of_GO_terms("GO:0004104", "GO:0003990", parents) # both are molecular function terms
    print("lcas for GO:0004104 (cholinesterase activity) and GO:0003990 (acetylcholinesterase activity)=",lcas2)
    lcas3 = find_lcas_of_pair_of_GO_terms("GO:0001578", "GO:0003990", parents) # one is biological process, one is molecular function
    print("lcas for GO:0001578 (microtubule bundle formation) and GO:0003990 (acetylcholinesterase activity)=",lcas3) 
    lcas4 = find_lcas_of_pair_of_GO_terms("GO:0004835", "GO:0003990", parents) # both are molecular function terms, but distant
    print("lcas for GO:0004835 (tubulin-tyrosine ligase activity) and GO:0003900 (acetylcholinesterase activity)=%s\n" % lcas4) # get GO:0003824 = 'molecular function'

    # for two genes, each having a list of GO terms, find the last common ancestor(s) of the GO terms for the two genes:
    gene1_terms = ['GO:0001578', 'GO:0004104', 'GO:0004835'] # could be a list of more than 2 terms
    gene2_terms = ['GO:0030036', 'GO:0003990'] # could be a list of more than 2 terms
    gene1_gene2_lcas = find_lcas_of_GO_terms_for_two_genes(gene1_terms, gene2_terms, parents)
    print("lcas for lists %s and %s = %s\n" % (gene1_terms, gene2_terms, gene1_gene2_lcas))
     
    # for several genes, each having a list of GO terms, find the last common ancestor(s) of the GO terms for the list of genes:
    # example 1:
    gene_terms = { 'gene1': ["GO:0003990", "GO:0004104"], 'gene2': ["GO:0003990", "GO:0004104"], 'gene3': ["GO:0004091"], 'gene4': ["GO:0003990", "GO:0004104", "GO:0004091"], 'gene5': ["GO:0004104"]}
    genes_lcas = find_lcas_of_GO_terms_for_many_genes(gene_terms, parents)
    print("example 1: lcas for genes = %s" % genes_lcas)
    # example 2:
    gene_terms = { 'C55A6.2': ["GO:0004835"], 'ZK1128.6': ["GO:0004835"], 'F25C8.5': ['GO:0004835'], 
                   'H23L24.3': ["GO:0004835"], 'K07C5.7': ["GO:0004835"]}
    genes_lcas = find_lcas_of_GO_terms_for_many_genes(gene_terms, parents)
    print("example 2: lcas for genes = %s" % genes_lcas)     
    # example 3:
    gene_terms = { 'T06E4.3': ["GO:0016303", "GO:0016773", "GO:0016772", "GO:0005515"],
                   'C48B6.6': ["GO:0016303", "GO:0016773", "GO:0005488", "GO:0016772", "GO:0005515"],
                   'B0261.2': ["GO:0008144", "GO:0016303", "GO:0016773", "GO:0005488", "GO:0016772", "GO:0005515"],
                   'Y48G1BL.2': ["GO:0016773", "GO:0016772", "GO:0005515"]}  
    genes_lcas = find_lcas_of_GO_terms_for_many_genes(gene_terms, parents)
    print("example 3: lcas for genes = %s" % genes_lcas)
      
#====================================================================#

if __name__=="__main__":
    main()

#====================================================================#


