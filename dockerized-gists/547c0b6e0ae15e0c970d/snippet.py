#   ~/.ipython/profile_default/startup/10-mystartup.py

import numpy as np

ip = get_ipython()

def import_astropy(self, arg):
    ip.ex('import astropy')
    ip.ex('print(astropy.__version__)')
    ip.ex('from astropy.io import ascii')
    ip.ex('from astropy import table')
    ip.ex('from astropy.table import Table, QTable, Column, MaskedColumn')
    ip.ex('from astropy.table.table_helpers import TimingTables, simple_table, complex_table')
    ip.ex('from astropy.time import Time, TimeDelta')
    ip.ex('from astropy.coordinates import SkyCoord, ICRS, FK4, FK5')
    ip.ex('import astropy.units as u')
    try:
        import line_profiler
        ip.define_magic('lprun', line_profiler.magic_lprun)
    except ImportError:
        pass

ip.define_magic('astro', import_astropy)
