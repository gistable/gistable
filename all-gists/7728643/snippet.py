def is_odd(num):
    return bool(num % 2)
    
def test_is_odd():
    assert_equal(is_odd(3), True)
    assert_equal(is_odd(4), False)