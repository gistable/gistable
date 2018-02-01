    def convert_angles(self, *q):
        yaw = atan2(2.0 * (q[1] * q[2] + q[0] * q[3]),
                    q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
        pitch = -asin(2.0 * (q[1] * q[3] - q[0] * q[2]))
        roll = atan2(2.0 * (q[0] * q[1] + q[2] * q[3]),
                     q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
        pitch *= 180.0 / pi
        yaw *= 180.0 / pi
        yaw -= 4.11
        roll *= 180.0 / pi
        return yaw, pitch, roll
