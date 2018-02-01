
from subprocess import check_output

EMPTY = tuple()

def get_pkgs():
    """Query local packages"""
    tmp = check_output(["pacman", "-Qi"])
    li = tmp.strip().split("\n\n")

    data = {}

    for info in li:
        info = info.strip().split('\n')
        for l in info:

            if l.startswith('Name'):
                name = l.split(':')[1].strip()
            if l.startswith('Optional Deps'):
                optdeps = l.split(':')[1].strip()
                if optdeps=='None': optdeps = EMPTY
                else: optdeps = tuple(optdeps.split(' '))
            if l.startswith('Description'):
                desc = l.split(':')[1].strip()
            if l.startswith('Depends On'):
                deps = l.split(':')[1].strip()
                if deps=='None': deps = EMPTY
                else: deps = tuple(deps.split(' '))
            if l.startswith('Required By'):
                reqs = l.split(':')[1].strip()
                if reqs=='None': reqs = EMPTY
                else: reqs = tuple(reqs.split(' '))

        data[name]={'optdeps':optdeps, 'desc':desc,
                    'deps': deps, 'reqs': reqs}

    return data


def get_missing_optdeps(pkgs):
    """Return missing optional dependencies
       key: pkg name
       val: list of packages that require pkg optionally """
    missing = {}
    for pkg, data in pkgs.iteritems():
        for dep in data['optdeps']:
            if dep not in pkgs:
                try:
                    missing[dep].append(pkg)
                except KeyError:
                    missing[dep]=[pkg]
    return missing


def print_missing_optdeps(pkgs):
    """Pretty print for get_missing_optdeps"""
    local_ = get_missing_optdeps(pkgs)
    sorted_ = local_.keys()
    sorted_.sort()
    for mis in sorted_:
        print mis
        print '    Optionaly required by:', ' '.join(local_[mis]), '\n'


def get_nonreq_libs(pkgs):
    """Get libs not required by any other"""
    local_ = set(pkgs.keys())
    all_opt_deps = set()
    non_req = {}
    for pk, data in pkgs.iteritems():
        all_opt_deps.update(data['optdeps'])

        if pk.startswith('lib') and 'libreoffice' not in pk:
            intr = local_.intersection(data['reqs'])
            if len(intr)==0:
                non_req[pk]=data['desc']

    for pk in non_req.keys():
        if pk in all_opt_deps:
            del non_req[pk]

    return non_req

def print_nonreq_libs(pkgs):
    """Pretty print for get_nonreq_libs"""
    non_req = get_nonreq_libs(pkgs)
    for n in sorted(non_req):
        print n, '\n    ', non_req[n], '\n'


pkgs = get_pkgs()

def main():
    from sys import argv

    if len(argv)==1:
        print 'Usage qpac <command>'
        print 'commands:'
        print '    missing-opt-deps: prints missing optional dependencies'
        print '    size: prints number of installed packages'
        print '    non-req-libs: prints non-required libraries'

        return

    command = argv[1].lower()

    if command=='missing-opt-deps':
        print_missing_optdeps(pkgs)
        return

    if command=='size':
        print len(pkgs)
        return

    if command=='non-req-libs':
        print_nonreq_libs(pkgs)
        return


if __name__=='__main__':
    main()
