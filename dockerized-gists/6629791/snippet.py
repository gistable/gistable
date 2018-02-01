#!/opt/cleanpython26/bin/python
"""usage: %prog options

Automate tagging and buildoing rpms from hg python projects.

You need to run this on a centos machine.

This probably wants to be a recipe to automatically pull in
buildout-siyrce release.  Or maybe this shouldn't involve source
releases.

Your project needs to build buildout-source-release.

"""

import optparse
import os
import shutil
import sys
import tempfile

parser = optparse.OptionParser(__doc__)
parser.add_option('--rpm-tree', '-r', default="~/rpm",
                  help='Location of rpm tree. Defaults to ~/rpm.')
parser.add_option('--name', '-n', default=os.path.basename(os.getcwd()),
                  help='Name of project. Defaults to current directory name.')
parser.add_option('--push', '-p', default=False, action="store_true",
                  help='Push tag to origin.')

def system(command):
    print command
    fi = os.popen4(command)[1]
    output = fi.read()
    if fi.close():
        print "ERROR:", output
        raise SystemError()

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    options, args = parser.parse_args(args)

    tag = args.pop(0)
    message = ' '.join(args)
    home = os.environ['HOME']

    try:
        system("""sed -i 's/Version: 0/Version: %s/' rpm.spec""" % tag)
        system("""sed -i "s/version = '0'/version = '%s'/" setup.py""" % tag)
        system("""git commit -am 'tag versions'""")
        system("""git tag -a %s -m %r""" % (tag, message))
        system("""sed -i 's/Version: %s/Version: 0/' rpm.spec""" % tag)
        system("""sed -i "s/version = '%s'/version = '0'/" setup.py""" % tag)
        system("""git commit -am 'reset versions'""")
        work = tempfile.mkdtemp('gitrpm')
        name = options.name + '-' + tag
        system("""git archive %s | (cd %s; tar xf -)""" % (tag, work))
        system("bin/buildout-source-release file://%s rpm.cfg"
               " -n%s"
               " buildout:index=%s/.buildout/download-cache/dist"
               % (work, name, home))
        shutil.copy(
            "%s.tgz" % name,
            os.path.join(os.path.expanduser(options.rpm_tree), "SOURCES"))
        os.remove("%s.tgz" % name)
        system("rpmbuild -ba %s/rpm.spec" % work)
        if options.push:
            system("""git push origin %s""" % tag)
        shutil.rmtree(work)
    finally:
        pass
        # system('hg revert .')
        # system('hg checkout default')



if __name__ == '__main__':
    main()

