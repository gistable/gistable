from jinja2.environment import create_cache

# blah blah blah

app.jinja_env.cache = create_cache(1000)

# blah blah blah

app.run()