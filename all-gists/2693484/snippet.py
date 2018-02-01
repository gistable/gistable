def proxy_fix(application):
    def new_application(environ, start_response):
        environ['wsgi.url_scheme'] = 'https'
        return application(environ, start_response)
    return new_application


app.wsgi_app = proxy_fix(app.wsgi_app)