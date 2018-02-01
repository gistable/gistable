#!/usr/bin/env python
"""
Setup a virtualenv with the Google App Engine SDK.

References:
  http://virtualenv.readthedocs.org/en/latest/virtualenv.html#creating-your-own-bootstrap-scripts
  http://mindtrove.info/virtualenv-bootstrapping/
"""
import hashlib
import os
import subprocess
import tempfile
import virtualenv


# SDK and SHA1 SUM available at:
# https://cloud.google.com/appengine/downloads
GAE_FILE = 'google_appengine_1.9.17.zip'
GAE_SHA1SUM = 'eec50aaf922d3b21623fda1b90e199c3ffa9e16e'
GAE_URL = 'https://storage.googleapis.com/appengine-sdks/featured/' + GAE_FILE
PTH_TPL = """
import sys; sys.__plen = len(sys.path)
%(path)s
import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)
"""


def after_install(options, home_dir):
  """Setup the GAE SDK.

  Download and unzip to home_dir/google_appengine
  Create .pth files for each in `lib/python2.7/site-packages/`.
  """
  # Create a secure temp directory.
  tmp_dir = tempfile.mkdtemp(dir=home_dir)
  tmp_file = os.path.join(tmp_dir, GAE_FILE)
  print 'Downloading', GAE_FILE, 'to', tmp_dir

  # Download the SDK with curl into the temp directory.
  subprocess.call(['curl', GAE_URL, '-o', tmp_file])

  # Calculate the SHA1 sum of the file.
  with open(tmp_file, 'rb') as fp:
    sha1sum = hashlib.sha1(fp.read()).hexdigest()

  # Compare the SHA1 sum and fail on mismatch.
  try:
    assert GAE_SHA1SUM == sha1sum
  except AssertionError:
    print 'SHA1SUM mismatch'
    print GAE_SHA1SUM, '!=', sha1sum
    print '1) The GAE SDK version was changed in', __file__, ' and the SHA1SUM was not, or'
    print '2) The downloaded .zip file is compromised.'
    raise

  # Unzip the SDK.
  subprocess.call(['unzip', '-o', tmp_file, '-d', home_dir])

  # Clean up the temp file and directory.
  os.remove(tmp_file)
  os.rmdir(tmp_dir)

  # Create .pth files.
  site_pkg_dir = os.path.join(home_dir, 'lib', 'python2.7', 'site-packages')
  gae_dir = os.path.join(home_dir, 'google_appengine')
  fancy_urllib_dir = os.path.join(gae_dir, 'lib', 'fancy_urllib')

  # Write google_appengine.pth
  fp = open(os.path.join(site_pkg_dir, 'google_appengine.pth'), 'w')
  fp.write(PTH_TPL % {'path': os.path.abspath(gae_dir)})
  fp.close()

  # Write fancy_urllib.pth
  fp = open(os.path.join(site_pkg_dir, 'fancy_urllib.pth'), 'w')
  fp.write(PTH_TPL % {'path': os.path.abspath(fancy_urllib_dir)})
  fp.close()


virtualenv.after_install = after_install


if __name__ == '__main__':
  virtualenv.main()