# https://groups.google.com/forum/?fromgroups=#!topic/celery-users/yIwEogsopEA

from Celery import celery

# instead of loading celeryconfig.py...
celery = Celery(broker="mongodb://127.0.0.1/avalanche_results", backend="mongodb://127.0.0.1/avalanche_tesults") 

# ** converts dict to args
res = RandomNumberSource.delay(**{'min': 0, 'max': 10, 'num': 5})

# You should print out 5 random numbers instead of hanging on authentication
print res.get()
