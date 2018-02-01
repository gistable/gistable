#!/usr/bin/env python

import ast
import json
import os
import subprocess
import argparse
import sys

FNULL = open(os.devnull, 'w')

# assume the osdmap test output
# is the same lenght and order...
# if add support for PG increase
# that's gonna break
def diff_output(original, new, pools):
    number_of_osd_remap = 0
    osd_data_movement = 0

    results = {}

    pg_data, pg_objects = get_pg_info()

    for i in range(len(original)):
        orig_i = original[i]
        new_i = new[i]

        if orig_i[0].isdigit():
            pg_id = orig_i.split('\t')[0]
            pool_id = pg_id.split('.')[0]
            pool_name = pools[pool_id]['pool_name']

            if not pool_name in results:
                results[pool_name] = {}
                results[pool_name]['osd_remap_counter'] = 0
                results[pool_name]['osd_bytes_movement'] = 0
                results[pool_name]['osd_objects_movement'] = 0

            original_mappings = ast.literal_eval(orig_i.split('\t')[1])
            new_mappings = ast.literal_eval(new_i.split('\t')[1])
            intersection = list(set(original_mappings).intersection(set(new_mappings)))

            osd_movement_for_this_pg = int(pools[pool_id]['pool_size']) - len(intersection)
            osd_data_movement_for_this_pg = int(osd_movement_for_this_pg) * int(pg_data[pg_id])
            osd_object_movement_for_this_pg = int(osd_movement_for_this_pg) * int(pg_objects[pg_id])

            results[pool_name]['osd_remap_counter'] += osd_movement_for_this_pg
            results[pool_name]['osd_bytes_movement'] += int(osd_data_movement_for_this_pg)
            results[pool_name]['osd_objects_movement'] += int(osd_object_movement_for_this_pg)

        elif orig_i.startswith('#osd'):
            break

    return results

def get_pools_info(osdmap_path):
    pools = {}
    args = ['osdmaptool', '--print', osdmap_path]
    osdmap_out = subprocess.check_output(args, stderr=FNULL).split('\n')
    for line in osdmap_out:
        if line.startswith('pool'):
            pool_id = line.split()[1]
            pool_size = line.split()[5]
            pool_name = line.split()[2].replace("'","")
            pools[pool_id] = {}
            pools[pool_id]['pool_size'] = pool_size
            pools[pool_id]['pool_name'] = pool_name
        elif line.startswith('max_osd'):
            break

    return pools

def get_osd_map(osdmap_path):
    args = ['sudo', 'ceph', 'osd', 'getmap', '-o', osdmap_path]
    subprocess.call(args, stdout=FNULL, stderr=subprocess.STDOUT)

def get_pg_info():
    pg_data = {}
    pg_objects = {}
    args = ['sudo', 'ceph', 'pg', 'dump']
    pgmap = subprocess.check_output(args, stderr=FNULL).split('\n')

    for line in pgmap:
        if line[0].isdigit():
            pg_id = line.split('\t')[0]
            pg_bytes = line.split('\t')[6]
            pg_obj = line.split('\t')[1]
            pg_data[pg_id] = pg_bytes
            pg_objects[pg_id] = pg_obj
        elif line.startswith('pool'):
            break

    return pg_data, pg_objects

def osdmaptool_test_map_pgs_dump(original_osdmap_path, crushmap):
    new_osdmap_path = original_osdmap_path + '.new'
    get_osd_map(original_osdmap_path)
    args = ['osdmaptool', '--test-map-pgs-dump', original_osdmap_path]
    original_osdmaptool_output = subprocess.check_output(args, stderr=FNULL).split('\n')

    args = ['cp', original_osdmap_path, new_osdmap_path]
    subprocess.call(args, stdout=FNULL, stderr=subprocess.STDOUT)
    args = ['osdmaptool', '--import-crush', crushmap, new_osdmap_path]
    subprocess.call(args, stdout=FNULL, stderr=subprocess.STDOUT)
    args = ['osdmaptool', '--test-map-pgs-dump', new_osdmap_path]
    new_osdmaptool_output = subprocess.check_output(args, stderr=FNULL).split('\n')

    pools = get_pools_info(original_osdmap_path)
    results = diff_output(original_osdmaptool_output, new_osdmaptool_output, pools)

    return results


def dump_plain_output(results):
    sys.stdout.write("%-20s %-20s %-20s %-20s\n" % ("POOL", "REMAPPED OSDs", "BYTES REBALANCE", "OBJECTS REBALANCE"))

    for pool in results:
        sys.stdout.write("%-20s %-20s %-20s %-20s\n" % (
            pool,
            results[pool]['osd_remap_counter'],
            results[pool]['osd_bytes_movement'],
            results[pool]['osd_objects_movement']
            ))

def cleanup(osdmap):
    FNULL.close()
    new_osdmap = osdmap + '.new'
    os.remove(new_osdmap)

def parse_args():
    parser = argparse.ArgumentParser(description='Ceph CRUSH change data movement calculator.')

    parser.add_argument(
        '--osdmap-file',
        help="Where to save the original osdmap. Temp one will be <location>.new. Default: /tmp/osdmap",
        default="/tmp/osdmap",
        dest="osdmap_path"
        )
    parser.add_argument(
        '--crushmap-file',
        help="CRUSHmap to run the movement test against.",
        required=True,
        dest="new_crushmap"
        )

    parser.add_argument(
        '--format',
        help="Output format. Default: plain",
        choices=['json', 'plain'],
        dest="format",
        default="plain"
        )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    ctx = parse_args()

    results = osdmaptool_test_map_pgs_dump(ctx.osdmap_path, ctx.new_crushmap)
    cleanup(ctx.osdmap_path)

    if ctx.format == 'json':
        print json.dumps(results)
    elif ctx.format == 'plain':
        dump_plain_output(results)
