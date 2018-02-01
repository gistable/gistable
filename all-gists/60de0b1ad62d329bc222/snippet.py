#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

def calc_ab(alpha_a, beta_a, alpha_b, beta_b):
    '''
    See http://www.evanmiller.org/bayesian-ab-testing.html

    αA is one plus the number of successes for A
    βA is one plus the number of failures for A
    αB is one plus the number of successes for B
    βB is one plus the number of failures for B
    '''
    total = 0.0
    for i in range(alpha_b):
        num = math.lgamma(alpha_a+i) + math.lgamma(beta_a+beta_b) + math.lgamma(1+i+beta_b) + math.lgamma(alpha_a+beta_a)
        den = math.log(beta_b+i) + math.lgamma(alpha_a+i+beta_a+beta_b) + math.lgamma(1+i) + math.lgamma(beta_b) + math.lgamma(alpha_a) + math.lgamma(beta_a)

        total += math.exp(num - den)
    return total

print(calc_ab(1600+1,1500+1,3200+1,3300+1))