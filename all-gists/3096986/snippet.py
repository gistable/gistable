from os import path

from fabric.api import cd, prefix, lcd
from fabric.api import run, sudo as run_as_root, local as run_on_local
from cuisine import package_install_apt, file_exists


def _run(command, sudo=False, local=False):
    if sudo:
        return run_as_root(command)
    if local:
        return run_on_local(command)
    else:
        return run(command)

def package_install_apt_python_pip():
    package_install_apt('python-pip')

def package_install_apt_python_virtualenv():
    package_install_apt('python-virtualenv')

def package_python_pip_bundle(project_dir_path, bundle_file_path, requirements_txt='requirements.txt', local=True):
    params = dict(requirements_txt=path.join(project_dir_path, requirements_txt), bundle_file_path=bundle_file_path)
    pip_bundle = 'pip bundle -r %(requirements_txt)s %(bundle_file_path)s' % params
    if local:
        with lcd(project_dir_path):
            _run(pip_bundle, local=True)
    else:
        with cd(project_dir_path):
            _run(pip_bundle, local=False)

def package_python_pip_freeze(project_dir_path, requirements_txt, local=True):
    params = dict(requirements_txt=requirements_txt)
    pip_freeze = 'pip freeze > %(requirements_txt)s' % params
    if local:
        with lcd(project_dir_path):
            _run(pip_freeze, local=True)
    else:
        with cd(project_dir_path):
            _run(pip_freeze, local=False)

def package_python_pip_install(package, editable=False, sudo=False):
    pip_install = ['pip', 'install']
    if editable:
        pip_install.append('-e')
    pip_install.append(package)
    _run(' '.join(pip_install), sudo=sudo)

def package_python_pip_uninstall(package, sudo=False):
    _run('pip uninstall -y %(package)s' % dict(package=package), sudo=sudo)

def python_virtualenv_create(virtualenv_dir_path):
    _run('virtualenv %(virtualenv_dir_path)s' % dict(virtualenv_dir_path=virtualenv_dir_path))

def python_virtualenv(virtualenv_dir_path):
    activate = path.join(virtualenv_dir_path, 'bin', 'activate')
    return prefix('source %(activate)s' % dict(activate=activate))

def python_gunicorn_paster_start(ini_file_path, pid_file_path, config_file_path=None, daemon=True):
    gunicorn = ['gunicorn_paster']
    if daemon:
        gunicorn.append('--daemon')
    if config_file_path:
        gunicorn.append('--config=%(config_file_path)s' % dict(config_file_path=config_file_path))
    gunicorn.append('--pid=%(pid_file_path)s' % dict(pid_file_path=pid_file_path))
    gunicorn.append(ini_file_path)
    _run(' '.join(gunicorn))

def python_gunicorn_paster_restart(ini_file_path, pid_file_path, config_file_path=None):
    python_gunicorn_stop(pid_file_path)
    python_gunicorn_paster_start(ini_file_path, pid_file_path, config_file_path)

def python_gunicorn_stop(pid_file_path):
    if file_exists(pid_file_path):
        out = _run('ps -p $(cat %(pid_file_path)s)|grep gunicorn')
        if out.stdout and out.succeeded:
            _run('kill $(cat %(pid_file_path)s)' % dict(pid_file_path=pid_file_path), sudo=True)