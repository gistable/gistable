# Note that target_env.login and target_env.password is global variables

# Maybe I should add this into Fabric project (http://docs.fabfile.org/en/1.4.2/index.html).
# This is complicated task for sure but it would be nice if Fabric could use ssh under Linux and PowerShell Remoting under Windows.

def remote_sh(target_host, command_text, ignore_error=False):
    print('run PowerShell script block at {0}: {1}'.format(target_host, command_text))

    command_text = command_text.replace('"', '\'')

    # -NoProfile -NonInteractive PowerShell parameters decrease execution time
    power_shell_text = """\
        powershell -NoProfile -NonInteractive
        \"$secure_password = ConvertTo-SecureString '{1}' -asPlainText -Force;
        $credentials = New-Object Management.Automation.PSCredential('{0}', $secure_password);
        $remote_session = New-PSSession -ComputerName {2} -Credential $credentials;
        Invoke-Command -Session $remote_session -ScriptBlock {{ {3} }};
        $remote_last_exit_code = Invoke-Command -Session $remote_session -ScriptBlock {{ $LastExitCode }};
        Remove-PSSession -Session $remote_session;
        exit $remote_last_exit_code\"""".format(
        target_env.login,
        target_env.password,
        target_host,
        command_text)

    power_shell_text = dedent(power_shell_text).replace('\n', ' ')

    # This print call could be uncommented for debugging purposes
    # print('run shell command: {0}'.format(power_shell_text))

    error_code = os.system(power_shell_text)

    if error_code and not ignore_error:
        raise Exception('Failed to execute PowerShell script block on host {0}. Actual return code was {1} '
            'but only zero value is expected. '
            'Script block is "{2}".'.format(target_host, error_code, command_text))

    return error_code