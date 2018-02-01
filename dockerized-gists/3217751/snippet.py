class Density(object):

    def __init__(self, data, bw=None):
        """ class definitions
        """
        self.maxmin['maxima'] = []
        self.maxmin['minima'] = []
         
    def new_values_for_maxmin_validator(method):
        """This is the decorator
        """
        def wrapper(self, *args, **kwargs): 
            if self.new_values is None: 
                raise ValueError('Max/Min cannot be calculated until density values have been calculated.')
            else:
                if self.new_values:

                    # Reassign maxima / minima values
                    self.maxmin['maxima'] = []
                    self.maxmin['minima'] = []

                    # Logic to calculate self.maxmin

                return method(self, *args, **kwargs)
        return wrapper

    @property
    @new_values_for_maxmin_validator
    def maxima(self):
        return self.maxmin['maxima']

    @property
    @new_values_for_maxmin_validator
    def minima(self):
        return self.maxmin['minima']