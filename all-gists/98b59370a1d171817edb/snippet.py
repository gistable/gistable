import krpc
import math
import time

# http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/

class PIDController(object):
    """ A robust PID """

    def __init__(self, input, setpoint, kp, ki, kd, outmin = 0, outmax = 0):
        self.last_time = time.time()
        self.i_term = 0
        self.last_input = input
        self.setparams(setpoint, kp, ki, kd, outmin, outmax)

    def setparams(self, setpoint, kp, ki, kd, outmin = -float('inf'), outmax = float('inf')):
        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.outmin = outmin
        self.outmax = outmax
        self.i_term = sorted((self.outmin, self.i_term, self.outmax))[1]

    def update(self, input):
        now = time.time()
        time_change = now - self.last_time

        if time_change < 0.05:
            return 0

        error = self.error(input)
        self.i_term += self.ki * error * time_change
        self.i_term = sorted((self.outmin, self.i_term, self.outmax))[1]
        d_input = (input - self.last_input) / time_change

        output = self.kp * error + self.i_term - self.kd * d_input
        output = sorted((self.outmin, output, self.outmax))[1]

        self.last_input = input
        self.last_time = now

        return output

    def error(self, input):
        return self.setpoint - input

conn = krpc.connect()
vessel = conn.space_center.active_vessel
control = vessel.control
control.roll = 0
roll = conn.add_stream(getattr, vessel.flight(), 'roll')

t = vessel.reaction_wheel_torque[2] # torque vector is pitch,heading,roll
I = vessel.moment_of_inertia[1] # roll axis is in y-axis

print 'Torque = %.2f Nm' % t
print 'MoI    = %.2f kg/m^2' % I

setpoint = 45 * (math.pi / 180.0)
O = 0.01
Tp = 3

print 'Overshoot    = %.1f' % (O*100) + '%'
print 'Time to peak = %.2f s' % Tp

# tune Kp and Kd
logO = math.log(O)
z = math.sqrt((logO*logO) / (math.pi*math.pi + logO*logO))
w = math.pi / (Tp * math.sqrt(1.0 - z*z))
kp = (I * w * w) / t
kd = (2 * z * w * I) / t

print 'z  = %.2f' % z
print 'w  = %.2f' % w
print 'Kp = %.2f' % kp
print 'Kd = %.2f' % kd

# run control loop
pid = PIDController(roll(), setpoint, kp, 0, kd, -1, 1)
while True:
    input = roll() * (math.pi / 180.0)
    output = pid.update(input)
    print 'input = %+.3f, setpoint = %.3f, error = %+.3f, output = %+.3f' % (input, setpoint, pid.error(input), output)
    control.roll = output
    time.sleep(0.1)
