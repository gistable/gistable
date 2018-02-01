"""
Configuration Parser

Configurable parser that will parse config files, environment variables,
keyring, and command-line arguments.



Example test.ini file:

    [defaults]
    gini=10

    [app]
    xini = 50

Example test.arg file:

    --xfarg=30

Example test.py file:

    import os
    import sys

    import config


    def main(argv):
        '''Test.'''
        options = [
            config.Option("xpos",
                          help="positional argument",
                          nargs='?',
                          default="all",
                          env="APP_XPOS"),
            config.Option("--xarg",
                          help="optional argument",
                          default=1,
                          type=int,
                          env="APP_XARG"),
            config.Option("--xenv",
                          help="environment argument",
                          default=1,
                          type=int,
                          env="APP_XENV"),
            config.Option("--xfarg",
                          help="@file argument",
                          default=1,
                          type=int,
                          env="APP_XFARG"),
            config.Option("--xini",
                          help="ini argument",
                          default=1,
                          type=int,
                          ini_section="app",
                          env="APP_XINI"),
            config.Option("--gini",
                          help="global ini argument",
                          default=1,
                          type=int,
                          env="APP_GINI"),
            config.Option("--karg",
                          help="secret keyring arg",
                          default=-1,
                          type=int),
        ]
        ini_file_paths = [
            '/etc/default/app.ini',
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'test.ini')
        ]

        # default usage
        conf = config.Config(prog='app', options=options,
                             ini_paths=ini_file_paths)
        conf.parse()
        print conf

        # advanced usage
        cli_args = conf.parse_cli(argv=argv)
        env = conf.parse_env()
        secrets = conf.parse_keyring(namespace="app")
        ini = conf.parse_ini(ini_file_paths)
        sources = {}
        if ini:
            for key, value in ini.iteritems():
                conf[key] = value
                sources[key] = "ini-file"
        if secrets:
            for key, value in secrets.iteritems():
                conf[key] = value
                sources[key] = "keyring"
        if env:
            for key, value in env.iteritems():
                conf[key] = value
                sources[key] = "environment"
        if cli_args:
            for key, value in cli_args.iteritems():
                conf[key] = value
                sources[key] = "command-line"
        print '\n'.join(['%s:\t%s' % (k, v) for k, v in sources.items()])


    if __name__ == "__main__":
        if config.keyring:
            config.keyring.set_password("app", "karg", "13")
        main(sys.argv)

Example results:

    $APP_XENV=10 python test.py api --xarg=2 @test.arg
    <Config xpos=api, gini=1, xenv=10, xini=50, karg=13, xarg=2, xfarg=30>
    xpos:   command-line
    xenv:   environment
    xini:   ini-file
    karg:   keyring
    xarg:   command-line
    xfarg:  command-line


"""
import argparse
import ConfigParser
import copy
import os
import sys

try:
    import keyring
except ImportError:
    keyring = None


class Option(object):
    """Holds a configuration option and the names and locations for it.

    Instantiate options using the same arguments as you would for an
    add_arguments call in argparse. However, you have two additional kwargs
    available:

        env: the name of the environment variable to use for this option
        ini_section: the ini file section to look this value up from
    """

    def __init__(self, *args, **kwargs):
        self.args = args or []
        self.kwargs = kwargs or {}

    def add_argument(self, parser, **override_kwargs):
        """Add an option to a an argparse parser."""
        kwargs = {}
        if self.kwargs:
            kwargs = copy.copy(self.kwargs)
            try:
                del kwargs['env']
            except KeyError:
                pass
            try:
                del kwargs['ini_section']
            except KeyError:
                pass
        kwargs.update(override_kwargs)
        parser.add_argument(*self.args, **kwargs)

    @property
    def type(self):
        """The type of the option.

        Should be a callable to parse options.
        """
        return self.kwargs.get("type", str)

    @property
    def name(self):
        """The name of the option as determined from the args."""
        for arg in self.args:
            if arg.startswith("--"):
                return arg[2:].replace("-", "_")
            elif arg.startswith("-"):
                continue
            else:
                return arg.replace("-", "_")

    @property
    def default(self):
        """The default for the option."""
        return self.kwargs.get("default")


class Config(object):
    """Parses configuration sources."""

    def __init__(self, options=None, ini_paths=None, **parser_kwargs):
        """Initialize with list of options.

        :param ini_paths: optional paths to ini files to look up values from
        :param parser_kwargs: kwargs used to init argparse parsers.
        """
        self._parser_kwargs = parser_kwargs or {}
        self._ini_paths = ini_paths or []
        self._options = copy.copy(options) or []
        self._values = {option.name: option.default
                        for option in self._options}
        self._parser = argparse.ArgumentParser(**parser_kwargs)
        self.pass_thru_args = []

    @property
    def prog(self):
        """Program name."""
        return self._parser.prog

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        self._values[key] = value

    def __delitem__(self, key):
        del self._values[key]

    def __contains__(self, key):
        return key in self._values

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def get(self, key, *args):
        """
        Return the value for key if it exists otherwise the default.
        """
        return self._values.get(key, *args)

    def __getattr__(self, attr):
        if attr in self._values:
            return self._values[attr]
        else:
            raise AttributeError("'config' object has no attribute '%s'"
                                 % attr)

    def build_parser(self, options, **override_kwargs):
        """."""
        kwargs = copy.copy(self._parser_kwargs)
        kwargs.update(override_kwargs)
        if 'fromfile_prefix_chars' not in kwargs:
            kwargs['fromfile_prefix_chars'] = '@'
        parser = argparse.ArgumentParser(**kwargs)
        if options:
            for option in options:
                option.add_argument(parser)
        return parser

    def parse_cli(self, argv=None):
        """Parse command-line arguments into values."""
        if not argv:
            argv = sys.argv
        options = []
        for option in self._options:
            temp = Option(*option.args, **option.kwargs)
            temp.kwargs['default'] = argparse.SUPPRESS
            options.append(temp)
        parser = self.build_parser(options=options)
        parsed, extras = parser.parse_known_args(argv[1:])
        if extras:
            valid, pass_thru = self.parse_passthru_args(argv[1:])
            parsed, extras = parser.parse_known_args(valid)
            if extras:
                raise AttributeError("Unrecognized arguments: %s" %
                                     ' ,'.join(extras))
            self.pass_thru_args = pass_thru + extras
        return vars(parsed)

    def parse_env(self):
        results = {}
        for option in self._options:
            env_var = option.kwargs.get('env')
            if env_var and env_var in os.environ:
                value = os.environ[env_var]
                results[option.name] = option.type(value)
        return results

    def get_defaults(self):
        """Use argparse to determine and return dict of defaults."""
        parser = self.build_parser(options=self._options)
        parsed, _ = parser.parse_known_args([])
        return vars(parsed)

    def parse_ini(self, paths=None):
        """Parse config files and return configuration options.

        Expects array of files that are in ini format.
        :param paths: list of paths to files to parse (uses ConfigParse logic).
                      If not supplied, uses the ini_paths value supplied on
                      initialization.
        """
        results = {}
        config = ConfigParser.SafeConfigParser()
        config.read(paths or self._ini_paths)
        for option in self._options:
            ini_section = option.kwargs.get('ini_section')
            if ini_section:
                try:
                    value = config.get(ini_section, option.name)
                    results[option.name] = option.type(value)
                except ConfigParser.NoSectionError:
                    pass
        return results

    def parse_keyring(self, namespace=None):
        """."""
        results = {}
        if not keyring:
            return results
        if not namespace:
            namespace = self.prog
        for option in self._options:
            secret = keyring.get_password(namespace, option.name)
            if secret:
                results[option.name] = option.type(secret)
        return results

    def parse(self, argv=None):
        """."""
        defaults = self.get_defaults()
        args = self.parse_cli(argv=argv)
        env = self.parse_env()
        secrets = self.parse_keyring()
        ini = self.parse_ini()

        results = defaults
        results.update(ini)
        results.update(secrets)
        results.update(env)
        results.update(args)

        self._values = results
        return self

    @staticmethod
    def parse_passthru_args(argv):
        """Handles arguments to be passed thru to a subprocess using '--'.

        :returns: tuple of two lists; args and pass-thru-args
        """
        if '--' in argv:
            dashdash = argv.index("--")
            if dashdash == 0:
                return argv[1:], []
            elif dashdash > 0:
                return argv[0:dashdash], argv[dashdash + 1:]
        return argv, []

    def __repr__(self):
        return "<Config %s>" % ', '.join([
            '%s=%s' % (k, v) for k, v in self._values.iteritems()])


def comma_separated_strings(value):
    """Handles comma-separated arguments passed in command-line."""
    return map(str, value.split(","))


def comma_separated_pairs(value):
    """Handles comma-separated key/values passed in command-line."""
    pairs = value.split(",")
    results = {}
    for pair in pairs:
        key, pair_value = pair.split('=')
        results[key] = pair_value
    return results
