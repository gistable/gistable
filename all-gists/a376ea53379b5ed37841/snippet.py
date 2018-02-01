@pytest.fixture
def url_checker():
    from pyramid.scripts.pviews import PViewsCommand
    from pyramid.request import Request
    from pyramid.paster import bootstrap

    def view_match(url):
        pviews = PViewsCommand([None, os.path.join(here, '../', 'development.ini'), url], 
                               quiet=True)
        config_uri = pviews.args[0]
        url = pviews.args[1]
        request = Request.blank(url)
        env = bootstrap(config_uri, request=request)
        view = pviews._find_view(request)
        result = True 
        if view is None:
            result = False
        env['closer']()
        return result

    return view_match
