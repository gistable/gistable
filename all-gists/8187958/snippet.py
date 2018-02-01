"""
traits_ndarray
--------------

I was taking the IPython.utils.traitlets for a spin;
the only really useful thing missing was an NDArray
which validates on certain shape and type constraints
and notifies for interesting kinds of inequalities
id(x)==id(y), (x==y).all(), allclose(x, y). 

Example

>>> class HasArrays(HasTraits):
...     
...     # insist only on value being an instance of `numpy.ndarray`
...     a = NDArray()
...     
...     # insist on data type
...     b = NDArray(dtype='i')
...     
...     # insist on shape, e.g. three columns, N rows
...     c = NDArray(shape=(-1, 3))

"""

import unittest

from IPython.utils.traitlets import Instance, TraitError, HasTraits

from numpy import ndarray, can_cast, allclose, dtype, array, zeros

__all__ = ['NDArray']

class NDArray(Instance):

    def __init__(self, **metadata):

        # How to do with just an enum?
        self.eq = metadata.pop('eq', 'id')
        valideq = 'id all allclose'.split(' ')
        if self.eq not in valideq:
            msg = 'eq=%r invalid, expect one of %r' % (self.eq, valideq)
            raise ValueError(msg)

        super(NDArray, self).__init__(
            klass=ndarray,
            args=(map(abs, metadata.get('shape', ())), ),
            allow_none=metadata.pop('allow_none', False),
            **metadata
        )

    def info(self):

        info = super(NDArray, self).info()

        dt = self.get_metadata('dtype')
        if dt:
            info += ', of %r' % (dtype(dt), )

        shape = self.get_metadata('shape')
        if shape:
            if self.get_metadata('bcast'):
                info += ', broadcasting to %r'
            else:
                info += ', with shape %r'
            info %= (shape, )

        return info

    def validate(self, obj, value):

        # this just checks instance
        val = super(NDArray, self).validate(obj, value)

        # maybe check dtype castable
        # TODO exact dtype match
        dt = self.get_metadata('dtype')
        if dt:
            if not can_cast(dtype(dt), value.dtype):
                msg = 'Expected type castable with %r, received %r'
                msg %= (dtype(dt), value.dtype)
                raise TraitError(msg)

        # maybe check shape
        shape = self.get_metadata('shape')
        if shape:
            # TODO implement implicit transpose, shape of (-1, 3), value.shape(3, -1), transpose it. 
            # TODO implement exact shape mode, len(shape) == len(value.shape)
            if len(shape) > len(value.shape):
                msg = 'Expected at least %d dimensions, received %d'
                msg %= (len(shape), len(value.shape))
                raise t.TraitError(msg)

            # broadcast mode, ignore 1s and start from right
            if self.get_metadata('bcast'):
                for i, (e, v) in enumerate(zip(reversed(shape), reversed(value.shape))):
                    if not (e==-1 or (e==1 or v==1) or e==v):
                        msg = 'Expected axis %d to have dim %d, received %d'
                        msg %= (len(value.shape) - i, e, v)
                        raise TraitError(msg)

            # normal, ignore -1 and start from left
            else:
                for i, (e, v) in enumerate(zip(shape, value.shape)):
                    if not (e==-1 or e==v):
                        msg = 'Expected axis %d to have dim %d, received %d'
                        msg %= (i, e, v)
                        raise TraitError(msg)

        return val

    def __set__(self, obj, value):

        new = self._validate(obj, value)
        old = self.__get__(obj)

        # handle array equality as requested
        if self.eq == 'id':
            same = id(new) == id(old)

        else:
            # place in common try-catch because both
            # can fail due to non-broadcastable shapes
            try:
                same = (old==new).all() if self.eq=='all' else allclose(old, new)
            except ValueError:
                same = False

        if not same:
            obj._trait_values[self.name] = new
            obj._notify_trait(self.name, old, new)


# Tests

class TestEq(unittest.TestCase):
    def test_id(self):
        self.assertEqual(NDArray(eq='id').eq, 'id')
    def test_all(self):
        self.assertEqual(NDArray(eq='all').eq, 'all')
    def test_allclose(self):
        self.assertEqual(NDArray(eq='allclose').eq, 'allclose')
    def test_badeq(self):
        with self.assertRaises(ValueError):
            NDArray(eq='foo')

class TestAllowNone(unittest.TestCase):
    def test_non_default(self):
        self.assertEqual(NDArray(allow_none=True)._allow_none, True)
    def test_default(self):
        self.assertEqual(NDArray()._allow_none, False)

class TestInfo(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(NDArray().info(), 'a ndarray')
    def test_allow_none(self):
        self.assertEqual(NDArray(allow_none=True).info(), 'a ndarray or None')
    def test_shape(self):
        self.assertEqual(NDArray(shape=(-1, 2)).info(), 'a ndarray, with shape (-1, 2)')
    def test_bcast(self):
        self.assertEqual(NDArray(shape=(-1, 2), bcast=True).info(), 'a ndarray, broadcasting to (-1, 2)')
    def test_dtype(self):
        self.assertEqual(NDArray(dtype='f32').info(), "a ndarray, of dtype('float32')")

class TestValidation(unittest.TestCase):

    class TestBed(HasTraits):
        x = NDArray()
        y = NDArray(dtype='i')
        z = NDArray(dtype='f')
        A = NDArray(shape=(3, 4))
        B = NDArray(shape=(-1, 3))
        C = NDArray(shape=(1, 3, -1), bcast=True)

    def test_instance_check(self):
        tb = self.TestBed()
        with self.assertRaises(TraitError):
            tb.x = 'foo'
        x = array([1.0, 2.0])
        tb.x = x
        self.assertEqual(id(tb.x), id(x))

    def test_dtype_check(self):
        tb = self.TestBed()
        f = array([1.0], 'd')
        i = array([1], 'i')
        tb.x = f
        tb.y = f
        with self.assertRaises(TraitError):
            tb.z = i

    def test_shape_normal(self):
        tb = self.TestBed()
        tb.A = zeros((3, 4))
        with self.assertRaises(TraitError):
            tb.A = zeros((4, 5))
    
    def test_shape_free(self):
        tb = self.TestBed()
        for n in [1, 5, 10]:
            tb.B = zeros((n, 3))
        for n in [1, 5, 10]:
            tb.B = zeros((n, 3, 2, 3))
        with self.assertRaises(TraitError):
            tb.B = zeros((2, 4))

    def test_shape_bcast(self):
        tb = self.TestBed()
        tb.C = zeros((2, 3, 4))
        tb.C = zeros((5, 4, 3, 1))
        tb.C = zeros((1, 3, 1, 2))
        tb.C = zeros((1, 2, 3, 4))
        with self.assertRaises(TraitError):
            tb.C = zeros((1, 3, 2, 2))


class TestEquality(unittest.TestCase):

    class TestBed(HasTraits):
        A = NDArray(eq='id')
        _A_has_changed = False
        def _A_changed(self):
            self._A_has_changed = True

        B = NDArray(eq='all')
        _B_has_changed = False
        def _B_changed(self):
            self._B_has_changed = True

        C = NDArray(eq='allclose')
        _C_has_changed = False
        def _C_changed(self):
            self._C_has_changed = True

    def test_eq_id(self):
        tb = self.TestBed()
        x = array([1, 2, 3]).astype('f')

        # set A first time, id has changed
        tb.A = x
        self.assertTrue(tb._A_has_changed)
        tb._A_has_changed = False

        # second time, no change in id
        tb.A = x
        self.assertFalse(tb._A_has_changed)
        tb._A_has_changed = False

        # third time, id changes but not values
        tb.A = x.copy()
        self.assertTrue(tb._A_has_changed)

        # 'all' first, see change
        tb.B = x
        self.assertTrue(tb._B_has_changed)
        tb._B_has_changed = False

        # but doesn't change on copy as with id testing
        tb.B = x.copy()
        self.assertFalse(tb._B_has_changed)

        # 'allclose' first, see change
        tb.C = x
        self.assertTrue(tb._C_has_changed)
        tb._C_has_changed = False

        # doesn't change on small variations
        tb.C = x.copy() + 1e-10
        self.assertFalse(tb._C_has_changed)
        tb._C_has_changed = False

        # but does change on large variations
        tb.C = x.copy() + 1e-1
        self.assertTrue(tb._C_has_changed)

