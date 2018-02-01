import re
from collections import defaultdict

import nltk
from nltk.corpus import cmudict

def clean_pron(pron):
    """Remove stress from pronunciations."""
    return re.sub(r"\d", "", pron)


def make_triphones(pron):
    """Output triphones from a word's pronunciation."""
    if len(pron) < 3:
        return []
    # Junk on end is to make word boundaries work
    return ([((pron[idx - 2], pron[idx - 1]), pron[idx])
             for idx in range(2, len(pron))] + [(('#', '#'), pron[0])] +
            [((pron[-2], pron[-1]), '#')])
                                                


def triphone_probs(prons):
    """Calculate triphone probabilities for pronunciations."""
    context_counts = defaultdict(lambda: defaultdict(int))
    for pron in prons:
        for (context, phoneme) in make_triphones(pron):
            context_counts[context][phoneme] += 1
            
    for (context, outcomes) in context_counts.items():
        total_outcomes = sum(outcomes.values())
        for outcome, count in outcomes.items():
            context_counts[context][outcome] = float(count) / total_outcomes
        
    return context_counts

        
def main():
    """Compute some triphone probabilities."""
    pron_dict = cmudict.dict()
    prons = (map(clean_pron, pron) for prons in pron_dict.values()
             for pron in prons)

    triphones = triphone_probs(prons)
    context = ('IH', 'NG')
    outcomes = triphones[context]
    print context
    sorted_outcomes = sorted(outcomes.items(), key=lambda x: x[1], reverse=True)
    for outcome in sorted_outcomes:
        print "%s: %.4f" % outcome


if __name__ == "__main__":
    main()