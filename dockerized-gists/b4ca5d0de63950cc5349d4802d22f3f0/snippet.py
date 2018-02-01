"""
This script upgrades all outdated python packages.
"""
__author__ = "serafeimgr"

from multiprocessing import Pool, cpu_count
from subprocess import PIPE, Popen


def run_command(command):
    """
    Executes a command.
    @param: command
    """
    stdout, stderror = Popen(command,
                             stdout=PIPE,
                             stderr=PIPE,
                             shell=True).communicate()
    return stdout, stderror


def upgrade_package(package):
    """
    Upgrade a package.

    @param: package
    """
    upgrade_command = "pip install --upgrade {}".format(package)
    stdout, _ = run_command(upgrade_command)
    print package, stdout


def collect_packages():
    """
    Collect outdated packages.

    @returns : packages
    """
    outdated_command = "pip list --outdated"
    stdout, _ = run_command(outdated_command)

    return [p.split(' ')[0] for p in stdout.split('\n') if p != ""]


def main():
    """Upgrade outdated python packages."""
    packages = collect_packages()
    pool = Pool(cpu_count())
    pool.map(upgrade_package, packages)
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
