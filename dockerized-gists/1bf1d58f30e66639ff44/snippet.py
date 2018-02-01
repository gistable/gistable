# -*- coding:utf-8 -*-
import pytest

xs = ((1, 1, 1),
      (3, 4, 12),
      pytest.mark.xfail((4, 4, 8)))


@pytest.mark.parametrize("x, y, expected", xs)
def test_mul(x, y, expected):
    assert x * y == expected

# py.test <filename>
