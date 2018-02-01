def _keyword_fixture(fn):
    fixture_name = fn.__name__
    fixture_module = import_module(fn.__module__)

    @pytest.fixture(autouse=True)
    def _autouse_fixture(request):
        if fixture_name in request.keywords:
            request.getfuncargvalue(fixture_name)

    _autouse_fixture.__name__ = '_{}_autouse'.format(fixture_name)
    setattr(fixture_module, _autouse_fixture.__name__, _autouse_fixture)

    return fn


def keyword_fixture(scope='function', params=None, autouse=False):
    if callable(scope) and params is None and autouse is False:
        fn = pytest.fixture(scope)
        return _keyword_fixture(fn)
    else:
        def _inner_keyword_fixture(fn):
            fn = pytest.fixture(scope, params, autouse)(fn)
            return _keyword_fixture(fn)
        return _inner_keyword_fixture


#### Used like so
@keyword_fixture
def my_shit(request):
    return run_code()


@pytest.mark.my_shit
def test_depends_on_my_shit_doesnt_need_its_value():
    assert 'winar'
    
    
def test_depends_on_my_shit_needs_its_value(my_shit):
    assert my_shit == 'winar'