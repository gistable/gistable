# syllables.py
# ------------

# get cmu_dict_file from http://webdocs.cs.ualberta.ca/~kondrak/cmudict.html

from collections import defaultdict

PHONEMES = set(['AA', 'AH', 'AW', 'B', 'D', 'EH', 'EY', 'G', 'IH', 'JH', 'L', 'N', 'OW' , 'P', 'S', 'T', 'UH', 'V', 'Y', 'ZH', 'AE', 'AO', 'AY', 'CH', 'DH' , 'ER', 'F', 'HH', 'IY', 'K', 'M', 'NG', 'OY', 'R', 'SH', 'TH' , 'UW', 'W', 'Z'])

VOWEL_PHONEMES = set(['AA', 'AH', 'AW', 'EH', 'ER', 'EY', 'IH', 'OW' , 'UH', 'AE', 'AO', 'AY', 'IY', 'OY', 'UW'])
CONSONANT_PHONEMES = PHONEMES - VOWEL_PHONEMES

pclean = lambda p: tuple(i.translate(None, '1234567890') for i in p)
pvowel = lambda p: tuple(i for i in p if i in VOWEL_PHONEMES)
pcons = lambda p: tuple(i for i in p if i in CONSONANT_PHONEMES)

def load_cmu_dict(cmu_dict_file):
    """
    Returns a dictionary of pronunciations. 
    Each value is a list of pronunciation tuples; 
    each pronunciation tuple contains syllable tuples;
    each syllable tuple contains phonemes.
    """
    raw_prons = {}
    with open(cmu_dict_file) as f:
        prev_word = ""
        for line in f:
            if line.startswith('##'): continue

            word, raw_pron = line.split('  ')

            # is this an alternative pronounciation for existing word?
            if word[-1] == ")" and word[-3] == "(":
                word = word[:-3].lower()
            else:
                word = word.lower()

            if word not in raw_prons:
                raw_prons[word] = []
           
            try:
                sylls = raw_pron.split('-')
                #raw_prons[word].append(tuple(pclean(s.split()) for s in sylls))
                raw_prons[word].append(tuple(s.split() for s in sylls))

            except KeyError:
                print("error on {}".format(word))
    return raw_prons
    
def rhyme(syll_1, syll_2):
    syll_1 = pclean(syll_1)
    syll_2 = pclean(syll_2)
    first_vowel = len(syll_1) - ''.join('V' if p in VOWEL_PHONEMES else 'C' for p in syll_1).index('V')
    v_syllable = syll_1[-first_vowel:]
    return ' '.join(syll_2).endswith(' '.join(v_syllable))

def vowel_change(syll_1, syll_2):
    syll_1 = pclean(syll_1)
    syll_2 = pclean(syll_2)
    placeholder = lambda x: ' '.join(ph if ph in CONSONANT_PHONEMES else "X" for ph in x )
    return placeholder(syll_1) == placeholder(syll_2)