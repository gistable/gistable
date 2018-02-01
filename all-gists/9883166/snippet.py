"""
My Python spin on this:
http://burakkanber.com/blog/machine-learning-genetic-algorithms-in-javascript-part-2/
"""

import math
import random
import sys
from copy import copy
from optparse import OptionParser

elements = \
    {'Actinium': {'value': 317, 'weight': 149},
     'Aluminium': {'value': 343, 'weight': 195},
     'Americium': {'value': 365, 'weight': 66},
     'Antimony': {'value': 479, 'weight': 28},
     'Argon': {'value': 395, 'weight': 317},
     'Arsenic': {'value': 393, 'weight': 213},
     'Astatine': {'value': 210, 'weight': 392},
     'Barium': {'value': 417, 'weight': 307},
     'Berkelium': {'value': 458, 'weight': 289},
     'Beryllium': {'value': 387, 'weight': 405},
     'Bismuth': {'value': 497, 'weight': 33},
     'Bohrium': {'value': 479, 'weight': 236},
     'Boron': {'value': 174, 'weight': 12},
     'Bromine': {'value': 199, 'weight': 114},
     'Cadmium': {'value': 394, 'weight': 411},
     'Caesium': {'value': 416, 'weight': 361},
     'Calcium': {'value': 395, 'weight': 281},
     'Californium': {'value': 322, 'weight': 302},
     'Carbon': {'value': 483, 'weight': 298},
     'Cerium': {'value': 414, 'weight': 259},
     'Chlorine': {'value': 460, 'weight': 56},
     'Chromium': {'value': 295, 'weight': 299},
     'Cobalt': {'value': 249, 'weight': 288},
     'Copernicium': {'value': 460, 'weight': 251},
     'Copper': {'value': 314, 'weight': 91},
     'Curium': {'value': 407, 'weight': 393},
     'Darmstadtium': {'value': 344, 'weight': 308},
     'Dubnium': {'value': 187, 'weight': 168},
     'Dysprosium': {'value': 128, 'weight': 166},
     'Einsteinium': {'value': 94, 'weight': 455},
     'Erbium': {'value': 399, 'weight': 432},
     'Europium': {'value': 271, 'weight': 409},
     'Fermium': {'value': 347, 'weight': 216},
     'Fluorine': {'value': 306, 'weight': 414},
     'Francium': {'value': 253, 'weight': 433},
     'Gadolinium': {'value': 231, 'weight': 86},
     'Gallium': {'value': 254, 'weight': 470},
     'Germanium': {'value': 25, 'weight': 77},
     'Gold': {'value': 267, 'weight': 339},
     'Hafnium': {'value': 101, 'weight': 138},
     'Hassium': {'value': 353, 'weight': 201},
     'Helium': {'value': 380, 'weight': 309},
     'Holmium': {'value': 109, 'weight': 54},
     'Hydrogen': {'value': 400, 'weight': 389},
     'Indium': {'value': 329, 'weight': 322},
     'Iodine': {'value': 253, 'weight': 345},
     'Iridium': {'value': 68, 'weight': 121},
     'Iron': {'value': 360, 'weight': 422},
     'Krypton': {'value': 8, 'weight': 490},
     'Lanthanum': {'value': 453, 'weight': 291},
     'Lawrencium': {'value': 351, 'weight': 84},
     'Lead': {'value': 395, 'weight': 65},
     'Lithium': {'value': 424, 'weight': 339},
     'Lutetium': {'value': 224, 'weight': 311},
     'Magnesium': {'value': 98, 'weight': 327},
     'Manganese': {'value': 447, 'weight': 114},
     'Meitnerium': {'value': 307, 'weight': 278},
     'Mendelevium': {'value': 331, 'weight': 304},
     'Mercury': {'value': 438, 'weight': 259},
     'Molybdenum': {'value': 343, 'weight': 147},
     'Neodymium': {'value': 475, 'weight': 127},
     'Neon': {'value': 127, 'weight': 149},
     'Neptunium': {'value': 300, 'weight': 117},
     'Nickel': {'value': 482, 'weight': 458},
     'Niobium': {'value': 375, 'weight': 56},
     'Nitrogen': {'value': 303, 'weight': 409},
     'Nobelium': {'value': 236, 'weight': 49},
     'Osmium': {'value': 490, 'weight': 208},
     'Oxygen': {'value': 497, 'weight': 432},
     'Palladium': {'value': 387, 'weight': 353},
     'Phosphorus': {'value': 157, 'weight': 49},
     'Platinum': {'value': 29, 'weight': 182},
     'Plutonium': {'value': 455, 'weight': 106},
     'Polonium': {'value': 394, 'weight': 293},
     'Potassium': {'value': 221, 'weight': 383},
     'Praseodymium': {'value': 83, 'weight': 58},
     'Promethium': {'value': 480, 'weight': 11},
     'Protactinium': {'value': 50, 'weight': 457},
     'Radium': {'value': 109, 'weight': 303},
     'Radon': {'value': 203, 'weight': 116},
     'Rhenium': {'value': 141, 'weight': 480},
     'Rhodium': {'value': 428, 'weight': 418},
     'Roentgenium': {'value': 201, 'weight': 171},
     'Rubidium': {'value': 367, 'weight': 278},
     'Ruthenium': {'value': 214, 'weight': 325},
     'Rutherfordium': {'value': 233, 'weight': 345},
     'Samarium': {'value': 192, 'weight': 361},
     'Scandium': {'value': 79, 'weight': 394},
     'Seaborgium': {'value': 125, 'weight': 361},
     'Selenium': {'value': 96, 'weight': 419},
     'Silicon': {'value': 122, 'weight': 356},
     'Silver': {'value': 429, 'weight': 182},
     'Sodium': {'value': 341, 'weight': 247},
     'Strontium': {'value': 159, 'weight': 310},
     'Sulfur': {'value': 438, 'weight': 151},
     'Tantalum': {'value': 397, 'weight': 177},
     'Technetium': {'value': 105, 'weight': 123},
     'Tellurium': {'value': 305, 'weight': 443},
     'Terbium': {'value': 75, 'weight': 100},
     'Thallium': {'value': 425, 'weight': 342},
     'Thorium': {'value': 129, 'weight': 342},
     'Thulium': {'value': 395, 'weight': 361},
     'Tin': {'value': 436, 'weight': 490},
     'Titanium': {'value': 303, 'weight': 377},
     'Tungsten': {'value': 234, 'weight': 14},
     'Ununhexium': {'value': 449, 'weight': 459},
     'Ununoctium': {'value': 411, 'weight': 184},
     'Ununpentium': {'value': 497, 'weight': 145},
     'Ununquadium': {'value': 113, 'weight': 282},
     'Ununseptium': {'value': 7, 'weight': 327},
     'Ununtrium': {'value': 52, 'weight': 158},
     'Uranium': {'value': 77, 'weight': 118},
     'Vanadium': {'value': 308, 'weight': 381},
     'Xenon': {'value': 19, 'weight': 463},
     'Ytterbium': {'value': 222, 'weight': 417},
     'Yttrium': {'value': 109, 'weight': 175},
     'Zinc': {'value': 140, 'weight': 104},
     'Zirconium': {'value': 288, 'weight': 453}}


class Chromosome(object):
    def __init__(self, members, weight=0, value=0, max_weight=1000, mutation_rate=0.6, score=0):
        self.members = members
        self.weight = weight
        self.value = value
        self.max_weight = max_weight
        self.mutation_rate = mutation_rate
        self.score = score
        for element in self.members:
            if self.members[element].get('active') is None:
                self.members[element]['active'] = int(round(random.random()))
        self.mutate()
        self.calc_score()

    def mutate(self):
        if self.mutation_rate < random.random():
            return False
        element = self.members.keys()[random.randint(0, len(self.members.keys()) - 1)]
        self.members[element]['active'] = 0 if self.members[element]['active'] else 1

    def calc_score(self):
        if self.score:
            return self.score
        self.value = 0
        self.weight = 0
        self.score = 0
        for element in self.members:
            if self.members[element]['active']:
                self.value += self.members[element]['value']
                self.weight += self.members[element]['weight']
        self.score = self.value
        if self.weight > self.max_weight:
            self.score -= (self.weight - self.max_weight) * 10
        return self.score

    def mate_with(self, other):
        child1 = {}
        child2 = {}
        i = 0
        for element in self.members:
            if i % 2 == 0:
                child1[element] = copy(self.members[element])
                child2[element] = copy(other.members[element])
            else:
                child2[element] = copy(self.members[element])
                child1[element] = copy(other.members[element])
            i += 1
        child1 = Chromosome(child1)
        child2 = Chromosome(child2)
        return [child1, child2]


class Population(object):
    def __init__(self, size=20, elems=elements):
        self.size = size
        self.elements = elems
        self.elitism = 0.2
        self.chromosomes = []
        self.fill()

    def fill(self):
        while len(self.chromosomes) < self.size:
            if len(self.chromosomes) < self.size / 3:
                self.chromosomes.append(Chromosome(self.elements))
            else:
                self.mate()

    def sort(self):
        self.chromosomes.sort(key=lambda x: x.calc_score(), reverse=True)

    def kill(self):
        target = math.floor(self.elitism * len(self.chromosomes))
        while len(self.chromosomes) > target:
            self.chromosomes.pop()

    def mate(self):
        key1 = self.chromosomes[random.randint(0, len(self.chromosomes) - 1)]
        key2 = key1
        while key2 == key1:
            key2 = self.chromosomes[random.randint(0, len(self.chromosomes) - 1)]
        children = key1.mate_with(key2)
        self.chromosomes += children

    def generation(self, reset=False):
        self.sort()
        if reset:
            self = Population(self.size, self.elements)
        else:
            self.kill()
        self.mate()
        self.fill()
        self.sort()


    def display(self, generation_num, no_improvement):
        print "Generation:\t%s" % generation_num
        print "Best Value:\t%s" % self.chromosomes[0].score
        print "Weight:\t\t%s" % self.chromosomes[0].weight
        print "No change in:\t%s\n" % no_improvement


def main(threshold=500):
    p = Population()
    no_improvement = 0
    generation_num = 0
    while True:
        if no_improvement < threshold:
            last_score = p.chromosomes[0].calc_score()
            p.generation()
            if last_score >= p.chromosomes[0].calc_score():
                no_improvement += 1
            else:
                no_improvement = 0
            generation_num += 1
            if generation_num % 10 == 0:
                p.display(generation_num, no_improvement)
        else:
            if p.chromosomes[0].weight > p.chromosomes[0].max_weight:
                p.generation(reset=True)
                no_improvement = 0
            else:
                p.display(generation_num, no_improvement)
                break


if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-t", "--threshold", type="int", dest="threshold",
                      default=500, help="Number of generations with no change")
    (options, args) = parser.parse_args()
    sys.exit(main(options.threshold))
