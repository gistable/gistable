def isolation_level(level):
    """Return a Flask view decorator to set SQLAlchemy isolation level
    
    Usage::
        @main.route("/thingy/<id>", methods=["POST"])
        @isolation_level("SERIALIZABLE")
        def update_a_thing(id):
            ...
    """
    def decorator(view):
        def view_wrapper(*args, **kwargs):
            db.session.connection(execution_options={'isolation_level': level})
            return view(*args, **kwargs)
        return view_wrapper
    return decorator