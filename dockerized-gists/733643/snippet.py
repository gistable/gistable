import math
import random


class Statistic(object):
    """
    Hookin' it up with the seven descriptive statistics.
    """

    def __init__(self, sample):
        self.sample = sample

    def size(self):
        return len(self.sample)

    def min(self):
        return min(self.sample)

    def max(self):
        return max(self.sample)

    def mean(self):
        return sum(self.sample) / len(self.sample)

    def median(self):
        length = len(self.sample)
        if length % 2 == 0:
            return (self.sample[length/2] + self.sample[length/2 + 1]) / 2
        else:
            return self.sample[math.floor(length/2)]
            
    def variance(self):
        mean = self.mean()
        return sum(math.pow(mean - value, 2) for value in self.sample) / (len(self.sample)-1)

    def standard_deviation(self):
        return math.sqrt(self.variance())

    def histogram(self, width=80.0):
        k = int(math.ceil(math.sqrt(self.size())))
        size = (self.max() - self.min()) / k
        bins = [(self.min() + (i * size), (self.min() + (i + 1) * size)) for i in xrange(k)]
        labels = ['%8.5f - %8.5f [%%s]' % bin for bin in bins]
        labelsize = max(len(label) for label in labels)
        populations = [len([i for i in self.sample if bin[0] <= i < bin[1]]) for bin in bins]
        maxpop = max(populations)
        histosize = width - labelsize - 1
        width = width - len(str(maxpop)) - 1
        for i, label in enumerate(labels):
            label = label % str(populations[i]).rjust(len(str(maxpop)))
            print label.rjust(labelsize), '#' * int(populations[i] * width / float(maxpop))

if __name__ == '__main__':
    sample = [15, 20, 21, 36, 15, 25, 15]
    statistic = Statistic(sample)
    print 'mean is %s' % statistic.mean()
    print 'variance is %s' % statistic.variance()
    print '+1 deviation (68%%): %s' % (statistic.mean() + statistic.standard_deviation())
    print '+2 deviation (95%%): %s' % (statistic.mean() + statistic.standard_deviation() * 2)
    print '+3 deviation (99%%): %s' % (statistic.mean() + statistic.standard_deviation() * 3)
    print 'Standard deviation of 15, 20, 21, 36, 15, 25, 15 is: %s' % statistic.standard_deviation()
    statistic.histogram()
    print ''
    print ''
    statistic = Statistic([random.gauss(25, 10) for _ in xrange(1000)])
    print 'mean: %s, variance is: %s, min: %s, max: %s' % (statistic.mean(), statistic.variance(), statistic.min(), statistic.max())
    print '+1 deviation (68%%): %s' % (statistic.mean() + statistic.standard_deviation())
    print '+2 deviation (95%%): %s' % (statistic.mean() + statistic.standard_deviation() * 2)
    print '+3 deviation (99%%): %s' % (statistic.mean() + statistic.standard_deviation() * 3)
    statistic.histogram()

    statistic = Statistic([random.triangular(0, 3400, 2876) for _ in xrange(1000)])
    print 'mean: %s, variance is: %s, min: %s, max: %s' % (statistic.mean(), statistic.variance(), statistic.min(), statistic.max())
    print '+1 deviation (68%%): %s' % (statistic.mean() + statistic.standard_deviation())
    print '+2 deviation (95%%): %s' % (statistic.mean() + statistic.standard_deviation() * 2)
    print '+3 deviation (99%%): %s' % (statistic.mean() + statistic.standard_deviation() * 3)
    statistic.histogram()

    statistic = Statistic([random.expovariate(0.001) for _ in xrange(250)])
    print 'mean: %s, variance is: %s, min: %s, max: %s' % (statistic.mean(), statistic.variance(), statistic.min(), statistic.max())
    print '+1 deviation (68%%): %s' % (statistic.mean() + statistic.standard_deviation())
    print '+2 deviation (95%%): %s' % (statistic.mean() + statistic.standard_deviation() * 2)
    print '+3 deviation (99%%): %s' % (statistic.mean() + statistic.standard_deviation() * 3)
    statistic.histogram()
