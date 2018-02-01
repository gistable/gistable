from itertools import product
from sys import argv
from random import shuffle
from urllib.request import urlopen
from urllib.error import HTTPError


def main(args):
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    combinations = [''.join(i) for i in product(letters, repeat=(int(args[1]) if len(args) > 1 else 2))]

    shuffle(combinations)

    for username in combinations:
        try:
            urlopen('https://github.com/' + username)
        except HTTPError:
            print(username + " is available!")


if __name__ == '__main__':
    main(argv)
