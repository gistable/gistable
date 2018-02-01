#!/usr/bin/python3
"""
This script lists all APT package updates currently available for your system
along with the version numbers of the old & new packages.  It is derived from
``/usr/lib/update-notifier/apt-check`` in the ``update-notifier-common``
package on Ubuntu 14.04 (Trusty Tahr) and is made available under the same
license (the GNU GPL v2).

This script is know to work on Ubuntu Trusty and Xenial, and it should work on
any recent version of Ubuntu with the ``python3-apt`` package installed.  If
``python3-prettytable`` is also installed, it'll even work prettily!

Output columns:

- package name
- installed version
- update candidate version
- 'S' if the update is a security update, '-' otherwise
- 'P' if the update is a `phased update
  <https://wiki.ubuntu.com/PhasedUpdates>`_, '-' otherwise
"""

__author__       = 'John Thorvald Wodder II'
__author_email__ = 'apt-check@varonathe.org'

from   collections import namedtuple
import platform
import apt
import apt_pkg

distro = platform.linux_distribution()[2]

security_pockets = [
    ("Ubuntu",    distro + "-security"),
    ("gNewSense", distro + "-security"),
    ("Debian",    distro + "-updates"),
]

class Upgrade(namedtuple('Upgrade', 'package installed candidate security phased')):
    @property
    def flags(self):
        return ('S' if self.security else '-') + ('P' if self.phased else '-')

def isSecurityUpgrade(ver):
    """ Check if the given version is a security update (or masks one) """
    return any((f.origin, f.archive) in security_pockets
               for f,_ in ver.file_list)

def apt_check():
    apt_pkg.init()
    cache = apt_pkg.Cache(apt.progress.base.OpProgress())
    depcache = apt_pkg.DepCache(cache)
    if depcache.broken_count > 0:
        raise SystemExit("Error: BrokenCount > 0")
    try:
        from UpdateManager.Core.UpdateList import UpdateList
        ul = UpdateList(None)
    except ImportError:
        ul = None
    # This mimics an upgrade but will never remove anything
    depcache.upgrade(True)
    if depcache.del_count > 0:
        # Unmark (clean) all changes from the given depcache
        depcache.init()
    depcache.upgrade()
    with apt.Cache() as aptcache:
        for pkg in cache.packages:
            if not depcache.marked_install(pkg) and \
                    not depcache.marked_upgrade(pkg):
                continue
            inst_ver = pkg.current_ver
            cand_ver = depcache.get_candidate_ver(pkg)
            if cand_ver == inst_ver:
                continue
            security = False
            phased = False
            if isSecurityUpgrade(cand_ver):
                security = True
            elif inst_ver:
                # Check for security updates that are masked by a candidate
                # version from another repo (-proposed or -updates)
                for ver in pkg.version_list:
                    if apt_pkg.version_compare(ver.ver_str, inst_ver.ver_str) \
                            > 0 and isSecurityUpgrade(ver):
                        security = True
                        break
            if ul is not None and \
                    ul._is_ignored_phased_update(aptcache[pkg.name]):
                phased = True
            yield Upgrade(
                package=pkg.name,
                installed=inst_ver.ver_str if inst_ver else None,
                candidate=cand_ver.ver_str,
                security=security,
                phased=phased,
            )

def main():
    updates = apt_check()
    try:
        from prettytable import PrettyTable
    except ImportError:
        for upd in updates:
            print('{0.package:20} {0.installed!s:20} {0.candidate:20} {0.flags}'\
                  .format(upd))
    else:
        tbl = PrettyTable(['Package', 'Installed', 'Candidate', 'SP'])
        tbl.align = 'l'
        for upd in updates:
            tbl.add_row([upd.package, upd.installed, upd.candidate, upd.flags])
        print(tbl.get_string(sortby='Package'))

if __name__ == "__main__":
    main()
