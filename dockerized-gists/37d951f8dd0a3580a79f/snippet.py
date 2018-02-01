class Vector(object):
  def __init__(self, components):
    self.components = components
    self.dims = len(components)
  
  def __add__(self, other):
    self._check_dims(other)
    return self.__class__([comp1 + comp2 for comp1, comp2 in zip(self.components, other.components)])
  
  def __sub__(self, other):
    self._check_dims(other)
    return self + -other
  
  def __neg__(self):
    return self.__class__([-comp for comp in self.components])
  
  def magnitude(self):
    return math.sqrt(sum(comp ** 2 for comp in self.components))
  
  def __abs__(self):
    return self.magnitude()
  
  def dot(self, other):
    self._check_dims(other)
    """Computes dot product"""
    return sum(comp1 * comp2 for comp1, comp2, in zip(self.components, other.components))
  
  def scale(self, cons):
    """Scale by constant"""
    return self.__class__([cons * comp for comp in self.components])
  
  def __mul__(self, other):
    if isinstance(other, Vector):
      return self.dot(other)
    elif isinstance(other, (int, long, float)):
      return self.scale(other)
    else:
      raise TypeError("Unsupported type %s for __mul__" % other.__class__.__name__)
  
  def __rmul__(self, other):
    return self * other # multiplication is commutative
  
  def _check_dims(self, other):
    if not isinstance(other, Vector):
      raise TypeError("Unsupported type: %s" % other.__class__.__name__)
    if self.dims != other.dims:
      raise TypeError("Dimensions must agree")

class Vector2D(Vector):
  def __init__(self, i, j):
    super(Vector2D, self).__init__([i, j])
  
  @property
  def i(self):
    return self.components[0]
  
  @i.setter
  def i(self, value):
    self.components[0] = value
  
  @property
  def j(self):
    return self.components[1]
  
  @j.setter
  def j(self, value):
    self.components[1] = value

def Vector3D(Vector2D):
  def __init__(self, i, j, k):
    super(Vector3D, self).__init__([i, j, k])
  
  @property
  def k(self):
    return self.components[2]
  
  @k.setter
  def k(self, value):
    self.components[2] = value
  
  def cross(self, other):
    self._check_dims(other)
    """Computes cross product"""
    return self.__class__([self.j*other.k - self.k*other.j,
                           self.k*other.i - self.i*other.k,
                           self.i*other.j - self.j*other.i])
  
  