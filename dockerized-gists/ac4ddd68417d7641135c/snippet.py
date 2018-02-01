import matplotlib.pyplot as plt

dt = 0.01
x = 4
r = 2
k = 2

def dx(t,x):
    return r*x*(1-x/k)

time = []
xvar = []
for i in range(500):
    t = i*dt
    time.append(t)
    xvar.append(x)
    k1 = dx(t,x)
    k2 = dx(t+dt,x + k1*dt)
    x += (k1+k2)*dt / 2

x = 1
x2var = []
for i in range(500):
    t = i*dt
    x2var.append(x)
    k1 = dx(t,x)
    k2 = dx(t+dt,x + k1*dt)
    x += (k1+k2)*dt / 2

x = 0.5
x3var = []
for i in range(500):
    t = i*dt
    x3var.append(x)
    k1 = dx(t,x)
    k2 = dx(t+dt,x + k1*dt)
    x += (k1+k2)*dt / 2

plt.plot(time,xvar,"-b")
plt.plot(time,x2var,"-y")
plt.plot(time,x3var,"-r")

plt.show()
