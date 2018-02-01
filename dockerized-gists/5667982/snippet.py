from __future__ import division
import numpy

def haar_transform(x):
    xc = x.copy()
    n = len(xc)

    avg = [0 for i in range(n)]
    dif = [0 for i in range(n)]

    while n > 1:

        for i in range(int(n/2)):
            avg[i] = (xc[2*i]+xc[2*i+1])/2
            dif[i] = xc[2*i]-avg[i]

        for i in range(int(n/2)):
            xc[i] = avg[i]
            xc[i+int(n/2)] = dif[i]

        n = int(n/2)

    return xc

def inverse_haar(x):
    
    n = len(x)
    tmp = [0 for i in range(n)]

    count = 2
    while count <= n:

        for i in range(int(count/2)):
            tmp[2*i] = x[i] + x[i + int(count/2)]
            tmp[2*i + 1] = x[i] - x[i + int(count/2)]

        for i in range(count):
            x[i] = tmp[i]

        count *= 2

    return numpy.array(tmp).astype(float)

if __name__ == '__main__':

    import pylab

    randomwalk = numpy.cumsum(numpy.random.random(1024)-0.5)
    
    haar = haar_transform(randomwalk)
    filtered = []
    for xi in haar:
        if abs(xi) < 0.5: filtered.append(0)
        else: filtered.append(xi)
    unhaar = inverse_haar(filtered)

    pylab.plot(randomwalk, '.')
    pylab.plot(unhaar, 'r-')
    pylab.show()