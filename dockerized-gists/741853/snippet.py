"""Genetic Algorithmn Implementation
see:
http://www.obitko.com/tutorials/genetic-algorithms/ga-basic-description.php
"""
import random

class GeneticAlgorithm(object):
    def __init__(self, genetics):
        self.genetics = genetics
        pass

    def run(self):
        population = self.genetics.initial()
        while True:
            fits_pops = [(self.genetics.fitness(ch),  ch) for ch in population]
            if self.genetics.check_stop(fits_pops): break
            population = self.next(fits_pops)
            pass
        return population

    def next(self, fits):
        parents_generator = self.genetics.parents(fits)
        size = len(fits)
        nexts = []
        while len(nexts) < size:
            parents = next(parents_generator)
            cross = random.random() < self.genetics.probability_crossover()
            children = self.genetics.crossover(parents) if cross else parents
            for ch in children:
                mutate = random.random() < self.genetics.probability_mutation()
                nexts.append(self.genetics.mutation(ch) if mutate else ch)
                pass
            pass
        return nexts[0:size]
    pass

class GeneticFunctions(object):
    def probability_crossover(self):
        r"""returns rate of occur crossover(0.0-1.0)"""
        return 1.0

    def probability_mutation(self):
        r"""returns rate of occur mutation(0.0-1.0)"""
        return 0.0

    def initial(self):
        r"""returns list of initial population
        """
        return []

    def fitness(self, chromosome):
        r"""returns domain fitness value of chromosome
        """
        return len(chromosome)

    def check_stop(self, fits_populations):
        r"""stop run if returns True
        - fits_populations: list of (fitness_value, chromosome)
        """
        return False

    def parents(self, fits_populations):
        r"""generator of selected parents
        """
        gen = iter(sorted(fits_populations))
        while True:
            f1, ch1 = next(gen)
            f2, ch2 = next(gen)
            yield (ch1, ch2)
            pass
        return

    def crossover(self, parents):
        r"""breed children
        """
        return parents

    def mutation(self, chromosome):
        r"""mutate chromosome
        """
        return chromosome
    pass

if __name__ == "__main__":
    """
    example: Mapped guess prepared Text
    """
    class GuessText(GeneticFunctions):
        def __init__(self, target_text,
                     limit=200, size=400,
                     prob_crossover=0.9, prob_mutation=0.2):
            self.target = self.text2chromo(target_text)
            self.counter = 0

            self.limit = limit
            self.size = size
            self.prob_crossover = prob_crossover
            self.prob_mutation = prob_mutation
            pass

        # GeneticFunctions interface impls
        def probability_crossover(self):
            return self.prob_crossover

        def probability_mutation(self):
            return self.prob_mutation

        def initial(self):
            return [self.random_chromo() for j in range(self.size)]

        def fitness(self, chromo):
            # larger is better, matched == 0
            return -sum(abs(c - t) for c, t in zip(chromo, self.target))

        def check_stop(self, fits_populations):
            self.counter += 1
            if self.counter % 10 == 0:
                best_match = list(sorted(fits_populations))[-1][1]
                fits = [f for f, ch in fits_populations]
                best = max(fits)
                worst = min(fits)
                ave = sum(fits) / len(fits)
                print(
                    "[G %3d] score=(%4d, %4d, %4d): %r" %
                    (self.counter, best, ave, worst,
                     self.chromo2text(best_match)))
                pass
            return self.counter >= self.limit

        def parents(self, fits_populations):
            while True:
                father = self.tournament(fits_populations)
                mother = self.tournament(fits_populations)
                yield (father, mother)
                pass
            pass

        def crossover(self, parents):
            father, mother = parents
            index1 = random.randint(1, len(self.target) - 2)
            index2 = random.randint(1, len(self.target) - 2)
            if index1 > index2: index1, index2 = index2, index1
            child1 = father[:index1] + mother[index1:index2] + father[index2:]
            child2 = mother[:index1] + father[index1:index2] + mother[index2:]
            return (child1, child2)

        def mutation(self, chromosome):
            index = random.randint(0, len(self.target) - 1)
            vary = random.randint(-5, 5)
            mutated = list(chromosome)
            mutated[index] += vary
            return mutated

        # internals
        def tournament(self, fits_populations):
            alicef, alice = self.select_random(fits_populations)
            bobf, bob = self.select_random(fits_populations)
            return alice if alicef > bobf else bob

        def select_random(self, fits_populations):
            return fits_populations[random.randint(0, len(fits_populations)-1)]

        def text2chromo(self, text):
            return [ord(ch) for ch in text]
        def chromo2text(self, chromo):
            return "".join(chr(max(1, min(ch, 255))) for ch in chromo)

        def random_chromo(self):
            return [random.randint(1, 255) for i in range(len(self.target))]
        pass

    GeneticAlgorithm(GuessText("Hello World!")).run()
    pass
