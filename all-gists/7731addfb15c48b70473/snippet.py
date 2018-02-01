"""
To use:

1. Install virtualenv and pip - probably best done via your package manager:

        sudo apt-get install python-pip python-virtualenv
        
2. `virtualenv stupidaibot`
3. `source stupidaibot/bin/activate`
4. save this file somewhere (if you haven't already)
5. `pip install nltk numpy` (takes a little while)
6. `python nltk_bot.py`
7. argue
"""

import os
import imp
_, nltk_path, _ = imp.find_module("nltk")
datapath = os.path.join(nltk_path, "datastructures")
try:
    os.makedirs(datapath)
except OSError:
    pass
os.environ["NLTK_DATA"] = datapath
try:
    import nltk
except:
    print __doc__
    import sys
    sys.exit(1)
nltk.data.path = [datapath]


#nltk.download("words")
#nltk.download("maxent_treebank_pos_tagger")
#nltk.download("maxent_ne_chunker")




sentence = " this   isn't another sample\nsentence, is it?"
start = ("", "", "BEGIN")
end = ("", "", "END")

def tag(sentence):
    s = " ".join(sentence.strip().split())
    tokens = nltk.word_tokenize(sentence)
    tagged_tokens = nltk.pos_tag(tokens)

    position = 0
    prefix_tokens = [start]
    for token, tag in tagged_tokens:
        # miniparser to find stuff between tokens
        nextpos = s.index(token, position)
        prefix = ""
        if nextpos > position:
            prefix = s[position:nextpos]
        position = nextpos + len(token)
        prefix_tokens.append((prefix, token, tag))
    prefix_tokens.append(end)

    return prefix_tokens, tagged_tokens

def print_tags(sentence, output_prefix="", strip_begin=True):
    words = []
    wtags = []
    for prefix, word, tag in sentence:
        if tag in ("BEGIN", "END"):
            continue
        length = len(word)
        if length <= len(tag):
            tag += " "
            length = max(len(word), len(tag))
            spaces = ' ' * (length - len(word))
            word += spaces

        tag += " " * (length - len(tag))
        tag = (" " * len(prefix)) + tag
        word = prefix + word
        words.append(word)
        wtags.append(tag)


    words = output_prefix + ' ' + "".join(words)
    wtags = output_prefix + ' ' + "".join(wtags)
    return words + "\n" + wtags

import pprint


def test_tag():
    prefixed, tagged = tag("this  isn't a whacky\n sentence, is it?!")
    result = "".join(prefix + token for prefix, token, tag in prefixed)
    assert result == "this isn't a whacky sentence, is it?!"






# adapted code from markov bot starts here:


from collections import defaultdict
import random
import time

description = random.choice(["Him", "Her"])

def generate(chain):
    result = [start]
    while result[-1] != end:
        result.append(random.choice(chain[result[-1]]))
    return result

def format_sentence(result):
    line = "".join([x[0] + x[1] for x in result if x not in (start, end)])
    return line

def add(chain, line):
    split, tagged = tag(line)
    for index, x in enumerate(split[:-1]):
        chain[x].append(split[index+1])
    return split

def main(log):
    seed = random.randint(1, 10000)
    random.seed(seed)
    log.write("random seed: %r\n" % seed)
    chain = defaultdict(list)

    lines = [
        "Come in.",
        "I told you once.",
        "Yes I have.",
        "Just now.",
        "Yes I did.",
        "I did!",
        "I'm telling you I did!",
        "Oh, I'm sorry. Is this a five minute argument or the full half hour?",
        "Thank you. Anyway, I did.",
        "Now, let's get this thing clear; I most definitely told you.",
        "Yes I did.",
        "Yes I did.",
        "Yes I did.",
        "Yes I did.",
        "Did.",
        "Yes it is.",
        "No it isn't.",
        "It is not.",
        "No I didn't.",
        "No, no, no.",
        "No no, nonsense!",
        "No it isn't.",
        "No you didn't; no, you came here for an argument.",
        "Can be.",
        "No it isn't.",
        "Look, if I argue with you, I must take up a contrary position. ",
        "Yes it is!",
        "Yes it is!",
        "No it isn't.",
        "Not at all.",
        "Thank you! Good Morning.",
        "That's it. Good morning.",
        "Sorry, the five minutes is up.",
        "I'm afraid it was.",
        "I'm sorry, I'm not allowed to argue anymore.",
        "If you want me to go on arguing, you'll have to pay for another five minutes.",
        "Well I'm very sorry, but I told you I'm not allowed to argue unless you've paid!",
        "Thank you.",
        "Well what?",
        "I told you, I'm not allowed to argue unless you've paid.",
        "No you didn't.",
        "No you didn't.",
        "Well, I'm very sorry, but you didn't pay.",
        "No you haven't.",
        "Not necessarily. I could be arguing in my spare time.",
        "No you haven't.",
    ]

    for line in lines:
        add(chain, line)

    while True:
        try:
            line = raw_input("You: ")
        except (KeyboardInterrupt, EOFError):
            break

        log.write("You: %r\n" % line)

        result = add(chain, line)
        tag_fmt = print_tags(result, "You:")
        log.write(tag_fmt)

        result = generate(chain)
        tag_fmt = print_tags(result, description + ":")
        log.write(tag_fmt)

        response = format_sentence(result)

        log.write("%s: %r\n" % (description, response))
        print "%s: %s" % (description, response)
    print

if __name__ == "__main__":
    #test_tag()

    with open("markov-log-%d.txt" % time.time(), "w") as log:
        main(log)