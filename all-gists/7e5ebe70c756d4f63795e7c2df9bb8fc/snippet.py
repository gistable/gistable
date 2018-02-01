import pickle

class Rick:
  def __str__(self):
    return "i'm pickle rick!!!!"

pickle_rick = pickle.dumps(Rick())
regular_rick = pickle.loads(pickle_rick)
print(regular_rick)
# >>> i'm pickle rick!!!!
