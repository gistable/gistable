import argparse

def get_domains(nr, how_many):
    bases = {
        1: {
            'length': 7,
            'tld': 'com',
            'key': '1676d5775e05c50b46baa5579d4fc7',
            'base': 0x45AE94B2
        },
        2: {
            'length': 5,
            'tld': 'eu',
            'key': '1670cf21500911e1758e2b0dd5b4',
            'base': 0x45AE94B2
        },
        3: {
            'length': 7,
            'tld': 'info',
            'key': '167cd47c0a09c9036d6097b754ab2e73',
            'base': 0x45AE94B2
        },
        4: {
            'length': 7,
            'tld': 'info',
            'key': 2038,
            'base': 0x45AE94B2
        }, 
        5: {
            'length': 11,
            'tld': 'eu',
            'key': "1670cf215403c56d8859a0636ffc74",
            'base': 0x45AE94B2
        }, 
        6: {
            'length': 7,
            'tld': 'info',
            'key': 2182,
            'base': 0x45AE94B2
        }
    }

    consonants = "qwrtpsdfghjklzxcvbnmv"
    vowels = "eyuioa"

    length = bases[nr]['length']
    tld = bases[nr]['tld']
    key = bases[nr]['key']
    base = bases[nr]['base']


    if type(key) == int:
        step = key
    else:
        step = 0
        for m in key:
            step += ord(m)

    for nr in range(how_many):
        domain = ""
        base += step

        for i in range(length):
            index = int(base/(3+2*i))
            if i % 2 == 0:
                char = consonants[index % 20]
            else:
                char = vowels[index % 6]
            domain += char

        domain += "." + tld
        print(domain)

if __name__=="__main__":
    parser = argparse.ArgumentParser("dga of Simda/Shiz")
    parser.add_argument("nr", type=int, choices=range(1,7), 
            help="which base set")
    parser.add_argument("-c", "--count", type=int, default=10,
            help="how many domains")
    args = parser.parse_args()
    get_domains(args.nr, args.count)

