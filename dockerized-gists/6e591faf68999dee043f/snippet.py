import re
import string

def remove_punc(s):
    table = string.maketrans("","")
    s = s.translate(table, string.punctuation)
    return s

def clean_data(x):
    clean_x = remove_punc(x)
    clean_x = re.sub("(Mr|Mrs|Ms|Dr)", clean_x, "")
    return { "original_name": x, "clean_name": clean_x }