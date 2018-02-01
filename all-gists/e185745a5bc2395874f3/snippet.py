def none_if_except(f, e=Exception):
    try:
        return f()
    except e:
        pass


def list_anyway(f, iterable):
    values = []
    for i in iterable:
        values.append( none_if_except( lambda:f(i) ) )
    return values


def not_empty(items):
    return [i for i in items if i is not None]


def choose_one_and_do(choose, do, *iter_list):
    iter_list = map(iter, iter_list)
    value_list = list_anyway(next, iter_list)
    while not_empty(value_list):
        n = choose(*value_list)
        yield value_list[n]
        value_list[n] = none_if_except( lambda:do(iter_list[n]) )


def merge_sorted(*sort_list):
    def choose(*values):
        return values.index(min(not_empty(values)))

    print "[{}] -> {}".format(
        ', '.join(map(str, sort_list)),
        list( choose_one_and_do(choose, next, *sort_list) )
        )


merge_sorted([-1,5,7,8], [0,1,2,3,6], [], [7,7,8,78])