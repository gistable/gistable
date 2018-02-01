@pytest.yield_fixture(autouse=True)
def newline_before_logging(request):
    if request.config.getoption('capture') == 'no':
        print()  # new-line        

    yield
