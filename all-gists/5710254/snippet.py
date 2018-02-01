from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def reverse_proxy(request):
    """
    Reverse proxy for a remote service.
    """
    path = request.get_full_path()
    #Optionally, rewrite the path to fit whatever service we're proxying to.
    
    url = "http://%s%s" % ("my_server.lol:9200", path)

    import requests
    requestor = getattr(requests, request.method.lower())
    
    proxied_response = requestor(url, data=request.body, files=request.FILES)
    
    from django.http.response import HttpResponse
    response = HttpResponse(proxied_response.content, content_type=proxied_response.headers.get('content-type'))
    for header_key, header_value in proxied_response.headers.iteritems():
        response[header_key] = header_value
    return response