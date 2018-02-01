"""
Test performance of these counting methods:

- count_if_else: Set to 1 if not yet seen and increment otherwise
- count_if: Set to 0 if not yet seen, then increment regardless of containment
- count_exception: Attempt to increment and set to 1 if KeyError caught
- count_setdefault: Set default value to 0, then increment
- count_fromkeys: Create dict with necessary keys set to 0, then increment each
- count_set_and_comprehension: Create dict of items and counts using a set
- count_defaultdict: Increment count, automatically setting unseen values to 0
- count_counter: Use counter to count number of occurrences of each value

Results::

    $ python3.5 time_count_functions.py 10
    List of 5000 random numbers generated in range 0 to 10
    count_if_else with time: 1.265662200999941
    count_if with time: 1.2668585689998508
    count_exception with time: 1.0739088390000688
    count_setdefault with time: 2.214042850000169
    count_fromkeys with time: 1.1851309869998659
    count_defaultdict with time: 0.9649407060001067
    count_counter with time: 0.5262270969997189

    $ python3.5 time_count_functions.py 250
    List of 5000 random numbers generated in range 0 to 250
    count_if_else with time: 1.1669907420000527
    count_if with time: 1.2063700009998684
    count_exception with time: 1.1212147190003634
    count_setdefault with time: 2.0994550949999393
    count_fromkeys with time: 1.0786272370000916
    count_defaultdict with time: 0.9669231920001948
    count_counter with time: 0.4641083870001239

    $ python3.5 time_count_functions.py 1000
    List of 5000 random numbers generated in range 0 to 1000
    count_if_else with time: 1.600467853000282
    count_if with time: 1.759542166999836
    count_exception with time: 1.9168700440000066
    count_setdefault with time: 2.639634401999956
    count_fromkeys with time: 1.673645010999735
    count_defaultdict with time: 1.639715238000008
    count_counter with time: 0.7596302269998887

    $ python3.5 time_count_functions.py 10000
    List of 5000 random numbers generated in range 0 to 10000
    count_if_else with time: 1.5599526559999504
    count_if with time: 2.221235025999704
    count_exception with time: 3.762508314000115
    count_setdefault with time: 2.9236523790004867
    count_fromkeys with time: 1.9307061319996137
    count_defaultdict with time: 3.098360151999259
    count_counter with time: 1.0297769050002898

"""
import sys
import timeit


list_size = 5000
range_size = int(sys.argv[1])

setup = """
from collections import defaultdict, Counter
import random
random.seed('MY SEED!')
range_size = """ + str(range_size) + """
list_size = """ + str(list_size) + """
initial_list = [random.randint(0, range_size) for i in range(list_size)]

def count_if_else(my_list):
    counts = {}
    for item in my_list:
        if item not in counts:
            counts[item] = 1
        else:
            counts[item] += 1
    return counts

def count_if(my_list):
    counts = {}
    for item in my_list:
        if item not in counts:
            counts[item] = 0
        counts[item] += 1
    return counts

def count_exception(my_list):
    counts = {}
    for item in my_list:
        try:
            counts[item] += 1
        except KeyError:
            counts[item] = 1
    return counts

def count_setdefault(my_list):
    counts = {}
    for item in my_list:
        counts.setdefault(item, 0)
        counts[item] += 1
    return counts

def count_fromkeys(my_list):
    counts = dict.fromkeys(my_list, 0)
    for item in my_list:
        counts[item] += 1
    return counts

def count_set_and_comprehension(my_list):
    return dict((item, my_list.count(item)) for item in set(my_list))

def count_defaultdict(my_list):
    counts = defaultdict(int)
    for item in my_list:
        counts[item] += 1
    return counts

def count_counter(my_list):
    return Counter(my_list)

"""


def time_function(func_name):
    timed_code = 'new_list = initial_list[:]; {}(new_list)'.format(func_name)
    time = min(timeit.Timer(timed_code, setup=setup).repeat(7, 1000))
    print("{} with time: {}".format(func_name, time))


print("List of {} random numbers generated in range 0 to {}"
      .format(list_size, range_size))
time_function("count_if_else")
time_function("count_if")
time_function("count_exception")
time_function("count_setdefault")
time_function("count_fromkeys")
time_function("count_defaultdict")
time_function("count_counter")