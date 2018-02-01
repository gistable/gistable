def tf_graph_wrapper(func):
    """Wraps a class method with a tf.Graph context manager"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self._graph.as_default():
            return func(self, *args, **kwargs)
    return wrapper


def tf_init(func):
    """Wraps an __init__ function with its own session and graph"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._graph = tf.Graph()
        self._sess = tf.Session(graph=self._graph)
        return tf_graph_wrapper(func)(self, *args, **kwargs)
    return wrapper


class TFSandbox:
    """Sandboxes subclass to live in a separate graph/session"""
    def __init_subclass__(cls):
        for name, value in cls.__dict__.items():

            # patch __init__
            if name == '__init__':
                setattr(cls, name, tf_init(value))

            # all class methods get wrapped
            elif callable(value):
                setattr(cls, name, tf_graph_wrapper(value))

            # _sess and _graph are reserved keywords
            elif name in ('_sess', '_graph'):
                raise ValueError('subclass cannot use reserved keywords _sess and _graph.')

    @tf_graph_wrapper
    def init_vars(self):
        return self.run(tf.global_variables_initializer())

    @tf_graph_wrapper
    def run(self, ops):
        return self._sess.run(ops)
        
        
class ExampleModel(TFSandbox):
    def __init__(self):
        """this automatically gets wrapped in a graph context"""
        self.x = tf.get_variable('x', shape=(3,), initializer=tf.random_normal_initializer())
        self.y = self.x ** 2
        
    def example_function(self):
        """this automatically gets wrapped in a graph context"""
        self.z = tf.get_variable('z', shape=(3,))
        return self.x * self.y + self.z
        
        
if __name__ == '__main__':
    # creates a model
    model = ExampleModel()
    z = model.example_function()
    model.init_vars()
    
    # model gets its own session and graph
    print(model._graph)
    print(model._sess)
    
    # run stuff
    print(model.run(model.x))
    print(model.run(model.y))
    print(model.run(z))