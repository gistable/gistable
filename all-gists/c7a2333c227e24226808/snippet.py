from pylab import *
from scipy.stats import norm, uniform

theta_grid = arange(0,2*pi,1.0/1024.0)

true_b = pi/2

b_belief = ones(shape=theta_grid.shape, dtype=float)
b_belief /= b_belief.sum()

def _radian_normalize(x):
    new_x = x.copy()
    new_x[where(new_x > 2*pi)] -= 2*pi
    new_x[where(new_x < 0)] += 2*pi
    return new_x

Nt = 25

t = arange(0,Nt)

true_directions = _radian_normalize(norm(pi/2,pi/4).rvs(Nt-1))

measured_directions = _radian_normalize(true_directions + true_b)

positions = zeros(shape=(2, Nt))
positions[:,1:] = array([ cumsum(cos(true_directions)), cumsum(sin(true_directions)) ])

position_noise = 0.25
measured_positions = positions + norm(0,position_noise).rvs( (2, Nt) )

measured_deltas = measured_positions[:,1:]-measured_positions[:,0:-1]

plot(theta_grid, b_belief, label='prior')

def update_belief(delta_pos, measured_dir, prior):
    print "delta_pos = " + str(delta_pos)
    print "measured dir = " + str(measured_dir - true_b)

    dist = norm(0, 2*position_noise)
    posterior = dist.pdf(delta_pos[0] - cos(measured_dir - theta_grid)) * dist.pdf(delta_pos[1] - sin(measured_dir - theta_grid))
    posterior *= prior
    posterior /= posterior.sum()
    return posterior

for i in range(21):
    b_belief = update_belief(measured_deltas[:,i], measured_directions[i], b_belief)
    if (i % 4 == 0):
        plot(theta_grid, b_belief, label='measurement ' + str(i))

legend()
xticks([0, pi/2, pi, 3*pi/2, 2*pi], ['0', 'pi/2', 'pi', '3pi/2', '2pi'])
#axis('equal')
#plot(positions[0], positions[1], 'bo', label='positions')
#plot(measured_positions[0], measured_positions[1], 'go', label='measured positions')
show()
