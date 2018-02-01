def to_cli_args(*args, **kwargs):
    cmd = []
    for k, v in kwargs.items():
        short = len(k) == 1
        if short:
            cmd.append('-' + k)
            if v is not True:
                cmd.append(v)
        else:
            if v is True:
                cmd.append('--' + k)
            else:
                cmd.append('--{0}={1}'.format(k, v))

    cmd.extend(args)
    return cmd


class Git(object):

    def __init__(self, cmd=None):
        self.current = list(cmd) if cmd else ['git']

    def __call__(self, *args, **kwargs):
        cmd = self.current + to_cli_args(*args, **kwargs)
        return subprocess.check_output(cmd).decode('utf8')

    def __getattr__(self, name):
        name = name.replace('_', '-')
        return Git(self.current + [name])

    def __str__(self):
        return str(self.current)

    def __repr__(self):
        return '<git.Git object {0}>'.format(str(self))

