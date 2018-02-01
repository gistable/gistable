import cPickle as pickle

def save(obj, filename):
    """Simple wrapper to pickle an object on disk
    
    :param: obj, any pickable object
    :param: filename, string representation of the file to save to

    """
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)

def load(filename):
    """Simple wrapper load a pickled an object from disk
    
    :param: filename, string representation of the file to load from
    :returns: the object saved in the file
    """
    with open(filename) as f:
        return pickle.load(f)