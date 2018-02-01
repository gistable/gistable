import sys

def split_line(line):
    cols = line.split("\t")
    return cols

def get_words(cols):
    words_ids = cols[4].split(" ")
    words = [w.split("#")[0] for w in words_ids]
    return words

def get_positive(cols):
    return cols[2]

def get_negative(cols):
    return cols[3]

def get_objective(cols):
    return 1 - (float(cols[2]) + float(cols[3]))

def get_gloss(cols):
    return cols[5]

def get_scores(filepath, word):

    f = open(filepath)
    for line in f:
        if not line.startswith("#"):
            cols = split_line(line)
            words = get_words(cols)

            if word in words:
                print("For given word {0} - {1}".format(word, get_gloss(cols)))
                print("P Score: {0}".format(get_positive(cols)))
                print("N Score: {0}".format(get_negative(cols)))
                print("O Score: {0}\n".format(get_objective(cols)))

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("USAGE: {0} <path to SentiWordNet>".format(sys.argv[0]))
        exit(1)

    word = input("Enter a word: ")
    get_scores(sys.argv[1], word.lower())
