def wrap(angle):
    if angle > pi:
        angle -= (2*pi)
    if angle < -pi:
        angle += (2*pi)
    if angle < 0:
        angle += 2*pi
    return angle

def magnetometer_readings_to_tilt_compensated_heading(bx, by, bz, phi, theta):
    """ Takes in raw magnetometer values, pitch and roll and turns it into a tilt-compensated heading value ranging from -pi to pi (everything in this function should be in radians). """
    variation = 4.528986*(pi/180) # magnetic variation for Corpus Christi, should match your bx/by/bz and where they were measured from (a lookup table is beyond the scope of this gist)
    Xh = bx * cos(theta) + by * sin(phi) * sin(theta) + bz * cos(phi) * sin(theta)
    Yh = by * cos(phi) - bz * sin(phi)
    return wrap((atan2(-Yh, Xh) + variation))
