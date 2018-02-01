def password():
    return getpass.getpass()

@parallel
def _foo():
    sudo('foo')

@task
def foo():
    """execute foo"""
    env.password = password()
    execute(_foo)
