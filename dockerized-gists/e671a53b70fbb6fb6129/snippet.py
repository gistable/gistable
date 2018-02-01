import pytest


def pytest_generate_tests(metafunc):
    if "fixA" in metafunc.fixturenames:
        metafunc.parametrize("fixA", [])


def test_fixA(fixA):
    print fixA


@pytest.mark.parametrize(["fixB"], [])
def test_fixB(fixB):
    print fixB


@pytest.mark.parametrize(["fixB"], [])
def test_fixA_fixB(fixA, fixB):
    print fixA, fixB


@pytest.mark.parametrize(["fixB"], [(1,)])
def test_fixA_fixB_bad(fixA, fixB):
    print fixA, fixB

@pytest.mark.parametrize(["fixP"], [(1,)])
@pytest.mark.parametrize(["fixQ"], [])
def test_fixA_fixB_bad2(fixP, fixQ):
    print fixP, fixQ

