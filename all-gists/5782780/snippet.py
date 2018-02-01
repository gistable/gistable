#
# orange_custom_tree.py
# Module implementing a custom version of Orange's TreeLearner which "forces"
# the first split to the specified attribute.
#
# Copyright (C) 2013 Tadej Janez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s): Tadej Janez <tadej.janez@tadej.hicsalta.si>
#

import Orange
import Orange.classification.tree as octree
import Orange.feature.scoring as fscoring

class ForcedFirstSplitTreeLearner(octree.TreeLearner):
    
    """A custom version of Orange.classification.tree.TreeLearner which "forces"
    the first split to the specified attribute.
    
    """
        
    def __init__(self, first_split_attr=None, **kwargs):
        """Initialize the ForcedFirstSplitTreeLearner.
        
        Keyword arguments:
        first_splitt_attr -- string representing the name of the attribute to
            be used for the first split
        kwargs -- dictionary of keyword arguments passed to the standard
            Orange.classification.tree.TreeLearner
        
        """
        self.first_split_attr = first_split_attr
        super(ForcedFirstSplitTreeLearner, self).__init__(**kwargs)
    
    def _new_tree_node(self, instances):
        """Create a new Orange.classification.tree.Node object for the given
        instances. Compute the node's contingency table, distribution and
        classifier. Return the constructed Orange.classification.tree.Node
        object. 
        
        Arguments:
        instances -- Orange.data.Table holding instances corresponding to this
            tree node
        
        """
        node = octree.Node()
        node.examples = instances
        node.contingency = Orange.statistics.contingency.Domain(instances)
        node.distribution = node.contingency.classes
        if self.base_learner.node_learner != None:
            node_learner = self.base_leaner.node_learner
        else:
            node_learner = Orange.classification.majority.MajorityLearner() 
        node.node_classifier = node_learner(instances)
        return node
    
    def __call__(self, instances, weight=0):
        """Build a decision tree for the given instances according to the
        specified parameters.
        Return an Orange.classification.tree.TreeClassfier object with the
        constructed tree.
        
        Arguments:
        instances -- Orange.data.Table holding learning instances
        
        Keyword arguments:
        weight -- meta attribute with weights of instances (optional)
        
        """
        # create an (internal) Orange.core.TreeLearner object
        bl = self._base_learner()
        self.base_learner = bl

        # set the scoring criteria if it was not set by the user
        if not self._handset_split and not self.measure:
            if instances.domain.class_var.var_type == Orange.data.Type.Discrete:
                measure = fscoring.GainRatio()
            else:
                measure = fscoring.MSE()
            bl.split.continuous_split_constructor.measure = measure
            bl.split.discrete_split_constructor.measure = measure
        # set the splitter if it was set by the user
        if self.splitter != None:
            bl.example_splitter = self.splitter
        
        # set up a boolean list with one entry for each feature and select the
        # (single) feature that the SplitConstructor should consider
        candidate_feat = [feat.name == self.first_split_attr for feat in
                          instances.domain]
        # create the tree's root node
        root_node = self._new_tree_node(instances)
        # call the SplitConstructor for the root node manually
        bs, bd, ss, quality, spent_feature = self.split(instances, weight,
            root_node.contingency, root_node.distribution, candidate_feat,
            root_node.node_classifier)
        root_node.branch_selector = bs
        root_node.branch_descriptions = bd
        root_node.branch_sizes = ss
        # split the examples into subsets by calling the appropriate Splitter
        if self.splitter != None:
            splitter = self.splitter
        else:
            splitter = octree.Splitter_IgnoreUnknowns()
        subsets = splitter(root_node, root_node.examples)[0]
        # build a sub-tree for each subset (which is not None) and store it as
        # a branch of the root_node
        root_node.branches = []
        for subset in subsets:
            if subset != None:
                subtree = bl(subset, weight)
                root_node.branches.append(subtree.tree)
        # create an (internal) Orange.core.TreeClassifier object
        descender = getattr(self, "descender", octree.Descender_UnknownMergeAsBranchSizes())
        tree = octree._TreeClassifier(domain=instances.domain, tree=root_node,
                                      descender=descender)
        
        # perform post pruning
        if getattr(self, "same_majority_pruning", 0):
            tree = Pruner_SameMajority(tree)
        if getattr(self, "m_pruning", 0):
            tree = Pruner_m(tree, m=self.m_pruning)
        
        return octree.TreeClassifier(base_classifier=tree)

if __name__ == "__main__":
    data = Orange.data.Table("titanic")
    nt = octree.TreeLearner(data)
    print "'Normal' TreeLearner:"
    print nt # should have the 'sex' attribute as the first split
    print
    
    ffst = ForcedFirstSplitTreeLearner(data, first_split_attr="age")
    print "ForcedFirstSplitTreeLearner:"
    print ffst # should have 'age' attribute as the first split
