#!/usr/bin/env python2
from argparse import ArgumentParser


parser = ArgumentParser(
    description='Profile loading a model\'s data for a specific view in order '
    'to find bottlenecks')
parser.add_argument('odoo_basedir')
parser.add_argument('odoo_cfg')
parser.add_argument('odoo_db')
parser.add_argument('model')
parser.add_argument('--view_id', default=None)
parser.add_argument('--view_type', default='form')
parser.add_argument('--domain', default="[('id', '=', 1)]")
args = parser.parse_args()

import sys
sys.path.insert(0, args.odoo_basedir)

from openerp import SUPERUSER_ID, api, tools
from openerp.sql_db import db_connect
tools.config.parse_config(['-c', args.odoo_cfg])
cr = db_connect(args.odoo_db).cursor()
uid = SUPERUSER_ID
domain = eval(args.domain)
with api.Environment.manage():
    env = api.Environment(cr, uid, {})
    fields_view_get = env[args.model].fields_view_get(
        view_id=args.view_id, view_type=args.view_type)
    fields_to_fetch = fields_view_get['fields'].keys()
    # this is intentionally inefficient to mimic what the web client does
    records = env[args.model].search(domain)
    import cProfile, pstats, StringIO
    pr = cProfile.Profile()
    pr.enable()
    for record_id in records.ids:
        record = env[args.model].browse([record_id]).read(fields_to_fetch)
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()
cr.close()
