UNITY_GZIP_FILES = frozenset([
    'js',
    'mem',
    'data',
    'unity3d',
])

def can_gzip_request(request):
    if (
        request.method in ('GET', 'HEAD') and
        'gzip' in request.accept_encoding
    ):
        parts = request.path_info.rsplit('.', 1)
        if len(parts) == 2:
            ext = parts[1]
            if ext in UNITY_GZIP_FILES:
                return True
    return False

def UnityGZipTween(handler, registry):
    def tween(request):
        if can_gzip_request(request):
            orig_path_info = request.path_info
            try:
                request.path_info += 'gz'
                response = handler(request)
                response.content_encoding = 'gzip'
                if 200 <= response.status_code < 300:
                    return response
            except Exception:
                pass
            finally:
                request.path_info = orig_path_info
        return handler(request)
    return tween
