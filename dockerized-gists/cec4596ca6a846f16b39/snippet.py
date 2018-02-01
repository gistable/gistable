from erppeek import Client
import sys
import base64
from subprocess import call
import time

#report = 'giscedata.facturacio.factura'
#ids = [1513047, 1513049, 1513057, 1513042]
#ids = [1513042]
report = 'account.general.ledger.cumulative'
ids = [2951]
params = {
   'report_type': 'pdf', 
   'form': {
        'sortbydate': 'sort_date',
        'periods': [[6, 0, []]],
        'date_to': '2016-06-23',
        'landscape': False,
        'initial_balance': False,
        'date_from': '2016-01-01',
        'company_id': 1,
        'state': 'none',
        'context': {
            'lang': 'ca_ES',
            'active_ids': [158],
            'tz': 'Europe/Madrid',
            'active_id': 158
        },
        'amount_currency': False,
        'display_account': 'bal_mouvement',
        'fiscalyear': 2},
        'model': 'account.account',
        'report_id': False,
        'id': ids[0]
}

O = Client('http://localhost:8069', 'database','user','pass')

#report_id = O.report(report, ids)
report_id = O.report(report, ids, params, {'lang': 'ca_ES', 'tz': 'Europe/Madrid'})
sys.stdout.write("Waiting")
res = {'state': False}
while not res['state']:
    res = O.report_get(report_id)
    sys.stdout.write(".")
    time.sleep(0.2)
    sys.stdout.flush()

sys.stdout.write("\n")

with open('report.pdf','w') as f:
    f.write(base64.b64decode(res['result']))

call(['evince', 'report.pdf'])
