def get_request():
    """
    blindly walks up the stack looking for 
    request.user
    """
    for i in itertools.count():
        try:
            frame = sys._getframe(i)
        except ValueError:
            frame = None
        if not frame: return None
        if "request" in frame.f_locals:
            request = frame.f_locals['request']
            if not isinstance(request, HttpRequest) or not hasattr(request, "user"):
                # wrong signature... keep looking
                continue
            return request
