class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))

def get_args():
    parser = argparse.ArgumentParser(description='Something smart here')
    parser.add_argument('my_conf', help='The configuration file for the db', action = FullPaths)
    return parser.parse_args()

