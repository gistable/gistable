#!/usr/bin/env python

# $ cat ipsec_conf.tmpl
# {#
#  
#   cgw_in_addr: customer_gateway tunnel_inside_address ip_address
#   cgw_in_cidr: customer_gateway tunnel_inside_address network_cidr
#   vgw_in_addr: vpn_gateway tunnel_inside_address ip_address
#   vgw_in_cidr: vpn_gateway tunnel_inside_address network_cidr
#   cgw_out_addr: customer_gateway tunnel_outside_address
#   vgw_out_addr: vpn_gateway tunnel_outside_address
# -#}
# 
# spdadd {{ cgw_in_addr }}/{{ cgw_in_cidr }} {{ vgw_in_addr }}/{{ vgw_in_cidr }} any -P out ipsec
#    esp/tunnel/{{ cgw_out_addr }}-{{ vgw_out_addr }}/require;
# spdadd {{ vgw_in_addr }}/{{ vgw_in_cidr }} {{ cgw_in_addr }}/{{ cgw_in_cidr }} any -P in ipsec
#    esp/tunnel/{{ vgw_out_addr }}-{{ cgw_out_addr }}/require;
#
# $ cat racoon_conf.tmpl
# remote {{ vgw_out_addr }} {
#     exchange_mode {{ mode }};
#     lifetime time {{ ike_lifetime }} seconds;
#     proposal {
#         encryption_algorithm {{ ike_encryption_protocol }};
#         hash_algorithm {{ ike_authentication_protocol }};
#         authentication_method pre_shared_key;
#         dh_group {{ ike_perfect_forward_secrecy }};
#     }
#     dpd_delay {{ dpd_delay }};
#     dpd_retry {{ dpd_retry }};
#     generate_policy off;
# }
# 
# sainfo address {{ cgw_in_addr }}/{{ cgw_in_cidr }} any address {{ vgw_in_addr }}/{{ vgw_in_cidr }} any {
#     pfs_group {{ ipsec_perfect_forward_secrecy }};
#     encryption_algorithm {{ ipsec_encryption_protocol }};
#     authentication_algorithm {{ ipsec_authentication_protocol }};
#     compression_algorithm deflate;
#     lifetime time {{ ipsec_lifetime }} seconds;
# }

import sys
import boto3
import xmltodict
from jinja2 import Template

profile = sys.argv[1]

s = boto3.Session(profile_name=profile)
ec2 = s.client('ec2')

vpn = ec2.describe_vpn_connections()
x = vpn['VpnConnections'][0]['CustomerGatewayConfiguration']

d = xmltodict.parse(x)

tunnels = d['vpn_connection']['ipsec_tunnel']

with open('racoon_conf.tmpl') as f:
    racoon_conf = f.read()
with open('ipsec_conf.tmpl') as f:
    ipsec_conf = f.read()

tnum = 1
templaterac = Template(racoon_conf)
templateips = Template(ipsec_conf)
for tun in tunnels:
    cgw_in_addr = tun['customer_gateway']['tunnel_inside_address']['ip_address']
    cgw_in_cidr = tun['customer_gateway']['tunnel_inside_address']['network_cidr']
    vgw_in_addr = tun['vpn_gateway']['tunnel_inside_address']['ip_address']
    vgw_in_cidr = tun['vpn_gateway']['tunnel_inside_address']['network_cidr']
    cgw_out_addr = tun['customer_gateway']['tunnel_outside_address']['ip_address']
    vgw_out_addr = tun['vpn_gateway']['tunnel_outside_address']['ip_address']
    
    print('\n#\n# psk.txt - {0} tunnel {1}\n#'.format(profile.title(), tnum))
    print('{0}\t{1}'.format(
        vgw_out_addr,
        tun['ike']['pre_shared_key'])
    )
    print('\n#\n# racoon.conf - {0} tunnel {1}\n#'.format(profile.title(), tnum))
    print(templaterac.render(
        vgw_out_addr =
            tun['vpn_gateway']['tunnel_outside_address']['ip_address'],
        mode = tun['ike']['mode'],
        ike_lifetime = tun['ike']['lifetime'],
        ike_encryption_protocol =
            ''.join(tun['ike']['encryption_protocol'].split('-')[:2]),
        ike_authentication_protocol = tun['ike']['authentication_protocol'],
        ike_perfect_forward_secrecy =
            tun['ike']['perfect_forward_secrecy'][-1],
        dpd_retry = tun['ipsec']['dead_peer_detection']['retries'],
        dpd_delay = tun['ipsec']['dead_peer_detection']['interval'],
        cgw_in_addr = cgw_in_addr,
        cgw_in_cidr = cgw_in_cidr,
        vgw_in_addr = vgw_in_addr,
        vgw_in_cidr = vgw_in_cidr,
        ipsec_perfect_forward_secrecy =
            tun['ipsec']['perfect_forward_secrecy'][-1],
        ipsec_encryption_protocol =
            ''.join(tun['ipsec']['encryption_protocol'].split('-')[:2]),
        ipsec_authentication_protocol =
            '_'.join(tun['ipsec']['authentication_protocol'].split('-')[:2]),
        ipsec_lifetime = tun['ipsec']['lifetime']
                
    ))
    print('\n#\n# ipsec.conf - {0} tunnel {1}\n#'.format(profile.title(), tnum))
    print(templateips.render(
        cgw_in_addr = cgw_in_addr,
        cgw_in_cidr = cgw_in_cidr,
        vgw_in_addr = vgw_in_addr,
        vgw_in_cidr = vgw_in_cidr,
        cgw_out_addr = cgw_out_addr,
        vgw_out_addr = vgw_out_addr
    ))
    print('\n')

    tnum += 1