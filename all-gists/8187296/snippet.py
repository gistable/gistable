import bottle

# monkey patch bottle to strip trailing slash if result not found
app = bottle.app()
router_match = app.router.match
def our_match(environ):
    try:
        targets, urlargs = router_match(environ)
    except HTTPError as e:
        if e.status == 404 and environ['PATH_INFO'].endswith('/'):
            environ['PATH_INFO'] = environ['PATH_INFO'][:-1]
            targets, urlargs = router_match(environ)
        else:
            raise
    return targets, urlargs

app.router.match = our_match
