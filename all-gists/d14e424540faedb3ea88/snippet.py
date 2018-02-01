"""
Setup:
    Assuming Odoo 8.0 sources at ~/odoo:
    $ cp odoo-sh.py ~/odoo
    $ cd ~/odoo
    $ python -i odoo-sh.py

Usage example:
    >>> env = connect('my-db-name')
    >>> Users = env['res.users']
    >>> Users.search()
    >>> Users.browse(1).name
    u'Administrator'
"""

from __future__ import print_function
from openerp.modules.registry import RegistryManager
from openerp.api import Environment


def connect(dbname='trunk', uid=1, context=None):
    r = RegistryManager.get(dbname)
    cr = r.cursor()
    Environment.reset()
    env = Environment(cr, uid, context or {})
    print('Connected to %s with user %s %s'
          % (dbname, env.uid, env.user.name))
    return env

if __name__ == '__main__':
    print(__doc__)