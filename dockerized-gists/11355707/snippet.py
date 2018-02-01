def waiter(tasks):
    """ async tasks to sync
        tasks     -> yield     + tasks_wo_result
         1 2 3 4
        [0,0,0,0] -> [       ] + [0,0,0,0] 1, 3 solved
        [1,0,3,0] -> [1,3    ] + [  0,  0] 2 solved
        [  2,  0] -> [1,3,2  ] + [      0] 4 solved
        [      4] -> [1,3,2,4] + [       ]
    """
    while tasks:
        for task in tasks:
            if task.complete:
                tasks.remove(task)
                yield task


class A(object):
    def __init__(self, v):
        self.v = self.count = v

    def __str__(self):
        return str(self.v)

    def __repr__(self):
        return str(self.v)

    @property
    def complete(self):
        self.count -= 1
        return not self.count

a = waiter([
    A(1),
    A(2),
    A(1),
    A(3),
    A(7),
    A(2),
])
for x in a:
    print(x) # 1 1 2 2 3 7

