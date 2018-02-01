#!/usr/bin/python
import argparse
import numpy as np
import math

PI = math.pi

def ines(p):
  """ Return a tuple of the sin and cos of the input angle (radians). """
  return ( math.sin(p) ,  math.cos(p) )

def R_x(p):
  """ Generate rotation matrix around the X axis of p degrees. """
  s, c = ines(p)
  result = np.matrix([ [ 1, 0, 0 ], [ 0 , c , -1*s ], [ 0 , s , c ] ], dtype=float )
  return result

def R_y(p):
  """ Generate rotation matrix around the Y axis of p degrees. """
  s, c = ines(p)
  result = np.matrix([ [ c, 0, s ], [ 0 , 1 , 0 ], [ -1*s , 0 , c ] ], dtype=float )
  return result

def R_z(p):
  """ Generate rotation matrix around the Z axis of p degrees. """
  s, c = ines(p)
  result = np.matrix([ [ c, -1*s, 0 ], [ s , c , 0 ], [ 0 , 0 , 1 ] ], dtype=float )
  return result

def xform ( vector, roll, pitch, yaw ):
  """ Transform input vector by roll, pitch, yaw. """
  return R_z(yaw)*R_y(pitch)*R_x(roll)*vector

def included_angle ( v , w ):
  """
    The dot (aka inner) product (the '.' here) is defined as:
      a.b = |a||b|cos(theta)
    where a and b are vectors and theta is the included angle.
    Also,
    |a| is the norm (length) of vector a, and can be calculated wiht pythagoras, or:
      |a| = sqrt(a.a)
    where the '.' is again the dot product.

    All that said, the angle can be calculated:
      theta = arccos( a.b / ( |a||b| ) )
            = arccos( a.b / ( sqrt( a.a ) * sqrt ( b.b ) )
  """
  return float(np.arccos(np.dot( v.T, w ) / ( np.sqrt(np.dot(v.T, v)) * np.sqrt(np.dot(w.T ,w )) )))

def voltages2pitchroll( vx , vy , gx , gy=None ):
  """
    Convert voltages to pitch and roll (radians), given the gains on those axes.
    If only a single gain is specified, it is used for both.
  """
  assert gx is not None
  if gy is None: gy = gx
  return ( float(np.arcsin( vx / gx )) , float( np.arcsin ( vy / gy )) )

## Convenience functions.
def pp( r, l ):
  COL = "35"
  print( ( "%" + COL + "s : %s" ) % ( r , l ) )

def r2d ( p ):
  return p*180.0/PI

def test_xform( vector , roll , pitch, yaw , description ):
  pp( description , "%s.T" % xform( start, roll, pitch, yaw ).round(4).transpose())

def test_angle( v1 , v2 , description ):
  pp( description , "%0.2f deg" % ( 180.0/PI*included_angle( v1, v2 ) ) )

def test_chain ( vx , vy , g ):
  """ This is where the processing chain calculation happens. """
  pp("gx = gy = Gain (v/g)", g )
  pitch, roll = voltages2pitchroll( vx, vy, g )
  pp("(volts) v1: %f, v2: %f" % ( vx, vy ) , "pitch = %f, roll = %f (deg)" % ( r2d(pitch) , r2d(roll) ) )
  # Take a z-unit vector and transform with with pitch and roll from sensor.
  z = np.matrix([0,0,1]).transpose()
  pp("Unit z", "%s.T" % z.transpose())
  Z = xform( z, roll , pitch, 0 )
  pp("Z", "%s.T" % Z.transpose().round(6))
  pp("net angle with vertical", "%f (deg)" % r2d(included_angle(z, Z))) #<--- The output.

## Test suite.
if __name__ == "__main__":
  print("(The .T after a vector means transpose)")
  ## Sanity checks for the transformation.
  print("Checking vector rotations.")
  start = np.matrix([ 1, 0 , 0]).round(4).transpose()      # Unit vector in the X direction.
  pp("Starting vector", "%s.T" % start.transpose())
  test_xform(start, 0 , 0 , PI/4 , "Yawing 45")
  test_xform(start, 0 , 0 , PI/2  , "Yawing 90")
  test_xform(start, PI/4 , 0 , 0  , "Rolling 45")
  test_xform(start, 0 , PI/4 , 0  , "Pitching 45")

  ## Sanity checks for the angle calculation.
  print("\nChecking angle calculation, comparing a vector to rotations of itself.")
  v1 = np.matrix([ 1 , 0 , 0 ]).transpose()
  pp("Starting vector" , "%s.T" % v1.transpose() )
  test_angle( v1 , v1 , "With itself")
  test_angle( v1 , xform( v1 , PI/4 , 0 , 0 ) , "Roll 45")
  test_angle( v1 , xform( v1 , 0 , PI/4  , 0 ) , "Pitch 45")
  test_angle( v1 , xform( v1 , 0 , 0    , PI/4 ) , "Yaw 45")
  test_angle( v1 , xform( v1 , 0 , PI/4 , PI/4 ) , "Pitch and yaw 45")

  ## Some test cases:
  print("\nIf the Y direction is pointed straight down (i.e. rolled 90 deg):")
  test_chain( 0, 1 , 1.0 )
  print("\nIf the x direction is pointed straight down (i.e. pitched 90 deg):")
  test_chain( 1, 0 , 1.0 )
  print("\nIf the x direction is pitched 45 forward:")
  test_chain( 1/math.sqrt(2), 0 , 1.0 )
  print("\nIf the y direction is rolled 45:")
  test_chain( 0, 1/math.sqrt(2), 1.0 )
  print("\nIf the x & y direction are at 45:")
  test_chain( 1/math.sqrt(2), 1/math.sqrt(2), 1.0 )
