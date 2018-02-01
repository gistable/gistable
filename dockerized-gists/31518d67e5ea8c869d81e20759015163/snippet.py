routers = dict(

    # base router
    BASE=dict(default_application='url_shortner'),
    url_shortner=dict(
        default_controller='default',
        default_function='index',
        # function list of default controller, to distinguish between
        # args and function name
        functions=['index', 'user', 'download', 'call',
                   'analytics', 'url_grid.load', '_get_analytics_link'
                   '_get_anon_uid'],
    ),
)
