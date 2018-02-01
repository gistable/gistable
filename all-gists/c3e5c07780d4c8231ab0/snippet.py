# wget https://raw.githubusercontent.com/bridgetkromhout/devops-against-humanity/b824d328392ea5c27026f917653e35da1b12b0f8/cards-DevOpsAgainstHumanity.csv

WHITE_CARDS = []
BLACK_CARDS = []
FILL_ME_IN = "_____"

from random import choice

def load():
    global WHITE_CARDS
    global BLACK_CARDS
    import csv
    f = open("./first-printing-cards-DevOpsAgainstHumanity.csv", 'r')
    reader = csv.reader(f)
    for r in reader:
        white = r[0]
        black = r[1]
        if white:
            WHITE_CARDS.append(white)
        if black:
            BLACK_CARDS.append(black)

def generate():
    generated_lulz = choice(BLACK_CARDS)
    #print "Chose card: " + generated_lulz
    #print ""
    while FILL_ME_IN in generated_lulz:
        generated_lulz = generated_lulz.replace(FILL_ME_IN, choice(WHITE_CARDS), 1)
    print generated_lulz

def main():
    load()
    print "DevOps Against Humanity"
    print "Hit enter for lulz, hit Ctrl+C if you get bored"
    print ""
    print ""
    raw_input()
    while True:        
        generate()
        raw_input()
        print ""


if __name__ == '__main__':
    main()
