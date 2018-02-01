from fabric.api import *

## hosts

@task
@hosts('a')
def first():
    execute(second)

@task
@hosts('b')
def second():
    pass

# $ fab first
# [a] Executing task 'first'
# [b] Executing task 'second'

# $ fab first -H c
# [a] Executing task 'first'
# [b] Executing task 'second'

# $ fab first:hosts=c
# [c] Executing task 'first'
# [b] Executing task 'second'



## roles

env.roledefs = {
    'd': ['host-d'],
    'e': ['host-e'],
}

@task
@roles('d')
def third():
    execute(forth)

@task
@roles('e')
def forth():
    pass

# $ fab third
# [host-d] Executing task 'third'
# [host-e] Executing task 'forth'

# $ fab third -H c
# [host-d] Executing task 'third'
# [host-e] Executing task 'forth'

# $ fab third:hosts=c
# [c] Executing task 'third'
# [host-e] Executing task 'forth'
