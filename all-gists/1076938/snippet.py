import os
import shutil
import subprocess
import sys
import tarfile
import urllib2

LIBXML2_PREFIX = "libxml2"
LIBXSLT_PREFIX = "libxslt"
LIBXML2_FTPURL = "ftp://xmlsoft.org/libxml2/"
LIBXSLT_FTPURL = "ftp://xmlsoft.org/libxslt/"


try:
    p = subprocess.Popen(['xml2-config', '--version'], stdout=subprocess.PIPE)
except OSError, e:
    raise
stdout, stderr = p.communicate()
assert p.returncode == 0
xml2_version = stdout.strip()

try:
    p = subprocess.Popen(['xslt-config', '--version'], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    assert p.returncode == 0
    xslt_version = stdout.strip()
except (OSError, AssertionError), e:
    xslt_version = None


def open_from_urls(urls):
    for url in urls:
        try:
            fobj = urllib2.urlopen(url)
        except urllib2.URLError, e:
            pass
        if sys.version_info < (2, 6) and 'content-length' not in fobj.info():
            # python 2.5 doesn't raise an error if doesn't exist,
            # instead it gives you an empty file.
            # we can probably be safe enough checking for the Content-length
            # header instead of checking for an empty value from read()
            pass
        else:
            return fobj
    raise ValueError("no urls existed")



wdir = os.path.dirname(os.path.abspath(__file__))
xml2_base = "libxml2-%s" % xml2_version
xslt_base = xslt_version and "libxslt-%s" % xslt_version

print >> sys.stderr, 'downloading %s sources' % xml2_base
try:
    f = open_from_urls(["%s%s.tar.gz" % (LIBXML2_FTPURL, xml2_base),
                        "%sold/%s.tar.gz" % (LIBXML2_FTPURL, xml2_base), ])
except ValueError, e:
    print >> sys.stderr, "could not download %s sources" % xml2_base
    sys.exit(1)
t = tarfile.open(f.geturl(), 'r|gz', fileobj=f)
t.extractall(path=wdir)
shutil.copy(os.path.join(wdir, xml2_base, 'doc', 'libxml2-api.xml'),
            os.path.join(wdir, xml2_base, 'python'))

if xslt_version:
    print >> sys.stderr, 'downloading %s sources' % xslt_base
    try:
        f = open_from_urls(["%s%s.tar.gz" % (LIBXSLT_FTPURL, xslt_base),
                            "%sold/%s.tar.gz" % (LIBXSLT_FTPURL, xslt_base), ])
    except ValueError, e:
        print >> sys.stderr, "could not download %s sources" % xslt_base
    else:
        t = tarfile.open(f.geturl(), 'r|gz', fileobj=f)
        t.extractall(path=wdir)
        for xsltfile, target in (('doc/libxslt-api.xml', None),
                                 ('python/generator.py', 'xsltgenerator.py'),
                                 ('python/libxslt-python-api.xml', None),
                                 ('python/libxsl.py', None),
                                 ('python/libxslt_wrap.h', None),
                                 ('python/libxslt.c', None)):
            target = target or os.path.basename(xsltfile)
            shutil.copy(os.path.join(wdir, xslt_base, xsltfile),
                        os.path.join(wdir, xml2_base, 'python', target))

pythondir = os.path.join(wdir, xml2_base, 'python')
for f in os.listdir(pythondir):
    fn = os.path.join(pythondir, f)
    shutil.move(fn, os.path.join(wdir, f))

exec(compile(open('setup.py').read().replace('\\r\\n', '\\n'),
    'setup.py', 'exec'))