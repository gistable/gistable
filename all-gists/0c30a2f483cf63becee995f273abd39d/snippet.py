@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.log.level = 'trace'
return firefox_options