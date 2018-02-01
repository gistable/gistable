# import functions
from numpy import linspace
from scipy.integrate import odeint

#import pylab as pyl
import matplotlib.pyplot as plt

# define constants
init_cond = [0.3, -0.1]
t_init    = 0.0
t_final   = 10.0
time_step = 0.005
num_data =int((t_final-t_init)/time_step)

k_spring = 0.1
c_damper = 0.5

# define ordinary differential equation
def mass_spring_damper(state, t):
    x, x_dot = state
    
    f = [x_dot,
         -k_spring*x - c_damper*x_dot] 
    return f

# integrate 
t_all = linspace(t_init, t_final, num_data)
y_all = odeint(mass_spring_damper, init_cond, t_all)

# plots
fig = plt.figure()
plt.plot(t_all,y_all[:,0],'b-')
plt.plot(t_all,y_all[:,1],'r--')
plt.legend(['x [m]','dx/dt [m/s]'])
plt.xlabel('time [s]')
plt.ylabel('state')