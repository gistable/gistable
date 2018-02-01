# args is sys.argv[1:]
def foo(config, args):
    config.domain = None
    config.fullurl = None
    hostname = None

    it = iter(args)
    while True:
        try:
            arg = next(it)
        except StopIteration:
            break

        if arg in ('-o', '--domain'):
            config.domain = next(it)
        elif arg in ('-e', '--fullurl'):
            config.fullurl = validate_exturi(next(it))
        elif arg in ('-h', '--hostname'):
            hostname = next(it)
        else:
            raise BadArgument("unexpected argument '%s'" % arg)

    if config.domain is None:
        if hostname is None:
            hostname = socket.gethostname()
        if not '.' in hostname:
            hostname += '.dev'
        config.domain = hostname

    if config.fullurl is None:
        config.fullurl = 'central.' + config.domain

    print('Choosen: ' % config.fullurl)
    doSomething(config)
