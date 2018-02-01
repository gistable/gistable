import os
from functools import lru_cache
from collections import defaultdict

# Read in the taxonomy
class NCBITaxonomy():
    def __init__(self, folder):
        self.tax = defaultdict(dict)
        # Read in the file of taxid information
        names_fp = os.path.join(folder, 'names.dmp')
        assert os.path.exists(names_fp)
        with open(names_fp) as f:
            for line in f:
                line = line.strip('\n').split('\t')
                taxid = line[0]
                val = line[2]
                key = line[6]
                assert key != '', line
                self.tax[taxid][key] = val
        # Read in the file linking taxids to rank and parents
        nodes_fp = os.path.join(folder, 'nodes.dmp')
        assert os.path.exists(nodes_fp)
        with open(nodes_fp) as f:
            for line in f:
                line = line.strip('\n').split('\t')
                child = line[0]
                parent = line[2]
                child_rank = line[4]
                assert parent in self.tax, line
                self.tax[child]['rank'] = child_rank
                if parent != child:
                    self.tax[child]['parent'] = parent

        # Read in the "merged" taxids
        merged_fp = os.path.join(folder, 'merged.dmp')
        assert os.path.exists(merged_fp)
        with open(merged_fp) as f:
            for line in f:
                line = line.strip('\n').split('\t')
                old_taxid = line[0]
                new_taxid = line[2]
                assert new_taxid in self.tax
                # Link the old taxid to the new taxid
                self.tax[old_taxid] = self.tax[new_taxid]

    def info(self, taxid):
        assert taxid in self.tax
        return self.tax[taxid]

    def name(self, taxid):
        assert taxid in self.tax
        return self.tax[taxid]['scientific name']

    def rank(self, taxid):
        assert taxid in self.tax
        return self.tax[taxid]['rank']

    def path_to_root(self, taxid):
        visited = [taxid]
        while 'parent' in self.tax[taxid]:
            taxid = self.tax[taxid]['parent']
            if 'ancestors' in self.tax[taxid]:
                visited.extend(self.tax[taxid]['ancestors'])
                return visited
            assert taxid not in visited, visited
            visited.append(taxid)
        return visited

    def is_below(self, taxid, group_taxid):
        # Determine whether a taxid is part of a particular group
        assert taxid in self.tax, "Tax ID not found: {}".format(taxid)
        if 'ancestors' not in self.tax[taxid]:
            self.tax[taxid]['ancestors'] = self.path_to_root(taxid)

        return group_taxid in self.tax[taxid]['ancestors']
    
    @lru_cache(maxsize=None)
    def lca(self, taxid1, taxid2):
        # Return the lowest common ancestor of both taxid1 and taxid2
        # Get the list of ancestors for both taxids (starting at the root)
        anc1 = self.path_to_root(taxid1)[::-1]
        anc2 = self.path_to_root(taxid2)[::-1]
        # Both lists end at the root
        if anc1[0] != anc2[0]:
            logging.info("{} and {} not rooted on the same taxonomy, returning None".format(taxid1, taxid2))
            return None
        # Set the initial LCA as the root
        lca = anc1[0]

        # Walk down the list of ancestors until they no longer agree
        for a1, a2 in zip(anc1, anc2):
            # If the ancestors are in common, update the LCA
            if a1 == a2:
                lca = a1
            else:
                break

        return lca

    @lru_cache(maxsize=None)
    def anc_at_rank(self, taxid, rank):
        """Return the ancestor of this taxid at a specific rank."""
        # The result is potentially None (if `taxid` is above `rank`)
        if self.rank(taxid) == rank:
            return taxid
        for t in self.path_to_root(taxid):
            if self.rank(t) == rank:
                return t
        return None

    def domain(self, taxid):
        """Determine the broad organismal domain that a taxid belongs to."""
        ancestors = self.path_to_root(taxid)
        if "2" in ancestors:
            d = "Bacteria"
        elif "10239" in ancestors:
            d = "Viruses"
        elif "2157" in ancestors:
            d = "Archaea"
        elif "4751" in ancestors:
            d = "Fungi"
        elif "33208" in ancestors:
            d = "Metazoa"
        elif "33090" in ancestors:
            d = "Green plants"
        elif "2759" in ancestors:
            d = "Other Eukaryotes"
        else:
            d = "Non-microbial"
        return d

# tax = NCBITaxonomy('ncbi_taxonomy')