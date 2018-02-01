import sys
import time
import subprocess
import types
from tempfile import TemporaryFile

def remote_sh(target_host, login, password, command_text, stdout=None, stderr=None):
    winrs_text = 'winrs -remote:{0} -username:{1} -password:{2} -noprofile {3}'.format(
        target_host, login, password, command_text)
    #print('winrs text: {0}\n'.format(winrs_text))

    with TemporaryFile() as stdout_file, TemporaryFile() as stderr_file:
        process = subprocess.Popen(winrs_text, stdout=stdout_file, stderr=stderr_file, stdin=subprocess.PIPE)

        while process.poll() is None:
            time.sleep(1)

        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout_str = stdout_file.read()
        stderr_str = stderr_file.read()

        if stdout:
            stdout.write(stdout_str)

        if stderr:
            stderr.write(stderr_str)

        return stdout_str.rstrip(), stderr_str.rstrip(), process.returncode

def winrm_instead_ssh():
    ssh_module = types.ModuleType('ssh')
    sys.modules['ssh'] = ssh_module

    # Stub for Crypto.Random module
    crypto_module = types.ModuleType('Crypto')
    random_module = types.ModuleType('Random')
    setattr(crypto_module, 'Random', random_module)
    sys.modules['Crypto'] = crypto_module

    # Stub for fabric.network.HostConnectionCache class
    #host_connection_cache_class = types.ClassType('HostConnectionCache', (object,), {})

    # Stub for fabric.state.default_channel function
    from fabric import state
    state.default_channel = lambda: None

    from fabric.state import env, win32

    def _prefix_env_vars(command):
        """
        Prefixes ``command`` with any shell environment vars, e.g. ``PATH=foo ``.

        Currently, this only applies the PATH updating implemented in
        `~fabric.context_managers.path`.
        """
        # path(): local shell env var update, appending/prepending/replacing $PATH
        path = env.path
        if path:
            # TODO change into if ssh transport then:
            if not win32:
                if env.path_behavior == 'append':
                    path = 'PATH=$PATH:\"%s\" ' % path
                elif env.path_behavior == 'prepend':
                    path = 'PATH=\"%s\":$PATH ' % path
                elif env.path_behavior == 'replace':
                    path = 'PATH=\"%s\" ' % path
            else:
                # TODO path with spaces are not supported yet.
                # It is possible escape path into double quotes but later all double quotes
                # will be escaped and this is not expected behavior.
                if env.path_behavior == 'append':
                    path = 'SET PATH=%PATH%;{0}; && '.format(path)
                elif env.path_behavior == 'prepend':
                    path = 'SET PATH={0};%PATH%; && '.format(path)
                elif env.path_behavior == 'replace':
                    path = 'SET PATH={0}; && '.format(path)
        else:
            path = ''
        return path + command

    from fabric.state import output

    def _execute(channel, command, pty=True, combine_stderr=None,
                 invoke_shell=False, stdout=None, stderr=None):
        # stdout/stderr redirection
        stdout = (stdout or sys.stdout) if output.stdout else None
        stderr = (stderr or sys.stderr) if output.stderr else None
        return remote_sh(env.host_string, env.user, env.password, command, stdout=stdout, stderr=stderr)

    from fabric import operations
    operations._execute = _execute
    operations._prefix_env_vars = _prefix_env_vars

    from fabric.context_managers import settings
    from fabric.context_managers import hide
    from fabric.operations import sudo, run

    def exists(path, use_sudo=False, verbose=False):
        """
        Return True if given path exists on the current remote host.

        If ``use_sudo`` is True, will use `sudo` instead of `run`.

        `exists` will, by default, hide all output (including the run line, stdout,
        stderr and any warning resulting from the file not existing) in order to
        avoid cluttering output. You may specify ``verbose=True`` to change this
        behavior.
        """
        func = use_sudo and sudo or run
        cmd = 'if exist %s (echo 1) else (echo 0)' % path
        # If verbose, run normally
        if verbose:
            with settings(warn_only=True):
                return bool(int(func(cmd).stdout))
                # Otherwise, be quiet
        with settings(hide('everything'), warn_only=True):
            return bool(int(func(cmd).stdout))

    from fabric.contrib import files
    files.exists = exists
