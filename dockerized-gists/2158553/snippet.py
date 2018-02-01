import SoftLayer.API
import ipaddr


def splitIpCidrNotation(arg):
    ipv4 = ipaddr.IPv4Network(arg)
    return str(ipv4.ip), str(ipv4.netmask)


def getClients(user, key):
    accountClient = SoftLayer.API.Client('SoftLayer_Account', None, user, key)
    vlanClient = SoftLayer.API.Client('SoftLayer_Network_Vlan', None, user, key)
    firewallUpdateRequestClient = SoftLayer.API.Client('SoftLayer_Network_Firewall_Update_Request', None, user, key)
    return accountClient, vlanClient, firewallUpdateRequestClient


def findAccessControlListByIp(client, ip):
    mask = {
        'firewallInterfaces': {
            'firewallContextAccessControlLists': {
                'rules': {}
            }
        }
    }

    client.set_object_mask(mask)
    networkVlan = client.getVlanForIpAddress(ip)
    for firewall in networkVlan['firewallInterfaces']:
        if firewall['name'] == 'inside':
            continue
        for controlList in firewall['firewallContextAccessControlLists']:
            if controlList['direction'] == 'out':
                continue
            firewallContextAccessControlListId = controlList['id']
            rules = controlList['rules']

    return firewallContextAccessControlListId, rules


def createUpdateRequstTemplateObject(client, sourceCidr, destCidr, action, protocol, port):

    destIp, destMask = splitIpCidrNotation(destCidr)
    destIps = ipaddr.IPv4Network(destCidr)
    firewallContextAccessControlListId, rules = findAccessControlListByIp(client, destIp)

    if sourceCidr != 'any':
        sourceIp, sourceMask = splitIpCidrNotation(sourceCidr)
    else:
        sourceIp = 'any'

    i = len(rules) + 1
    for destIp in destIps.iterhosts():
        newRule = {
            'action': action,
            'destinationIpAddress': str(destIp),
            'destinationIpSubnetMask': '255.255.255.255',
            'sourceIpAddress': sourceIp,
            'sourceIpSubnetMask': sourceMask,
            'protocol': protocol,
            'destinationPortRangeStart': port,
            'destinationPortRangeEnd': port,
            'orderValue': i,
        }
        i = i + 1
        rules.append(newRule)

    templateObject = {
        'firewallContextAccessControlListId': firewallContextAccessControlListId,
        'rules': rules
    }

    return templateObject


def updateFirewall(vlanClient, sourceCidr, destCidr, port, protocol, action, firewallUpdateRequestClient):
    return firewallUpdateRequestClient.createObject(createUpdateRequstTemplateObject(vlanClient, sourceCidr, destCidr, action, protocol, port))


def main_cli():
    from argparse import ArgumentParser
    from pprint import pprint

    parser = ArgumentParser(description='Create a SoftLayer Firewall Rule')
    parser.add_argument('-s', nargs=1, type=str, required=True, metavar="Source", help="Source IP in short CIDR Notation",
        dest="sourceCidr")
    parser.add_argument('-d', nargs=1, type=str, required=True, metavar="Destination", help="Destination IP in short CIDR Notation",
        dest="destCidr")
    parser.add_argument('-r', nargs=1, type=int, required=True, metavar='Port', help='Destination Port', dest='port')
    parser.add_argument('-p', nargs=1, type=str, required=True, metavar='Protocol', help='Protocol tcp/udp',
        dest='protocol')
    parser.add_argument('-a', nargs=1, type=str, required=True, metavar='Action', help='Action the rule will impliment: permit/deny',
        dest='action')

    args = parser.parse_args()

    apiUsername = ""
    apiKey = ""
    accountClient, vlanClient, firewallUpdateRequestClient = getClients(apiUsername, apiKey)
    pprint(updateFirewall(vlanClient, args.sourceCidr[0], args.destCidr[0], args.port[0], args.protocol[0], args.action[0], firewallUpdateRequestClient))


if __name__ == "__main__":
    main_cli()
