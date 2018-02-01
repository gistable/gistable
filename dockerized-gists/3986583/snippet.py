def add_subdomain_to_global(endpoint, values):
    g.subdomain = values.pop('subdomain', None)

def add_subdomain_to_url_params(endpoint, values):
    if not 'subdomain' in values:
        values['subdomain'] = g.subdomain

def add_subdomain_support(app):
    app.url_value_preprocessor(add_subdomain_to_global)
    app.url_defaults(add_subdomain_to_url_params)