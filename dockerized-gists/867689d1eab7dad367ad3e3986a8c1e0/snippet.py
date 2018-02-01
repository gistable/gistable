import numpy as np
import math

def regression(points, A_funcs, b_func):
    A = [[f(*p) for f in A_funcs] for p in points]
    b = [b_func(*p) for p in points]
    AT = np.transpose(A)
    hat = np.dot(np.dot(np.linalg.inv(np.dot(AT, A)), AT), b)
    e = b - np.dot(A, hat)
    return list(hat), 1 - np.dot(e, e)

def polynomial_regression(points, degree):
    A_funcs = list(map(lambda n: lambda x, y: x ** n, range(degree + 1)))
    b_func = lambda x, y: y
    return regression(points, A_funcs, b_func)

def linear_regression(points):
    return polynomial_regression(points, 1)

def exponential_regression(points):
    points = [[p[0], math.log(p[1])] for p in points]
    lr, R2 = linear_regression(points)
    return [math.exp(lr[0]), math.exp(lr[1])], R2

def logarithmic_regression(points):
    points = [[math.log(p[0]), p[1]] for p in points]
    return linear_regression(points)

def circle_regression(points):
    A_funcs = [lambda x, y: x * x + y * y, lambda x, y: x, lambda x, y: y]
    b_func = lambda x, y: 1
    return regression(points, A_funcs, b_func)

def conic_regression(points):
    A_funcs = [lambda x, y: x * x, lambda x, y: x * y, lambda x, y: y * y, lambda x, y: x, lambda x, y: y]
    b_func = lambda x, y: 1
    return regression(points, A_funcs, b_func)
