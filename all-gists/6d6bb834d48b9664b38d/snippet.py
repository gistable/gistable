def numerical():
    from scipy.integrate import odeint
    from numpy import array

    # [position, mass, velocity, mass flow]

    def acceleration(y, t, v_exhaust=1.0):
        return array([y[2], y[3], v_exhaust * y[3]/y[1], 0.0])

    initial_state = array([0.0, 2.0, 0.0, -1.0])
    solution = odeint(acceleration, initial_state, [i/10.0 for i in range(11)], args=(1.0,))

    print solution

def symbolic():
    from sympy import symbols, integrate

    m, n, t, v_exhaust = symbols('m n t v_exhaust')
    acceleration = -v_exhaust * n / (m - n*t)

    velocity = integrate(acceleration, (t, 0, t))
    position = integrate(velocity, (t, 0, t))

    params = {m: 2.0, n: 1.0, v_exhaust: 1.0}
    v = velocity.subs(params)
    p = position.subs(params)

    solution = [(p.subs({t: i/10.0}).evalf(), v.subs({t: i/10.0}).evalf()) for i in range(11)]
    print '\n'.join(map(str, solution))

def analytical():
    from math import log

    v_exhaust = 1.0
    m = 2.0
    n = 1.0

    def velocity(t):
        return v_exhaust * log((m - n*t) / m)

    def position(t):
        return -(v_exhaust / n) * ((m-n*t) * log((m-n*t) / m) + n*t)

    solution = ((position(i/10.0), velocity(i/10.0)) for i in range(11))
    print '\n'.join(map(str, solution))

numerical()
symbolic()
analytical()
