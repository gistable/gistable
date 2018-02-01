# -*- encoding: utf-8 -*-
import os

from setuptools import setup, find_packages, Command
from setuptools.command.develop import develop


class PthLine(object):
    def __init__(self, package):
        self.package = package

    def __str__(self):
        return self.line

    @property
    def package_tuple(self):
        package_parts = self.package.split(".")
        return ", ".join([
            "\"{}\"".format(part)
            for part in package_parts
        ])

    @property
    def line(self):
        data = [
            'import sys, types, os',
            'p = os.path.join("{project_path}", *({package_tuple}))',
            'ie = os.path.exists(os.path.join(p,\'__init__.py\'))',
            (
                'm = sys.modules[\'{package}\'] = types.ModuleType(\'{package}\')'
                'if sys.modules.get(\'{package}\', False) is False '
                'else sys.modules[\'{package}\']'
            ),
            'mp = (m or []) and m.__dict__.setdefault(\'__path__\',[])',
            '(p not in mp) and mp.append(p)',
        ]

        return ';'.join(data).format(
            package=self.package,
            package_tuple=self.package_tuple,
            project_path=self.project_path.replace("\\", "\\\\"),
        )

    @property
    def project_path(self):
        return os.path.abspath(os.path.dirname(__file__))


class FixNamespacePackages(Command):
    @property
    def site_packages_directory(self):
        from distutils.sysconfig import get_python_lib

        return get_python_lib()

    @property
    def pth_file_name(self):
        import glob

        data = glob.glob(
            os.path.join(
                self.site_packages_directory,
                '%s*-nspkg.pth' % self.pth_file_basename
            )
        )
        if len(data):
            return data[0]
        else:
            return os.path.join(
                self.site_packages_directory,
                '%s-nspkg.pth' % self.pth_file_basename
            )

    @property
    def namespace_packages(self):
        return NAMESPACE_PACKAGES

    @property
    def pth_file_data(self):
        lines = []
        for package in self.namespace_packages:
            lines.append(str(PthLine(package)))
        return "\n".join(lines)

    @property
    def project_path(self):
        return os.path.abspath(os.path.dirname(__file__))

    def inject_pth_file(self):
        print("Writing %s" % self.pth_file_name)
        with open(self.pth_file_name, 'w') as file_handle:
            file_handle.write(
                self.pth_file_data
            )

    def run(self):
        self.inject_pth_file()

    def initialize_options(self):
        self.pth_file_basename = None

    def finalize_options(self):
        ei = self.get_finalized_command("egg_info")
        self.pth_file_basename = ei.egg_name



develop.sub_commands.append(
    ('fix_namespace_packages', lambda x: True)
)


class DevelopCommand(develop):
    def run(self):
        super().run()
        for sub_command in self.get_sub_commands():
            self.run_command(sub_command)


def requirements(filename):
    with open(filename, 'r') as requirements_file:
        return [
            line.strip() for line in requirements_file
            if not line.startswith('#')
            ]


INSTALL_REQUIRES = requirements('requirements.txt')
TEST_REQUIRES = requirements('requirements.test.txt')
NAMESPACE_PACKAGES = ['namespace_package', 'namespace_package.subpackage']

setup(
    name='pip.install.e.fix',
    version='1.0',
    packages=find_packages(exclude=['tests.*', 'tests']),
    namespace_packages=NAMESPACE_PACKAGES,
    include_package_data=True,
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    tests_require=TEST_REQUIRES,
    cmdclass={
        'fix_namespace_packages': FixNamespacePackages,
        'develop': DevelopCommand,
    }
)
