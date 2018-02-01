def download_cover(url, name=None):
    #print "========================== START"
    #print "==== COVER URL: %s" % (url,)
    purl = urlparse(url)
    path = purl.path
    if path.startswith('/'):
        path = path[1:]
    abspath = os.path.join(settings.MEDIA_ROOT,settings.RADIOPLAYLIST_COVERS_PREFIX,path)
    relpath = os.path.join(settings.RADIOPLAYLIST_COVERS_PREFIX,path)
    if not os.path.exists(os.path.dirname(abspath)):
        os.makedirs(os.path.dirname(abspath))
    
    request = urllib2.Request(url)
    opener = urllib2.build_opener(openanything.DefaultErrorHandler())
    if os.path.exists(abspath):
        #print "==== PATH: %s" % (abspath,)
        existing_mod_time = datetime.datetime.fromtimestamp( os.path.getmtime(abspath) )
        html_timestamp = format_http_date(existing_mod_time.utctimetuple())
        #html_timestamp = 'Mon, 10 Jul 2009 08:46:04 GMT'
        #print "==== EXISTING MTIME: %s  (%s)" % (existing_mod_time, html_timestamp,)
        request.add_header('If-Modified-Since', html_timestamp)
    else:
        #print "==== DOES NOT EXIST YET: %s" % (abspath)
        pass
    img_datastream = opener.open(request)
    data = img_datastream.read()
    if data: # implies that the status code was not 304
        if os.path.exists(abspath):
            os.remove(abspath)
        output = open(abspath,'wb')
        output.write(data)
        output.close()
    folder, created = filer_models.Folder.objects.get_or_create(name='Covers')
    image, created = filer_models.Image.objects.get_or_create(_file=relpath)
    image.name = name or None
    image.folder = folder
    image.save()
    #print "========================== END"
    return image.id