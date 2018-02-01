#!/usr/bin/env python
# 1. Save this file in your ~/.gimp-2.8/plug-ins/ directory
# 2. Run gimp from terminal
# 3. Go to Filters/Python-Fu/IPython Console
# 4. Go back to terminal to enjoy interactive Gimp scripting
#
import gimpfu
import gimp
from gimpfu import pdb

_pdb_types = dict([(getattr(gimpfu,pf),pf) for pf in dir(gimpfu) if pf.startswith('PDB_')])
_str_params = lambda params: ['%s %s: %s' % (param[1], _pdb_types.get(param[0]), param[2]) for param in params]

def pdb_help(procedure):
    """
    Convenient function to display help on a Gimp pdb procedure : 
    Example : 
        pdb.query('png-save')
        pdb_help(pdb.file_png_save)
    """
    proc_attrs = [(a,getattr(procedure,a)) for a in dir(procedure) if a.startswith('proc_')]
    io_attrs = [(a,_str_params(getattr(procedure,a))) for a in dir(procedure) if a in ('params','return_vals')]
    return proc_attrs + io_attrs

def ipython_embed(image, layer):
    import IPython
    IPython.embed()

gimpfu.register("IPython-Console", "IPython Interpreter",
                "Launches IPython interpreter in terminal",
                "Nic", "Nicolas CORNETTE", "2014",
                "<Image>/Filters/Languages/Python-Fu/_IPython Console",
                "", [], [], ipython_embed)
gimpfu.main()
