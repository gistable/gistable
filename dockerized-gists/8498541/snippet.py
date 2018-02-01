#!/usr/bin/python

import argparse
import re
import logging
import os
import sys

if os.name == "nt":
    import pbs as sh
else:
    import sh

__author__ = 'aluetjen'

LOGGER = logging.getLogger()


class CleanKernel:
    def clean(self, old_packages):
        for package in old_packages:
            self.purge_package(package)

    def purge_package(self, package):
        LOGGER.info("Purging package=%s", package)
        LOGGER.debug(sh.apt_get.remove(package, y=True, purge=True))

    def find_old_kernel_packages(self, installed_packages, running_kernel):
        installed_packages = [x for x in [self.extract_version(package) for package in installed_packages]
                              if x is not None]
        running_kernel = re.match("([0-9]+)\\.([0-9]+)\\.([0-9]+)-([0-9]+)(-.*)?", running_kernel).groups(1)[0:4]
        return [package[0] for package in installed_packages if self.is_older(package, running_kernel)]

    def is_older(self, package, version):
        for version_idx in range(0, 4):
            if package[1][version_idx] < int(version[version_idx]):
                return True
            if package[1][version_idx] > int(version[version_idx]):
                return False
        return False

    def extract_version(self, package):
        match = re.match("(.*)-([0-9]+)\\.([0-9]+)\\.([0-9]+)-([0-9]+)(-.*)?", package)
        if match is None:
            LOGGER.debug("Cannot extract version from {package}. Ignoring this package.".format(**locals()))
            return None

        return package, [int(v) for v in match.groups(1)[1:5]]

    def running_kernel_version(self):
        running_kernel = sh.uname('-r').strip()
        running_kernel_version = re.match("(.*)-([^0-9]+)", running_kernel).group(1)
        return running_kernel_version

    def installed_kernel_packages(self):
        result = []
        linux_packages = sh.dpkg_query(W=True, f='${status} ${package}\\n')
        for package in linux_packages:
            if not package.startswith("install ok installed linux-"):
                continue;

            result.append(re.match("install ok installed (.*)", package).groups(1)[0].strip())

        return result


if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--whatif', default=False, action="store_true")
    args = parser.parse_args()

    target = CleanKernel()

    installed_packages = target.installed_kernel_packages()
    running_kernel_version = target.running_kernel_version()
    old_packages = target.find_old_kernel_packages(installed_packages, running_kernel_version)

    if len(old_packages) == 0:
        sys.exit(2)

    if not args.whatif:
        target.clean(old_packages)
    else:
        for package in old_packages:
            LOGGER.info("{package}".format(**locals()))