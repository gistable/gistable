def drop_into_pdb(app, exception):
    import sys
    import pdb
    import traceback
    traceback.print_exc()
    pdb.post_mortem(sys.exc_info()[2])
 
# somewhere in your code (probably if DEBUG is True)
flask.got_request_exception.connect(drop_into_pdb)