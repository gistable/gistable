from os import environ, path

from ansible import errors, utils
from keepassdb import Database

DEFAULT_DB = 'prod'


class VarsModule(object):
    """Loads variables from secret_vars/<username>.kdb in the same directory
    as the playbook."""
    def __init__(self, inventory):
        self.inventory = inventory

    def run(self, host):
        """Load variables from a keepass database."""
        password = environ.get('KEEPASS_PASSWORD')
        if password is None:
            password = utils.getpass.getpass('Enter your keepass password: ')
        basedir = self.inventory.playbook_basedir()
        if basedir is not None:
            basedir = path.abspath(basedir)
        kpdir = environ.get('KEEPASS_DIR', path.join(basedir, 'secret_vars'))
        kpdb = environ.get('KEEPASS_DB', DEFAULT_DB)
        filename = path.join(kpdir, '%s.kdb' % kpdb)
        try:
            keepassdb = Database(filename, password=password)
        except Exception as e:
            args = filename, e.message
            raise errors.AnsibleError('Unable to open %s ("%s")' % args)
        results = dict()
        for group in keepassdb.groups:
            if group.title != 'ansible':
                continue
            for entry in group.entries:
                results['%s_url' % entry.title] = entry.url
                results['%s_username' % entry.title] = entry.username
                results['%s_password' % entry.title] = entry.password
                results['%s_comment' % entry.title] = entry.notes
                # Decode the key=value pairs found in the notes.
                lines = entry.notes.split('\n')
                if len(lines) == len(list(l for l in lines if '=' in l)):
                    for line in lines:
                        key, value = map(unicode.strip, line.split('=', 1))
                        results['_'.join([entry.title, key])] = value
        return results