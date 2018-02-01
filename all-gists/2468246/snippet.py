def blog(request, url=""):
    remote = "http://YOURTUMBLRSITE.tumblr.com"
    local = ""http://www.example.com/blog"

    conn = httplib2.Http()
    #This is to support Tumblr's search.
    if request.GET.get("q"):
        urlencode = lambda s: urllib.urlencode({'x': s})[2:]
        url = url+"/"+urlencode(request.GET.get("q"))
    proxy_url = "%s/%s" % (remote, url)
    resp, content = conn.request(proxy_url, request.method)
    p = re.compile('(.+id="content".+)(href|src|rel|action)="\/(.+id="footer".+)', re.DOTALL)
    content = re.sub(p, r'\1\2="%s/\3' % (local), content)
    content = content.replace(remote, local)
    return HttpResponse(content)
