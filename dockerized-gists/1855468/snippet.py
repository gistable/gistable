def exists(path, as_user=None, use_sudo=False, verbose=False):
    """
    Return True if given path exists on the current remote host.

    If ``as_user`` is set, will use `sudo` as that user instead of `run`. If
    ''as_user'' or ''use_sudo'' is True, will use 'sudo' as root.

    `exists` will, by default, hide all output (including the run line, stdout,
    stderr and any warning resulting from the file not existing) in order to
    avoid cluttering output. You may specify ``verbose=True`` to change this
    behavior.
    """
    if as_user is True or use_sudo:
        func = sudo
    elif as_user:
        func = lambda x: sudo(x, user=as_user)
    else:
        func = run

    cmd = 'test -e "$(echo %s)"' % path
    # If verbose, run normally
    if verbose:
        with settings(warn_only=True):
            return not func(cmd).failed
    # Otherwise, be quiet
    with settings(hide('everything'), warn_only=True):
        return not func(cmd).failed