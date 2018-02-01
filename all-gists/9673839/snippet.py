# Mostly stolen from deap's symbreg GP example
import operator
import math
import random
import string
import inspect
import ctypes

import numpy
from scipy import optimize

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

# Define new functions
def safeIntDiv(left, right):
    try:
        return int(left / right)
    except (ZeroDivisionError, OverflowError):
        return 0

def safeIntMod(left, right):
    try:
        return int(left % right)
    except (ZeroDivisionError, OverflowError):
        return 0


def safeLShift(val):
    return operator.lshift(val, 1)

def safeRShift(val):
    return operator.rshift(val, 1)

# Operation cost table
OperationCost = {
    operator.add.__name__: 1,
    operator.sub.__name__: 1,
    operator.xor.__name__: 1,
    safeIntMod.__name__: 4,
    operator.mul.__name__: 2,
    safeIntDiv.__name__: 4,
    operator.neg.__name__: 1,
    safeLShift.__name__: 1,
    safeRShift.__name__: 1,
}

defaultSymbolMap = {
    'add': '({0} + {1})',
    'sub': '({0} - {1})',
    'xor': '({0} ^ {1})',
    'safeIntMod': '({0} % {1})',
    'mul': '({0} * {1})',
    'safeIntDiv': '({0} / {1})',
    'neg': '~{0}',
    'safeLShift': '({0} << 1)',
    'safeRShift': '({0} >> 1)',
}
 
def getInfix(individual, symbolMap=defaultSymbolMap, index=0):
    x = individual[index]
    
    if x.arity >= 3:
        data = []
        last_index = index
        for _ in range(x.arity):
            out, last_index = getInfix(individual, index=last_index+1)
            data.append(out)
        retVal = x.seq.format(*data)
    elif x.arity == 2:
        out_left, next_idx = getInfix(individual, index=index+1)
        out_right, last_index = getInfix(individual, index=next_idx+1)
        retVal = symbolMap.get(x.name, x.name).format(out_left, out_right)
    elif x.arity == 1:
        val, last_index = getInfix(individual, index=index+1)
        retVal = symbolMap.get(x.name, x.name).format(val)
    else:
        retVal, last_index = x.value, index
 
    if index == 0:
        return retVal
    return retVal, last_index


pset = gp.PrimitiveSet("MAIN", 5)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(safeIntMod, 2)
pset.addPrimitive(operator.xor, 2)
pset.addPrimitive(safeIntDiv, 2)
pset.addPrimitive(operator.neg, 1)
pset.addPrimitive(safeLShift, 1)
pset.addPrimitive(safeRShift, 1)
pset.renameArguments(ARG1='a')
pset.renameArguments(ARG2='b')
pset.renameArguments(ARG3='c')
pset.renameArguments(ARG4='d')
# Problem input
pset.renameArguments(ARG0='x')

creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

float2Int = lambda x: ctypes.cast(ctypes.pointer(ctypes.c_float(x)), ctypes.POINTER(ctypes.c_int32)).contents.value
int2Float = lambda x: ctypes.cast(ctypes.pointer(ctypes.c_int32(x)), ctypes.POINTER(ctypes.c_float)).contents.value

def evalParams(params, func, points):
    # Evaluate the mean squared error between the expression
    # and the real function
    intparams = list(map(float2Int, params))
    intrepr = lambda x: int2Float(func(float2Int(x), *intparams))
    #sqerrors = ((intrepr(x) - x**(-1/2))**2 for x in points)
    sqerrors = ((intrepr(x) - x**(1/2))**2 for x in points)

    errsum = math.fsum(sqerrors)
    if math.isnan(errsum):
        errsum = len(points) * 1e+40

    return errsum

def evalInvSqrt(individual, points):    
    # Compute the difficulty of individual
    difficulty = 1
    for x in individual:
        difficulty += OperationCost.get(x.name, 0)

    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    nb_args = len(inspect.getargspec(func)[0])
    
    # Optimize the "constants"
    res = optimize.fmin(evalParams,
                        [1 for _ in range(nb_args - 1)],
                        args=(func, points),
                        full_output=True,
                        disp=False)
    errsum = res[1]
    individual.optim_params = res[0]
    return errsum / len(points), difficulty

points = [x/10. for x in range(0, 50) if x != 0]

toolbox.register("evaluate", evalInvSqrt, points=points)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

def main():
    #random.seed(31415926535)

    pop = toolbox.population(n=200)
    hof = tools.HallOfFame(20)
    
    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)

    try:
        pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 20, stats=mstats,
                                       halloffame=hof, verbose=True)
    except KeyboardInterrupt:
        pass
    print()

    for idx, y in enumerate(hof):
        err, cost = evalInvSqrt(y, points)
        optim_params = {key: val for key, val in zip(string.ascii_lowercase, [hex(float2Int(x)) for x in y.optim_params])}
        print("#{idx:01d}: ({err:.6f}, {cost}) {eq} {optim_params}".format(
            eq=getInfix(y),
            **locals()
        ))
    return pop, log, hof

if __name__ == "__main__":
    main()