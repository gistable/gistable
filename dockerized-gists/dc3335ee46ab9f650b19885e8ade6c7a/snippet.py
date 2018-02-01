#!/bin/python
from flashtext.keyword import KeywordProcessor
import random
import string
import re
import time


def get_word_of_length(str_length):
    # generate a random word of given length
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(str_length))

# generate a list of 100K words of randomly chosen size
all_words = [get_word_of_length(random.choice([3, 4, 5, 6, 7, 8])) for i in range(100000)]

print('Count  | FlashText | Regex    ')
print('-------------------------------')
for keywords_length in range(1, 20002, 1000):
    # chose 5000 terms and create a string to search in.
    all_words_chosen = random.sample(all_words, 5000)
    story = ' '.join(all_words_chosen)

    # get unique keywords from the list of words generated.
    unique_keywords_sublist = list(set(random.sample(all_words, keywords_length)))
    
    # compile regex
    # source: https://stackoverflow.com/questions/6116978/python-replace-multiple-strings
    rep = dict([(key, '_keyword_') for key in unique_keywords_sublist])
    compiled_re = re.compile("|".join(rep.keys()))

    # add keywords to flashtext
    keyword_processor = KeywordProcessor()
    for keyword in unique_keywords_sublist:
        keyword_processor.add_keyword(keyword, '_keyword_')

    # time the modules
    start = time.time()
    _ = keyword_processor.replace_keywords(story)
    mid = time.time()
    _ = compiled_re.sub(lambda m: rep[re.escape(m.group(0))], story)
    end = time.time()
    # print output
    print(str(keywords_length).ljust(6), '|',
          "{0:.5f}".format(mid - start).ljust(9), '|',
          "{0:.5f}".format(end - mid).ljust(9), '|',)

# Count  | FlashText | Regex    
# -------------------------------
# 1      | 0.02141   | 0.00004   |
# 1001   | 0.02498   | 0.13180   |
# 5001   | 0.03147   | 0.59799   |
# 10001  | 0.02858   | 1.08717   |
# 15001  | 0.02734   | 1.51461   |
# 20001  | 0.03109   | 1.76158   |