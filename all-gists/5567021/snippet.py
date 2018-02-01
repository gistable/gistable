def user_from_session_key(session_key):
    """
    Returns the User related to the given Django session key.
    """
    from django.conf import settings
    from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
    from django.contrib.auth.models import AnonymousUser

    session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    session_wrapper = session_engine.SessionStore(session_key)
    session = session_wrapper.load()
    user_id = session.get(SESSION_KEY)
    backend_id = session.get(BACKEND_SESSION_KEY)
    
    if user_id and backend_id:
        auth_backend = load_backend(backend_id)
        user = auth_backend.get_user(user_id)
        
        if user:
            return user
        
    return AnonymousUser()
