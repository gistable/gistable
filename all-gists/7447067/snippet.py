from pylab import *
from scipy.stats import *

num_adults = 227e6
basic_income = 7.25*40*50
labor_force = 154e6
disabled_adults = 21e6
current_wealth_transfers = 3369e9

def jk_rowling(num_non_workers):
    num_of_jk_rowlings = binom(num_non_workers, 1e-7).rvs()
    return num_of_jk_rowlings * 1e9

def basic_income_cost_benefit():
    direct_costs = num_adults * basic_income
    administrative_cost_per_person = norm(250,75)
    non_worker_multiplier = uniform(-0.10, 0.15).rvs()
    non_workers = (num_adults-labor_force-disabled_adults) * (1+non_worker_multiplier)
    marginal_worker_hourly_productivity = norm(10,1)

    administrative_costs = num_adults * administrative_cost_per_person.rvs()
    labor_effect_costs_benefit = -1 * ((num_adults-labor_force-disabled_adults) *
                                       non_worker_multiplier *
                                       (40*52*marginal_worker_hourly_productivity.rvs())
                                       )
    return direct_costs + administrative_costs + labor_effect_costs_benefit - jk_rowling(non_workers)

def basic_job_cost_benefit():
    administrative_cost_per_disabled_person = norm(500,150).rvs()
    administrative_cost_per_worker = norm(5000, 1500).rvs()
    non_worker_multiplier = uniform(-0.20, 0.25).rvs()
    basic_job_hourly_productivity = uniform(0.0, 7.25).rvs()

    disabled_cost = disabled_adults * (basic_income + administrative_cost_per_disabled_person)
    num_basic_workers = ((num_adults - disabled_adults - labor_force) *
                         (1+non_worker_multiplier)
                         )

    basic_worker_cost_benefit = num_basic_workers * (
        basic_income +
        administrative_cost_per_worker -
        40*50*basic_job_hourly_productivity
        )
    return disabled_cost + basic_worker_cost_benefit


N = 1024*32
bi = zeros(shape=(N,), dtype=float)
bj = zeros(shape=(N,), dtype=float)

for k in range(N):
    bi[k] = basic_income_cost_benefit()
    bj[k] = basic_job_cost_benefit()

subplot(211)
width = 4e12
height=50*N/1024

title("Basic Income")
hist(bi, bins=50)
axis([0,width,0,height])

subplot(212)
title("Basic Job")
hist(bj, bins=50)

axis([0,width,0,height])

show()
