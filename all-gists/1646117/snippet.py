"""
From this paper: http://acl.ldc.upenn.edu/acl2004/emnlp/pdf/Mihalcea.pdf 

I used python with nltk, and pygraph to do an implmentation of of textrank.

for questions: http://twitter.com/voidfiles

"""
import nltk
import itertools
from operator import itemgetter

from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.pagerank import pagerank
from pygraph.classes.exceptions import AdditionError

text = u"""In the Valley, we have lots of euphemisms for changing your business until you find a way to make money: You might throw things at the wall and see what sticks, or go where the money is, or pivot. Whatever you call it, it boils down to a basic animal instinct-the killer instinct. You need to look at the whole picture and attack an area that is vulnerable, and then keep attacking until you have won, or until you find an even more vulnerable spot. Rinse, then repeat.

I have yet to run my own company, but that doesn't stop me from evaluating the ability of a business to harness its killer instinct and fuel its own expansion. I have worked for companies with and without this instinct. I like working for companies with a keen killer instinct.

This killer instinct directly relates to last month's Google Reader debacle. I would often deride Google for changing Reader, but at the same time, I knew from the beginning that it was the right move on the part of Google.

Google has amassed their resources to support Google+. They have gone so far as to tie employees' salaries and bonuses to how well Google+ does. They then rolled out integrations across the company. The company uses anything that could possibly prop up Google+ to drive the success of the project. This is the killer instinct in action. Google knows that if they don't combat Facebook, they are going to forfeit a significant market in the future. They aren't going to lose this battle without a fight.

As an outsider, and as a former Yahoo employee, I applaud Google's determination. Yahoo had been trying to start a social networking service for as long as I worked there. The problem with the Yahoo social networking plan is that they have tried five5 different things in five5 years. Apparently Google+ wasn't all that welcome at Google in it's internal beta, and there have even been some very public rants from Googlers about the faults of Google+,the project- but Google is still pushing it hard. If Yahoo ran had run into this much resistance, they would have shut it down.

Now that I work for a small company, I have had the chance to see killer instinct in the flesh. I know how much focus it gives a company, and that it drives the development of a strong plan. It gives you a roadmap, even when you don't always know what the future looks like. I can only hope that when I run my own company, I'll have that same killer instinct."""


text = nltk.word_tokenize(text)

tagged = nltk.pos_tag(text)


def filter_for_tags(tagged, tags=['NN', 'JJ', 'NNP']):
    return [item for item in tagged if item[1] in tags]


def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]


def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

tagged = filter_for_tags(tagged)
tagged = normalize(tagged)

unique_word_set = unique_everseen([x[0] for x in tagged])

gr = digraph()
gr.add_nodes(list(unique_word_set))

window_start = 0
window_end = 2

while 1:

    window_words = tagged[window_start:window_end]
    if len(window_words) == 2:
        print window_words
        try:
            gr.add_edge((window_words[0][0], window_words[1][0]))
        except AdditionError, e:
            print 'already added %s, %s' % ((window_words[0][0], window_words[1][0]))
    else:
        break

    window_start += 1
    window_end += 1

calculated_page_rank = pagerank(gr)
di = sorted(calculated_page_rank.iteritems(), key=itemgetter(1))
for k, g in itertools.groupby(di, key=itemgetter(1)):
    print k, map(itemgetter(0), g)
