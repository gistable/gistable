#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

pip install networkx distance pattern 

In Flipboard's article[1], they kindly divulge their interpretation
of the summarization technique called LexRank[2].

While reading Flipboard's article, you can, if followed point by point, 
reimplement their summarization algorithm.
Here are the steps/excerpts that stood out to me:

    1. We model sentences as bags of words

    2. The strength of interaction... [can be measured by] standard
       metrics for this, such as Jaccard similarity...

    Note: We skip the normalization step
    3. The normalized adjacency matrix[3] of the graph is...

    4. We can compute the PageRank centrality measure for each sentence
       in the document.


[1] http://engineering.flipboard.com/2014/10/summarization/
[2] http://dl.acm.org/citation.cfm?id=1622501
[3] http://en.wikipedia.org/wiki/Adjacency_matrix
Note: The following pictures help visualize the mirrored for-loop(?):
http://en.wikipedia.org/wiki/Adjacency_matrix#Examples

I dont know what the technical name is for that double for-loop.
If anyone knows, please send your answers here:
https://twitter.com/rodricios
"""

import distance, operator
import networkx as nx
from pattern.en import tokenize
from pattern.vector import Document,LEMMA

def summarize(text_to_summarize):
    stokens = tokenize(text_to_summarize)

    # STEP 1
    # pattern.vector's Document is a nifty bag-o-words structure,
    # with a TF weighting scheme
    docs = [Document(string= s, name=e,stemmer=LEMMA)
            for e,s in enumerate(stokens) if len(s.split(" ")) > 7]
    
    linkgraph = []
    # STEP 2 and 3 happen interwovenly
    for doc in docs:
        for doc_copy in docs:
            if doc.name != doc_copy.name:
                # STEP 2 happens here
                wordset_a = [x[1] for x in doc.keywords()]
                wordset_b = [y[1] for y in doc_copy.keywords()]
                jacc_dist = distance.jaccard(wordset_a, wordset_b)
                if jacc_dist < 1:
                    linkgraph.append((str(doc.name), #index to sentence
                                      str(doc_copy.name),1-jacc_dist)) #dist. score
    # By the time we reach here, we'd have completed STEP 3
    
    # STEP 4
    #I referenced this SO post for help with pagerank'ing
    #http://stackoverflow.com/questions/9136539/how-to-weighted-edges-affect-pagerank-in-networkx
    D=nx.DiGraph()
    D.add_weighted_edges_from(linkgraph)
    pagerank = nx.pagerank(D)
    sort_pagerank = sorted(pagerank.items(),key=operator.itemgetter(1))
    sort_pagerank.reverse()
    top2 = sort_pagerank[:2]
    orderedtop2 = [int(x[0]) for x in top2]
    orderedtop2 = sorted(orderedtop2)
    return " ".join([ stokens[i] for i in orderedtop2 ])

if __name__ == "__main__":
    text = 'Someday I will have a place to put all my collections.\
                It will most likely be my basement, or a little corner of my \
                basement. But I didn\'t write Star Wars. If I had, I might be \
                able to build a museum on the sparkling lakefront of Chicago, \
                right next to Soldier Field. George Lucas did write Star Wars, \
                and his art and memorabilia collections will be housed in his \
                Museum of Narrative Art in the Windy City. Lucas just \
                announced that Beijing-based MAD Architects will design the \
                museum, while Chicago firm Studio Gang Architects will be \
                responsible for the surrounding landscape and a pedestrian \
                bridge that links nearby peninsula Northerly Island with the \
                city. It should be a stunning addition to the collection of \
                shoreline museums, but it has encountered opposition from \
                open-space advocates and Bears fans, as the museum will \
                occupy part of their tailgating field. In honor of the \
                Museum of Narrative Art and its star-studded cast of \
                architects, here\'s a roundup of articles from Architizer \
                that feature Star Wars-related architecture: Jeff Bennett\'s \
                Wars on Kinkade are hilarious paintings that ravage the \
                peaceful landscapes of Thomas Kinkade with the brutal \
                destruction of Star Wars. It is not unlike a contemporary \
                rendering, which combines Sci-fi and Romantic notions, and \
                we have examples with ratings. Ra di Martino, a visual artist \
                and filmmaker, found the ruins of Star Wars sets, and \
                photographed them in her two series, No More Stars (Star Wars) \
                and EVERY WORLD\'S A STAGE. These haunting images show a world \
                far, far away, now left as ghost towns. These haunting images \
                show a world far, far away, now left as ghost towns. We \
                explore the designs and the blueprints behind the architecture \
                of the Rebel Alliance and the Empire. Artist \u00E9 Delsaux \
                photoshops Star Wars characters and ships into everyday \
                environments. Stormtroopers roam parking lots, the Millennium \
                Falcon visits a Dubai construction site, and the Emperor lurks \
                in the suburbs. Aedas appropriates the Sandcrawler for an office \
                building, but replaces the weathered, rough brown material \
                (COR-TEN?) with shiny glass and the treads with landscaping. \
                The story of artist Ralph McQuarrie, the man who helped \
                George Lucas realize his visions.'
    print summarize(text)