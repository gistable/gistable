import argparse
import json
import re
import sys
import uuid


class OpenVPNNetworkConfiguration(object):
    KNOWN_CONFIG_KEYS = {
        'name': {'key': 'Name'},
        'startonopen': {'key': 'VPN.AutoConnect', 'value': lambda x: bool(x)},
        'remote': {'key': 'VPN.Host', 'value': lambda x: x.split()[0]},
        'auth': {'key': 'VPN.OpenVPN.Auth'},
        'auth-retry': {'key': 'VPN.OpenVPN.AuthRetry'},
        'auth-nocache': {'key': 'VPN.OpenVPN.AuthNoCache', 'value': True},
        'cipher': {'key': 'VPN.OpenVPN.Cipher'},
        'comp-lzo': {'key': 'VPN.OpenVPN.CompLZO'},
        'comp-noadapt': {'key': 'VPN.OpenVPN.CompNoAdapt', 'value': True},
        'key-direction': {'key': 'VPN.OpenVPN.KeyDirection'},
        'ns-cert-type': {'key': 'VPN.OpenVPN.NsCertType'},
        'port': {'key': 'VPN.OpenVPN.Port', 'value': lambda x: int(x)},
        'proto': {'key': 'VPN.OpenVPN.Proto'},
        'push-peer-info': {'key': 'VPN.OpenVPN.PushPeerInfo', 'value': True},
        'remote-cert-eku': {'key': 'VPN.OpenVPN.RemoteCertEKU'},
        'remote-cert-ku': {'key': 'VPN.OpenVPN.RemoteCertEKU', 'value': lambda x: x.split()},
        'remote-cert-tls': {'key': 'VPN.OpenVPN.RemoteCertTLS'},
        'reneg-sec': {'key': 'VPN.OpenVPN.RenegSec', 'value': lambda x: int(x)},
        'server-poll-timeout': {'key': 'VPN.OpenVPN.ServerPollTimeout', 'value': lambda x: int(x)},
        'shaper': {'key': 'VPN.OpenVPN.Shaper', 'value': lambda x: int(x)},
        'static-challenge': {'key': 'VPN.OpenVPN.StaticChallenge', 'value': lambda x: x.rsplit(maxsplit=1)},
        'tls-remote': {'key': 'VPN.OpenVPN.TLSRemote'},
        'username': {'key': 'VPN.OpenVPN.Username'},
        'verb': {'key': 'VPN.OpenVPN.Verb'},
        'verify-hash': {'key': 'VPN.OpenVPN.VerifyHash'},
        'verify-x509-name': {
            'key': 'VPN.OpenVPN.VerifyX509', 'value': lambda x: {i[0]: i[1] for i in zip(['Name', 'Type'], x.split())}
        },
    }

    OPENVPN_KEYS = [
        'Auth',
        'AuthRetry',
        'AuthNoCache',
        'Cipher',
        'ClientCertRef',
        'ClientCertPattern',
        'ClientCertType',
        'CompLZO',
        'CompNoAdapt',
        'IgnoreDefaultRoute',
        'KeyDirection',
        'NsCertType',
        'Password',
        'Port',
        'Proto',
        'PushPeerInfo',
        'RemoteCertEKU',
        'RemoteCertKU',
        'RemoteCertTLS',
        'RenegSec',
        'SaveCredentials',
        'ServerCARefs',
        'ServerCertRef',
        'ServerPollTimeout',
        'Shaper',
        'StaticChallenge',
        'TLSAuthContents',
        'TLSRemote',
        'Username',
        'Verb',
        'VerifyHash',
        'VerifyX509',
    ]

    def __init__(self):
        self.openvpn = {}
        self.vpn = {
            'Type': 'OpenVPN',
            'AutoConnect': False,
            'Host': None,
            'OpenVPN': self.openvpn
        }
        self.network_config = {
            'GUID': str(uuid.uuid4()),
            'Name': None,
            'Type': 'VPN',
            'VPN': self.vpn
        }
        self.onc = {
            'Type': 'UnencryptedConfiguration',
            'NetworkConfigurations': [self.network_config],
            'Certificates': []
        }

    def init_with_file(self, f):
        lines = f.readlines()
        lines = self.transform_config(lines)
        self.parse_openvpn_config(lines)

    @staticmethod
    def transform_config(lines):
        _lines = []
        multiline = None
        for line in lines:
            if not multiline and re.match(r'\A\s*<[a-z-]+>', line):
                multiline = line.strip()
            elif multiline and re.match(r'\A\s*</[a-z-]+>', line):
                _lines.append(multiline + '\n' + line.strip())
                multiline = None
            elif multiline:
                multiline += ('\n' + line.strip())
            else:
                parts = line.strip().split(' ', 1)
                command = parts[0]
                args = None
                if len(parts) > 1:
                    args = parts[1]
                if command == 'remote' and len(args.split()) == 3:
                    args = args.split()
                    _lines.append('remote {}'.format(args[0]))
                    _lines.append('port {}'.format(args[1]))
                    _lines.append('proto {}'.format(args[2]))
                else:
                    _lines.append(line.strip())
        return _lines

    def parse_openvpn_config(self, lines):
        for line in lines:
            if re.match(r'\A\s*#viscosity', line):
                line = re.match(r'\A\s*#viscosity(.*)', line).group(1)
            elif re.match(r'\A\s*#', line):
                continue
            parts = line.strip().split(' ', 1)
            command = parts[0]
            args = None
            if len(parts) > 1:
                args = parts[1]
            if command in self.KNOWN_CONFIG_KEYS:
                spec = self.KNOWN_CONFIG_KEYS[command]
                value = spec.get('value', args)
                if callable(value):
                    value = value(args)
                _dict = self.network_config
                key_parts = spec['key'].split('.')
                for k in key_parts[:-1]:
                    _dict = _dict[k]
                _dict[key_parts[-1]] = value
            elif command.startswith('<tls-auth>'):
                self.openvpn['TLSAuthContents'] = '\n'.join(
                    re.search('<tls-auth>(.*?)</tls-auth>', line, re.DOTALL).group(1).strip().split('\n'))
            elif command.startswith('<ca>'):
                _cas = []
                _ca_uuids = []
                for ca in re.findall(r'-----BEGIN CERTIFICATE-----(.*?)-----END CERTIFICATE-----', line, re.DOTALL):
                    guid = str(uuid.uuid4())
                    _ca = ''.join(ca.strip().split())
                    _cas.append(_ca)
                    _ca_uuids.append(guid)
                    self.onc['Certificates'].append({
                        'GUID': guid,
                        'Type': 'Authority',
                        'X509': _ca
                    })
                self.openvpn['ServerCARefs'] = [_ca_uuids[0]]
                self.openvpn['ClientCertType'] = 'Pattern'
                self.openvpn['ClientCertPattern'] = {'IssuerCARef': [_ca_uuids[-1]]}

    def to_json(self, outfile=None):
        if outfile:
            json.dump(self.onc, outfile, sort_keys=True, indent=2, separators=(',', ': '))
        else:
            return json.dumps(self.onc, sort_keys=True, indent=2, separators=(',', ': '))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--infile',
        metavar='OPENVPN_CONFIG_FILE',
        help='OpenVPN config file to be converted. If not present, stdin is used.',  # NOQA
        default=None
    )
    parser.add_argument(
        '--outfile',
        metavar='ONC_FILE',
        help='Path to output ONC file. If not present, stdout is used.',
        default=None
    )
    args = parser.parse_args()

    infile = sys.stdin
    outfile = sys.stdout
    if args.infile:
        infile = open(args.infile, 'r')
    if args.outfile:
        outfile = open(args.outfile, 'w')

    c = OpenVPNNetworkConfiguration()
    c.init_with_file(infile)
    c.openvpn['Password'] = 'not_used'
    c.openvpn['IgnoreDefaultRoute'] = True
    c.to_json(outfile)
    infile.close()
    outfile.close()

if __name__ == '__main__':
    main()