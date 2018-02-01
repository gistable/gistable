# add try-catch block to ignore exceptions raised from re.findall()

def get_versions_for_package(pkg):
    'Get a list of available versions for package'
    pkg = denormalize(pkg)
    content = urlopen('http://code.google.com/p/rudix/downloads/list?q=Filename:%s' % pkg).read()

    try:
        urls = re.findall('(rudix.googlecode.com/files/(%s-([\w.]+(?:-\d+)?(?:.i386)?)(\.dmg|\.pkg)))' % pkg, content)
        versions = sorted(list(set(urls)), cmp=lambda x, y: version_compare(x[2], y[2]))
        if len(versions) == 0:
            return []
        else:
            return versions

    except:
	    pass