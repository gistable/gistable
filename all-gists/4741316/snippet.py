@pytest.fixture
def template(request):
    if 'param' in request.fixturenames:
        param = request.getfuncargvalue('param')
    else:
        param = 'default'

    # return something based on param



@pytest.mark.parametrize('param', ['one', 'two'])
def test_something(template, param):
     # test goes here
