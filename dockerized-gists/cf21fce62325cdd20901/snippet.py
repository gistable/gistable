import logging
import subprocess
import salt.utils

log = logging.getLogger(__name__)

def primary_interface():
    try:
        import salt.utils.network as network
    except Exception as e:
        log.warn('Could not import salt.utils.network: %s' % e)
        return {}

    grains = {}

    interfaceLabel = _get_default_interface()
    interface = network.interface(interfaceLabel)

    grains['primary_interface'] = interface

    return grains

def _get_default_interface():
    if salt.utils.is_windows():
        return _windows_get_default_interface()
    else:
        return _linux_get_default_interface()

def _windows_get_default_interface():
    powershellScript = ['$interfaceIndices = (Get-NetIPConfiguration | Foreach IPv4DefaultGateway).ifIndex',
    '$primaryInterface = $interfaceIndices | Foreach-Object { Get-NetIPInterface -AddressFamily IPv4 -InterfaceIndex $_ | Sort-Object InterfaceMetric | Select -First 1 }',
    '$primaryInterface | Get-NetAdapter | Select -ExpandProperty InterfaceDescription']
    return subprocess.check_output(['powershell', '-NoProfile', '-Command', ';'.join(powershellScript)]).strip()


def _linux_get_default_interface():
    import shlex
    cmd = shlex.split('ip -4 route list 0/0')
    return subprocess.check_output(cmd).split()[4]
