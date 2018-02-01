# Standalone mini version of pip
# Geared towards Pythonista, but easily adaptable to other pure python installs

import argparse, copy, gzip, os, os.path, re, requests, shutil, site, sys, tarfile, time, xmlrpclib

# Where packages will end up installed
site_packages = site.USER_SITE
# Root of Pythonista saveable document location
pythonista_base = os.path.split(site_packages)[0]
# Temporary directory for work
tmp_dir = os.path.join(pythonista_base, '__pip_tmp')

# Override the default usage message and turn it into a help message
default_usage_msg = """\
pip <command> [options]

commands:
    install      Install packages.
    uninstall    Uninstall packages.
    search       Search PyPI for packages.
"""

install_usage_msg = """\
pip install [options] <requirement specifier> ...
"""

uninstall_usage_msg = """\
pip uninstall [options] <package> ...
"""

search_usage_msg = """\
search [options] <query>
"""

setup_pre_prefix = """
def dummyFunc(*args, **kwargs):
    return args[0]

class dummyClass(object):
    def __init__(self, fn):
        self.__dict__['fn'] = fn
    def __call__(self, *args, **kwargs):
        return self.fn(self)
    def __getitem__(self, name):
        return self.fn(self)
    def __getattr__(self, name):
        return self.fn(self)

global _dummy
_dummy = dummyClass(dummyFunc)

_open = open

def _dummy_open(*args, **kwargs):
    try:
        return _open(*args, **kwargs)
    except:
        return _dummy

open = _dummy_open
"""

setup_prefix = """
def setup(*kargs, **kwargs):
    return (kargs, kwargs)

s = """

dummy_obj = """
%s = _dummy
"""

def find_setup(root):
    queue = [root]
    while len(queue) > 0:
        node = queue.pop(0)
        dirpath, dirnames, filenames = os.walk(node).next()
        for child in sorted(filenames):
            node = os.path.join(dirpath,child)
            if (os.path.split(node)[-1].lower() == 'setup.py'):
                return node
        for child in sorted(dirnames):
            queue.append(os.path.join(dirpath,child))
    return None

def setup_parse_lite(setup_file):
    # Read in the setup.py file
    with open(setup_file) as f:
        astr = f.read()
    # Split out the part starting with setup(...
    if 'setup (' in astr:
        setup_str = 'setup ('
    else:
        setup_str = 'setup('
    astr = astr.split(setup_str)[-1]
    # Parse the remaining string to find the closing parentheses
    parens = {'(': ')'}
    closing = [')']
    stack = [')']
    sofar = ''
    for c in astr:
        sofar += c
        d = parens.get(c, None)
        if d:
            stack.append(d)
        elif c in closing:
            stack.pop()
        if not stack:
            # Our stack is empty, we found the closing, return it
            return 'setup(' + sofar
    # We ran out! Return nothing, couldn't parse it right
    return None

def define_dummy(setup_code, e_msg):
    # This can handle undefined variables and undefined objects/fuctions
    # However, if the setup code attempts to interact with one of these objects
    # there will likely be an error
    try:
        var_name = re.match("name '([^']+)' is not defined", e_msg.message).group(1)
    except:
        # For some reason, we didn't find a name, abort
        return ''
    # Found a name, now to dummy it out 
    return (dummy_obj % var_name) + setup_code

def setup_try(setup_file):
    setup_fn = setup_parse_lite(setup_file)
    result = None
    if setup_fn:
        # We were able to extract the setup function call
        setup_code = setup_prefix + setup_fn
        # At most, only try executing the code (and patching around errors) 10 times
        for x in range(10):
            try:
                gs = {'os':None}
                ls = {}
                # Attempt to run the code
                tmp_code = setup_pre_prefix + setup_code
                exec(tmp_code, gs, ls)
                # We didn't error out, extract the local variable 's' value, if defined
                del gs
                result = copy.deepcopy(ls.get('s', [None,None])[1])
                del ls
                # clean up after ourselves
                break
            except NameError as e:
                # We ran into an undefined name, re-define it and try again
                setup_code = define_dummy(setup_code, e)
            except:
                # Some other kind of error, just return no results
                result = None
                break
    if result == None:
        print setup_pre_prefix + setup_code
    return result


class PyPi:
    def __init__(self):
        self.pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
        self.limit = 10
    def versions(self, module_name, show_hidden=False):
        hits = self.pypi.package_releases(module_name, show_hidden)
        if not hits:
            return []
        if len(hits) > self.limit:
            hits = hits[:(self.limit)]
        return hits
    def search(self, search_str):
        if not search_str:
            return []
        hits = self.pypi.search({'name': search_str}, 'and')
        if not hits:
            return []
        hits = sorted(hits, key=lambda module: module['_pypi_ordering'], reverse=True)
        if len(hits) > self.limit:
            hits = hits[:(self.limit)]
        return hits
    def module_url(self, module_name, module_ver=''):
        hits = self.pypi.package_releases(module_name, True)
        if not hits:
            return None
        if not module_ver:
            module_ver = hits[0]
        elif not module_ver in hits:
            return None
        hits = self.pypi.release_urls(module_name, module_ver)
        if not hits:
            return None
        source = ([x for x in hits if x['packagetype'] == 'sdist'][:1] + [None])[0]
        return source
    def _sizeof_fmt(self, num, suffix='Bps', show_decimal=False):
        num /= 8.0
        places = ["%.", "%.1"]
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(num) < 1024.0:
                return (places[show_decimal] + "f %s%s") % (num, unit, suffix)
            num /= 1024.0
        return (places[show_decimal] + "f %s%s") % (num, 'Y', suffix)
    def _download(self, module_url, tmp_dir, output_file, width=9):
        with open(os.path.join(tmp_dir, output_file), 'wb') as f:
            try:
                start = time.clock()
                r = requests.get(module_url, stream=True)
                total_length = int(r.headers.get('content-length'))
                dl = 0
                for chunk in r.iter_content(32768):
                    dl += len(chunk)
                    f.write(chunk)
                    if total_length is None:
                        # Indeterminate file size, just output speed
                        print ("[*unknown*]|???|%s" % (self._sizeof_fmt(dl//(time.clock() - start), show_decimal=True)))
                    else:
                        # Known file size, output progress plus speed
                        done = int(width * dl / total_length)
                        print ("[%s%s]|%s|%s" % ('=' * done, ' ' * (width-done), self._sizeof_fmt(total_length, suffix='B'), self._sizeof_fmt(dl//(time.clock() - start), show_decimal=True)))
                return True
            except:
                pass
        # Some sort of error, return False
        return False
    def _ungzip(self, tmp_dir, input_file, output_file):
        # Ungzip file to output file, which can already exist or not (will get overwritten)
        in_file = os.path.join(tmp_dir, input_file)
        with open(os.path.join(tmp_dir, output_file), 'wb') as f:
            try:
                with open(in_file, 'rb') as g:
                    gz_check = g.read(3)
            except:
                gz_check = ''
            if gz_check != '\x1f\x8b\x08':
                # Not a gzip file, return an error
                return False
            try:
                with gzip.open(in_file, 'rb') as gzfile:
                    f.write(gzfile.read())
                    return True
            except:
                # Error parsing the gzip file, return false
                return False
        return False
    def _untar(self, tmp_dir, input_file, output_dir):
        # Untar file to output directory, which must exist already (and should be blank)
        in_file = os.path.join(tmp_dir, input_file)
        out_dir = os.path.join(tmp_dir, output_dir)
        try:
            with open(in_file, 'rb') as f:
                f.seek(257)
                ustar_check = f.read(5)
        except:
            ustar_check = ''
        if ustar_check != 'ustar':
            # Not a tar file, return an error
            return False
        try:
            tar = tarfile.open(in_file, 'r')
            # check for a leading directory common to all files and remove it
            dirnames = [os.path.join(os.path.dirname(x.name), '') for x in tar.getmembers() if x.name != 'pax_global_header']
            common_dir = os.path.commonprefix(dirnames or ['/'])
            if not common_dir.endswith('/'):
                common_dir = os.path.join(os.path.dirname(common_dir), '')
            for member in tar.getmembers():
                fn = member.name
                if fn == 'pax_global_header':
                    continue
                if common_dir:
                    if fn.startswith(common_dir):
                        fn = fn.split(common_dir, 1)[-1]
                    elif fn.startswith('/' + common_dir):
                        fn = fn.split('/' + common_dir, 1)[-1]
                fn = fn.lstrip('/')
                fn = os.path.join(out_dir, fn)
                dirf = os.path.dirname(fn)
                if member.isdir():
                    # A directory
                    if not os.path.exists(fn):
                        os.makedirs(fn)
                elif member.issym():
                    # skip symlinks
                    continue
                else:
                    try:
                        fp = tar.extractfile(member)
                    except (KeyError, AttributeError):
                        # invalid member, not necessarily a bad tar file
                        continue
                    if not os.path.exists(dirf):
                        os.makedirs(dirf)
                    with open(fn, 'wb') as destfp:
                        shutil.copyfileobj(fp, destfp)
                    fp.close()
            tar.close()
            return True
        except:
            return False
        return False
    def _unzip(self, tmp_dir, input_file, output_dir):
        in_file = os.path.join(tmp_dir, input_file)
        out_dir = os.path.join(tmp_dir, output_dir)
        try:
            with open(in_file, 'rb') as f:
                pk_check = f.read(2)
        except:
            pk_check = ''
        if pk_check != 'PK':
            # Not a zip file, return an error
            return False
        zipfp = open(in_file, 'rb')
        try:
            zipf = zipfile.ZipFile(zipfp)
            # check for a leading directory common to all files and remove it
            dirnames = [os.path.join(os.path.dirname(x), '') for x in zipf.namelist()]
            common_dir = os.path.commonprefix(dirnames or ['/'])
            # Check to make sure there aren't 2 or more sub directories with the same prefix
            if not common_dir.endswith('/'):
                common_dir = os.path.join(os.path.dirname(common_dir), '')
            for name in zipf.namelist():
                data = zipf.read(name)
                fn = name
                if common_dir:
                    if fn.startswith(common_dir):
                        fn = fn.split(common_dir, 1)[-1]
                    elif fn.startswith('/' + common_dir):
                        fn = fn.split('/' + common_dir, 1)[-1]
                fn = fn.lstrip('/')
                fn = os.path.join(location, fn)
                dirf = os.path.dirname(fn)
                if not os.path.exists(dirf):
                    os.makedirs(dirf)
                if fn.endswith('/'):
                    # A directory
                    if not os.path.exists(fn):
                        os.makedirs(fn)
                else:
                    fp = open(fn, 'wb')
                    try:
                        fp.write(data)
                    finally:
                        fp.close()
            zipfp.close()
            return True
        except:
            zipfp.close()
            return False
        return False

def cleanup_tmp():
    print "  cleaning up temporary files ..."
    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except:
        pass

def cmd_install(args):
    """
    - Use .module_url(package_name), no need to search, assume exact match
    - No match? "Could not find any downloads that satisfy the requirement <package_name>"
    - If we got a match (not None), then:
      - create the temp directory if it doesn't exist
      - download the content to it
      - look at the file name:
        - if it's .tgz / .tar.gz:
          - gunzip to a .tar file
          - remove the output directory if it exists
          - re-create the output directory
          - untar to the directory
    - Run breadth-first search on the output directory looking for setup.py
    - Attempt to parse the setup.py, looking for modules to install
    - Move those to the site-packages directory
    """
    # Simple install implementation, assume single exact package name
    # For now, assume a single argument: package name
    pypi = PyPi()
    if (len(args) < 1):
        print "  error: please provide a package name to install"
        return
    package_name = args[0]
    module_info = pypi.module_url(package_name)
    if not module_info:
        # Unable to find an exact match, exit out
        print "  error: could not find any downloads that satisfy the requirement: %s" % package_name
        return
    print "Found: %s" % module_info['filename']
    # Make sure that tmp_dir exists
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    # Download into the tmp_dir
    result = pypi._download(module_info['url'], tmp_dir, module_info['filename'])
    if not result:
        # We had an error, try to clean up
        cleanup_tmp()
        print "  error: error downloading package for: %s" % package_name
        return
    # Successfully downloaded, now need to expand the file
    # We'll just handle a few combinations here for now
    print "Expanding: %s" % module_info['filename']
    if module_info['filename'].lower().endswith('.tar.gz') or module_info['filename'].lower().endswith('.tgz'):
        # .tar.gz / .tgz
        # When done expanding, module_dir will contain the path to the expanded module
        # Expand the gzip archive to a .tar file
        tar_file = os.path.splitext(module_info['filename'])[0]
        if not tar_file.lower().endswith('.tar'):
            tar_file += '.tar'
        print "Extracting: %s" % tar_file
        result = pypi._ungzip(tmp_dir, module_info['filename'], tar_file)
        if not result:
            # The gzip file didn't decompress correctly
            cleanup_tmp()
            print "  error: error decompressing: %s" % module_info['filename']
            return
        # Expand the tar archive into a directory
        module_dir = os.path.splitext(tar_file)[0]
        print "Extracting: %s/" % module_dir
        real_module_dir = os.path.join(tmp_dir, module_dir)
        # Remove the output directory if it already exists
        try:
            shutil.rmtree(real_module_dir, ignore_errors=True)
        except:
            pass
        # Recreate it if it doesn't
        if not os.path.exists(real_module_dir):
            os.makedirs(real_module_dir)
        result = pypi._untar(tmp_dir, tar_file, module_dir)
        if not result:
            # The gzip file didn't decompress correctly
            cleanup_tmp()
            print "  error: error decompressing: %s" % module_info['filename']
            return
    else:
        cleanup_tmp()
        print "  error: unhandled archive type: %s" % module_info['filename']
        return
    # Now process the module contained in module_dir
    real_module_dir = os.path.join(tmp_dir, module_dir)
    # Search for the topmost setup.py file
    setup_file = find_setup(real_module_dir)
    if not setup_file:
        # Couldn't find a setup.py file
        cleanup_tmp()
        print "  error: unable to find a setup.py: %s" % module_dir
        return
    print "Parsing setup.py ..."
    setup_py = setup_try(setup_file)
    if not setup_py:
        # Couldn't find a setup.py file
        cleanup_tmp()
        print "  error: unable to simply parse setup.py: %s" % module_dir
        return
    # Parsed setup.py, might have a list of packages, let's see
    # They'll be at the same level as the setup.py file
    module_base_dir = os.path.dirname(setup_file)
    # Keep only the strings
    modules  = [x for x in setup_py.get('packages',[]) if type(x) == type('')]
    requires = [x for x in setup_py.get('install_requires',[]) if type(x) == type('')]
    if not modules:
        # Couldn't find a setup.py file
        cleanup_tmp()
        print "  error: unable to detect modules in simply parsed setup.py: %s" % module_dir
        return
    # Woo, we found module (package) names
    # Reduce them to a simple set, splitting things like foo.sub to just 'foo' and removing dupes
    # This could be fragile, as written, if the modules are stored in places like: src.dir/module.name
    # Probably needs to be revisited
    modules = sorted(set([x.split('.',1)[0] for x in modules]))
    print "\nModules(s) found for install: %s" % (', '.join(modules))
    if requires:
        print "Packages(s) required by this one: %s" % (', '.join(requires))
        print "!! Note: Dependencies not auto-installed at this time"
    # Loop through each module
    print "Installing modules ..."
    for module in modules:
        module_src  = os.path.join(module_base_dir, module)
        destination = os.path.join(site_packages, module)
        # Ensure that there is not a matching directory in site-packages
        if (os.path.exists(destination)):
            print "!! Skipped, already installed: %s" % module
            continue
        # Ensure that the source module directory exists
        if (not os.path.exists(module_src)):
            print "!! Error: unable to find module: %s" % module
        # If no match, move it over
        try:
            shutil.move(module_src, destination)
            print "++ Installed: %s" % module
        except:
            print "!! Error: Something went wrong installing module: %s" % module
    cleanup_tmp()
    print "Done."

def main():
    parser = argparse.ArgumentParser(usage=default_usage_msg)
    subparsers = parser.add_subparsers(help=argparse.SUPPRESS)
    # Add install command
    parser_install = subparsers.add_parser('install', usage=install_usage_msg, help=argparse.SUPPRESS)
    parser_install.add_argument('args', nargs='*', help=argparse.SUPPRESS)
    parser_install.set_defaults(cmd='install')
    # Add uninstall command
    parser_uninstall = subparsers.add_parser('uninstall', usage=uninstall_usage_msg, help=argparse.SUPPRESS)
    parser_uninstall.add_argument('args', nargs='*', help=argparse.SUPPRESS)
    parser_uninstall.set_defaults(cmd='uninstall')
    # Add search command
    parser_search = subparsers.add_parser('search', usage=search_usage_msg, help=argparse.SUPPRESS)
    parser_search.add_argument('args', nargs='*', help=argparse.SUPPRESS)
    parser_search.set_defaults(cmd='search')
    args = parser.parse_args()
    if (args.cmd == 'install'):
        cmd_install(args.args)
    elif (args.cmd == 'uninstall'):
        print "  <unimplemented>"
    elif (args.cmd == 'search'):
        print "  <unimplemented>"

if __name__ == '__main__':
    main()
