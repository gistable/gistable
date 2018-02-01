import numpy as NP
import math

def isclose(x, y, rtol=1.e-5, atol=1.e-8):
    return abs(x-y) <= atol + rtol * abs(y)

def euler_angles_from_rotation_matrix(R):
    '''
    From a paper by Gregory G. Slabaugh (undated),
    "Computing Euler angles from a rotation matrix
    '''
    phi = 0.0
    if isclose(R[2,0],-1.0):
        theta = math.pi/2.0
        psi = math.atan2(R[0,1],R[0,2])
    elif isclose(R[2,0],1.0):
        theta = -math.pi/2.0
        psi = math.atan2(-R[0,1],-R[0,2])
    else:
        theta = -math.asin(R[2,0])
        cos_theta = math.cos(theta)
        psi = math.atan2(R[2,1]/cos_theta, R[2,2]/cos_theta)
        phi = math.atan2(R[1,0]/cos_theta, R[0,0]/cos_theta)
    return psi, theta, phi

if __name__ == '__main__':
    import unittest
    import random
    class Test(unittest.TestCase):
        def test1(self):
            R = NP.array([[0.5,-0.1464, 0.8536],
                          [0.5, 0.8536, -0.1464],
                          [-math.sqrt(2)/2.0,0.5,0.5]])
            psi, theta, phi = euler_angles_from_rotation_matrix(R)
            self.assertTrue(isclose(theta, math.pi/4.0))
            self.assertTrue(isclose(psi, math.pi/4.0))
            self.assertTrue(isclose(phi, math.pi/4.0))
            
        def test2(self):
            R = NP.array([[0.5,-0.1464, 0.8536],
                          [0.5, 0.8536, -0.1464],
                          [-1.0,0.5,0.5]])
            psi, theta, phi = euler_angles_from_rotation_matrix(R)
            self.assertTrue(isclose(theta, math.pi/2.0))
            self.assertTrue(isclose(psi, -0.16985631158231004))
            self.assertTrue(isclose(phi, 0.0))

        def test3(self):
            R = NP.array([[0.5,-0.1464, 0.8536],
                          [0.5, 0.8536, -0.1464],
                          [1.0,0.5,0.5]])
            psi, theta, phi = euler_angles_from_rotation_matrix(R)
            self.assertTrue(isclose(theta, -math.pi/2.0))
            self.assertTrue(isclose(psi, 2.971736342007483))
            self.assertTrue(isclose(phi, 0.0))

        def test4(self):
            # A little fuzzing
            rand = random.uniform
            for i in range(10000):
                R = NP.array([[rand(-1.,1.),rand(-1.,1.),rand(-1.,1.)],
                              [rand(-1.,1.),rand(-1.,1.),rand(-1.,1.)],
                              [rand(-1.,1.),rand(-1.,1.),rand(-1.,1.)]])
                psi, theta, phi = euler_angles_from_rotation_matrix(R)

    def suite():
        suite1 = unittest.makeSuite(Test)
        return unittest.TestSuite([suite1])

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner().run(suite)
