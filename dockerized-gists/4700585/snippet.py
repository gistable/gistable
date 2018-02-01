#!/usr/bin/env python
"""
Generates graphs of VLANs and connected hardware/CCIs from data in the
SoftLayer API.
"""
import argparse
import time
import math

import matplotlib.pyplot as plt
import networkx as nx
import SoftLayer


def enum(**enums):
    return type('Enum', (), enums)

Type = enum(DATACENTER=0, PUBLIC_VLAN=1, PRIVATE_VLAN=2, HARDWARE=3, VGUEST=4,
            FIREWALL=5)
GraphLayout = enum(SPRING=0, CIRCULAR=1, RANDOM=2, SHELL=3, SPECTRAL=4)
GraphLayoutMapping = {
    GraphLayout.SPRING: nx.spring_layout,
    GraphLayout.CIRCULAR: nx.circular_layout,
    GraphLayout.RANDOM: nx.random_layout,
    GraphLayout.SHELL: nx.shell_layout,
    GraphLayout.SPECTRAL: nx.spectral_layout,
}


def draw_nodes(G, pos, matches, nodelist=None, **kwargs):
    nodelist = []
    for n, d in G.nodes(data=True):
        if len([True for name, val in matches.items()
               if d.get(name) == val]) == len(matches):
            nodelist.append(n)

    nx.draw_networkx_nodes(G, pos, nodelist=nodelist, **kwargs)


def draw_graph(G, layout=GraphLayout.SPRING, scale=1):
    pos = GraphLayoutMapping.get(layout, nx.spring_layout)(G, scale=scale)

    edgelist = [(u, v) for (u, v, d) in G.edges(data=True)
                if d.get('type') != Type.DATACENTER]
    nx.draw_networkx_edges(G, pos,
                           edgelist=edgelist,
                           label='',
                           width=1 * scale)

    draw_nodes(G, pos, {'type': Type.DATACENTER},
               node_size=200 * scale,
               linewidths=1 * scale,
               node_color='black',
               node_shape='o',
               label='Datacenter')
    draw_nodes(G, pos, {'type': Type.PUBLIC_VLAN},
               node_size=75 * scale,
               linewidths=1 * scale,
               node_color='b',
               node_shape='o',
               label='VLAN (Public)')
    draw_nodes(G, pos, {'type': Type.PRIVATE_VLAN},
               node_size=75 * scale,
               linewidths=1 * scale,
               node_color='b',
               node_shape='s',
               label='VLAN (Private)')
    draw_nodes(G, pos, {'type': Type.HARDWARE},
               node_size=50 * scale,
               linewidths=1 * scale,
               node_color='r',
               node_shape='v',
               label='Hardware')
    draw_nodes(G, pos, {'type': Type.VGUEST},
               node_size=50 * scale,
               linewidths=1 * scale,
               node_color='g',
               node_shape='d',
               label='CCI')
    draw_nodes(G, pos, {'type': Type.FIREWALL},
               node_size=100 * scale,
               linewidths=1 * scale,
               node_color='r',
               node_shape='*',
               label='Firewall')

    leg = plt.legend(loc='lower center', ncol=4, prop={'size': 8})
    leg.get_frame().set_alpha(0.5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generates graphs of VLANs and connected hardware/CCIs '
                    'from data in the SoftLayer API.')
    parser.add_argument(
        '-U', '--username',
        default=None,
        help='SoftLayer username.')
    parser.add_argument(
        '-K', '--api_key',
        default=None,
        help='SoftLayer Api_key.')
    parser.add_argument(
        '--layout',
        choices=['spring', 'circular', 'random', 'shell', 'spectral'],
        default='spring',
        help='Graph layout to use.')
    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='Image DPI')
    parser.add_argument(
        '--show',
        action='store_true',
        default=False,
        help='Show matplotlib viewer')
    args = parser.parse_args()
    graph_layout = getattr(GraphLayout, args.layout.upper())

    print("Fetching from API")
    before = time.time()
    client = SoftLayer.Client(username=args.username, api_key=args.api_key)
    vlans = client['Account'].getNetworkVlans(mask="""
        hardware, virtualGuests, virtualGuestCount,
        primaryRouter[hostname, datacenter], dedicatedFirewallFlag,
        highAvailabilityFirewallFlag
    """)
    print("Fetching from API took %0.2f seconds" % (time.time() - before, ))

    # Create a graph for each datacenter and one for all data.
    print("Building graph data")
    before = time.time()
    datacenter_graphs = {}
    all_graph = nx.Graph()
    for vlan in vlans:
        datacenter_id = vlan['primaryRouter']['datacenter']['id']
        if datacenter_id not in datacenter_graphs:
            datacenter_graphs[datacenter_id] = {
                'graph': nx.Graph(),
                'longName': vlan['primaryRouter']['datacenter']['longName'],
                'name': vlan['primaryRouter']['datacenter']['name'],
            }
        graph = datacenter_graphs[datacenter_id]['graph']
        firewall = False
        if vlan['dedicatedFirewallFlag'] or \
                vlan['highAvailabilityFirewallFlag']:
            firewall = True
        for g in [graph, all_graph]:
            vlan_id = "vlan%s" % vlan['id']
            if vlan['primaryRouter']['hostname'].startswith('bcr'):
                g.add_node(vlan_id, type=Type.PRIVATE_VLAN)
            else:
                g.add_node(vlan_id, type=Type.PUBLIC_VLAN)

            g.add_node(datacenter_id, type=Type.DATACENTER)
            if firewall:
                firewall_id = "firewall%s" % vlan_id
                g.add_node(firewall_id, type=Type.FIREWALL)
                g.add_edge(firewall_id, vlan_id)
                g.add_edge(firewall_id, datacenter_id)
            else:
                g.add_edge(vlan_id, datacenter_id)

            for hardware in vlan['hardware']:
                g.add_node(hardware['hostname'], type=Type.HARDWARE)
                g.add_edge(vlan_id, hardware['hostname'])

            for vguest in vlan['virtualGuests']:
                g.add_node(vguest['hostname'], type=Type.VGUEST)
                g.add_edge(vlan_id, vguest['hostname'])

    # Connect all datacenters to eachother
    for datacenter in datacenter_graphs:
        for datacenter2 in datacenter_graphs:
            if datacenter != datacenter2:
                all_graph.add_edge(datacenter, datacenter2,
                                   type=Type.DATACENTER)

    datacenter_graphs['all'] = {
        'graph': all_graph,
        'longName': 'All Datacenters',
        'name': 'all',
    }
    print("Building graph data took %0.2f seconds" % (time.time() - before, ))

    # Output graphs
    print("Drawing graphs")
    before = time.time()
    for datacenter_key, d in datacenter_graphs.items():
        plt.figure("datacenter_%s" % d['name'])
        plt.axis('off')
        plt.title(d['longName'])
        if d.get('scale'):
            scale = d['scale']
        else:
            # Scale is dynamically determined based on the number of nodes
            scale = -0.10 * math.log(len(d['graph']), math.e) + 1
            scale = max(scale, 0.25)

        draw_graph(d['graph'], layout=graph_layout, scale=scale)
        filename = "graph_%s.png" % d['name']
        print("Writing file: %s" % filename)
        plt.savefig(filename, dpi=args.dpi)
    print("Drawing graphs took %0.2f seconds" % (time.time() - before, ))

    if args.show:
        plt.show()
