import datetime
import random

from django.db import models
from django.db.models import Count


class RandomManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.when_last_cached = datetime.datetime.now() - datetime.timedelta(minutes=10)
        return super(RandomManager, self).__init__(*args, **kwargs)

    def random_filter(self):
        """
        Override this if you need to filter on something
        """
        return self.all()

    def random(self):
        now = datetime.datetime.now()
        if self.when_last_cached < now - datetime.timedelta(minutes=5):
            self.when_last_cached = now
            self.count = self.random_filter().aggregate(count=Count('id'))['count']
        
        # Try 3 times then fail
        i = 0
        while True:
            random_index = random.randint(0, self.count - 1)
            try:
                return self.random_filter()[random_index]
            except IndexError:
                if i > 2:
                    raise IndexError
                i += 1
