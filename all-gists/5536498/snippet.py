import os
import sys
import logging


# Turn logging down premptively.
logging.getLogger("shotgun_api3").setLevel(logging.WARNING)


import shotgun_api3


_server_names = {
    'production': 'https://production.shotgunstudio.com',
    'testing': 'https://testing.shotgunstudio.com'
}


_registry = {
    
    # Production
    'https://production.shotgunstudio.com': {
    
        None: ('any_script', 'xxx'),
        'sgactions.deploy': ('sgactions.deploy', 'xxx'),
        'sgactions.dispatch': ('sgactions.dispatch', 'xxx'),
    
    # Testing
    }, 'https://testing.shotgunstudio.com': {
        
        None: ('Generic Script', 'xxx'),
        'sgfs.tests': ('sgfs.tests', 'xxx'),
        
    }
}


def get_args(name=None, server=None, auto_name_stack_depth=0):
    
    # Get the module name that this was called from using stack frame magic.
    if name is None and hasattr(sys, '_getframe'):
        
        try:
            frame = sys._getframe(1 + auto_name_stack_depth)
        
        except ValueError:
            pass
        
        else:
            name = frame.f_globals.get('__name__')
            
            # Was run via `python -m <name>`; reconstruct.
            if name == '__main__':
                package = frame.f_globals.get('__package__')
                file_name = frame.f_code.co_filename
                base_name = file_name and os.path.splitext(os.path.basename(file_name))[0]
                name = '.'.join(x for x in (package, base_name) if x) or None
    
    # Default to production.
    if server is None:
        server = 'production'
        
    # Convert server names into URLs
    server = _server_names.get(server, server)
    
    try:
        local_registry = _registry[server]
    except KeyError:
        raise KeyError('no %r registry' % server)
    
    args = None
    if name is not None:
        # Start at the most precise and keep going to the most general.
        # E.g. 'a.b.c' will try 'a.b.c', then 'a.b', then 'a'.
        chunks = name.split('.')
        for end_i in xrange(len(chunks), 0, -1):
            args = local_registry.get('.'.join(chunks[:end_i]))
            if args:
                break
    
    # Fall back onto default.
    try:
        args = args or local_registry[None]
    except KeyError:
        raise KeyError('no default in %r registry' % server)
    
    if sys.flags.verbose:
        print '# %s.connect(...): %r -> %r' % (__package__, name, args)
    
    return (server, ) + tuple(args)


def connect(*args, **kwargs):
    return shotgun_api3.Shotgun(*get_args(*args, **kwargs), connect=False)