import numpy as np

def transfer_function(x, y):
    return np.power(np.prod(x, axis=1)[:, None] * np.prod(y, axis=0), 1./x.shape[1])

def gnn(c):
    return  normalize([np.random.random(c[i] * c[i + 1]).reshape((c[i], c[i + 1])) for i in range(len(c) - 1)])

def predict(weights, input_vector, reverse=False):
    current_net = [input_vector] + weights
    if reverse: current_net = [input_vector] + [layer.T for layer in weights[::-1]]
    return reduce(transfer_function, current_net)

def normalize(weights):
    constants = [np.power(np.prod(w, axis=1), -1./w.shape[1]).reshape(w.shape[0],1) for w in weights]
    return [np.multiply(w, constant) for w, constant in zip(weights, constants)]