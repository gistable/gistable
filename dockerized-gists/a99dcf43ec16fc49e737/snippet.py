import subprocess

import pytest


class Interpreter(object):
    base = '/usr/bin/python'

    def __init__(self, suffix):
        self.suffix = suffix

    @property
    def exe(self):
        return self.base + self.suffix


class Virtualenv(object):
    def __init__(self, directory, executable):
        self.executable = executable
        self.directory = directory

    def create(self):
        subprocess.check_call([
            'virtualenv',
            '-p',
            self.executable,
            str(self.directory.join('venv')),
        ])

    def install(self, url):
        subprocess.check_call([
            str(self.directory.join('venv', 'bin', 'pip')),
            'install',
            url,
        ])

    def execute(self, arg):
        return subprocess.check_call([
            str(self.directory.join('venv', 'bin', 'python')),
            '-c',
            arg,
        ])


@pytest.fixture(params=[
    '2.7',
    '3.3',
    '3.4',
])
def interpreter(request):
    return Interpreter(request.param).exe


@pytest.fixture
def venv(tmpdir, interpreter):
    return Virtualenv(tmpdir, interpreter)


@pytest.fixture(params=[
    '2.5.1',
    '2.5.2',
])
def version(request):
    return request.param


@pytest.fixture(params=[
    'pypi',
    'git',
])
def install_url(request, version):
    method = request.param

    if method == 'pypi':
        return 'requests=={}'.format(version)
    elif method == 'git':
        return (
            'git+https://github.com/kennethreitz/requests'
            '@v{}#egg=requests'.format(version)
        )


def test_ssl(venv, install_url):
    venv.directory.chdir()
    venv.create()
    venv.install(install_url)
    venv.execute('import requests;'
                 'requests.get('
                 '"https://binstar-cio-packages-prod.s3.amazonaws.com")')
