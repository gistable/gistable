#!/usr/bin/env python

'''
tr -s ' ' < tpcc_pg_report.vmstat | sed 's/^ //g' | sed 's/ /,/g' > tpcc_pg_report.vmstat.csv
'''

from __future__ import division

import csv
from itertools import izip_longest


def grouper(n, iterable, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def parse_vm_csv(vmReader):
    timestamp = 1
    data = []

    # Skip the header lines
    vmReader.next()
    vmReader.next()

    for row in vmReader:
        data.append({
            'timestamp': timestamp,
            'procs_r': int(row[0]),  # The number of processes waiting for run time.
            'procs_b': int(row[1]),  # The number of processes in uninterruptible sleep.
            'memory_swpd': int(row[2]),  # the amount of virtual memory used.
            'memory_free': int(row[3]),  # the amount of idle memory.
            'memory_buff': int(row[4]),  # the amount of memory used as buffers.
            'memory_cache': int(row[5]),  # the amount of memory used as cache.
            'swap_si': int(row[6]),  # Amount of memory swapped in from disk (/s).
            'swap_so': int(row[7]),  # Amount of memory swapped to disk (/s).
            'io_bi': int(row[8]),  # Blocks received from a block device (blocks/s).
            'io_bo': int(row[9]),  # Blocks sent to a block device (blocks/s).
            'system_in': int(row[10]),  # The number of interrupts per second, including the clock.
            'system_cs': int(row[11]),  # The number of context switches per second.
            'cpu_us': int(row[12]),  # Time spent running non-kernel code. (user time, including nice time)
            'cpu_sy': int(row[13]),  # Time spent running kernel code. (system time)
            'cpu_id': int(row[14]),  # Time spent idle.
            'cpu_wa': int(row[15]),  # Time spent waiting for IO.
            'cpu_st': int(row[16]),  # Time stolen from a virtual machine.
        })
        timestamp += 1
        if timestamp > 25000:
            break

    data_averaged = []
    for rows in grouper(60, data):
        # Filter out the None values
        clean_rows = []
        for row in rows:
            if row:
                clean_rows.append(row)

        data_averaged.append({
            'timestamp': clean_rows[0]['timestamp'],
            'procs_r': sum([x['procs_r'] for x in clean_rows]) / len(clean_rows),
            'procs_b': sum([x['procs_b'] for x in clean_rows]) / len(clean_rows),
            'memory_swpd': sum([x['memory_swpd'] for x in clean_rows]) / len(clean_rows),
            'memory_free': sum([x['memory_free'] for x in clean_rows]) / len(clean_rows),
            'memory_buff': sum([x['memory_buff'] for x in clean_rows]) / len(clean_rows),
            'memory_cache': sum([x['memory_cache'] for x in clean_rows]) / len(clean_rows),
            'swap_si': sum([x['swap_si'] for x in clean_rows]) / len(clean_rows),
            'swap_so': sum([x['swap_so'] for x in clean_rows]) / len(clean_rows),
            'io_bi': sum([x['io_bi'] for x in clean_rows]) / len(clean_rows),
            'io_bo': sum([x['io_bo'] for x in clean_rows]) / len(clean_rows),
            'system_in': sum([x['system_in'] for x in clean_rows]) / len(clean_rows),
            'system_cs': sum([x['system_cs'] for x in clean_rows]) / len(clean_rows),
            'cpu_us': sum([x['cpu_us'] for x in clean_rows]) / len(clean_rows),
            'cpu_sy': sum([x['cpu_sy'] for x in clean_rows]) / len(clean_rows),
            'cpu_id': sum([x['cpu_id'] for x in clean_rows]) / len(clean_rows),
            'cpu_wa': sum([x['cpu_wa'] for x in clean_rows]) / len(clean_rows),
            'cpu_st': sum([x['cpu_st'] for x in clean_rows]) / len(clean_rows),
        })
    return data_averaged


ibm = parse_vm_csv(csv.reader(open('ibm1/tpcc_pg_report.vmstat.csv', 'rb')))
dell = parse_vm_csv(csv.reader(open('r620/tpcc_pg_report.vmstat.csv', 'rb')))
assert(len(ibm) == len(dell))

writer = csv.writer(open('cpu_usage.csv', 'wb'), dialect=csv.excel)
writer.writerow(['timestamp', 'ibm_cpu_us', 'ibm_cpu_sy', 'ibm_cpu_id', 'ibm_cpu_wa', 'dell_cpu_us', 'dell_cpu_sy', 'dell_cpu_id', 'dell_cpu_wa'])
for i in range(0, len(ibm)):
    ibm_row = ibm[i]
    dell_row = dell[i]
    writer.writerow([ibm_row['timestamp'], ibm_row['cpu_us'], ibm_row['cpu_sy'], ibm_row['cpu_id'], ibm_row['cpu_wa'], dell_row['cpu_us'], dell_row['cpu_sy'], dell_row['cpu_id'], dell_row['cpu_wa']])

writer = csv.writer(open('memory.csv', 'wb'), dialect=csv.excel)
writer.writerow(['timestamp', 'ibm_memory_swpd', 'ibm_memory_free', 'ibm_memory_buff', 'ibm_memory_cache', 'dell_memory_swpd', 'dell_memory_free', 'dell_memory_buff', 'dell_memory_cache'])
for i in range(0, len(ibm)):
    ibm_row = ibm[i]
    dell_row = dell[i]
    writer.writerow([ibm_row['timestamp'], ibm_row['memory_swpd'], ibm_row['memory_free'], ibm_row['memory_buff'], ibm_row['memory_cache'], dell_row['memory_swpd'], dell_row['memory_free'], dell_row['memory_buff'], dell_row['memory_cache']])

writer = csv.writer(open('system.csv', 'wb'), dialect=csv.excel)
writer.writerow(['timestamp', 'ibm_system_in', 'ibm_system_cs', 'dell_system_in', 'dell_system_cs'])
for i in range(0, len(ibm)):
    ibm_row = ibm[i]
    dell_row = dell[i]
    writer.writerow([ibm_row['timestamp'], ibm_row['system_in'], ibm_row['system_cs'], dell_row['system_in'], dell_row['system_cs']])

writer = csv.writer(open('io.csv', 'wb'), dialect=csv.excel)
writer.writerow(['timestamp', 'ibm_io_bi', 'ibm_io_bo', 'dell_io_bi', 'dell_io_bo'])
for i in range(0, len(ibm)):
    ibm_row = ibm[i]
    dell_row = dell[i]
    writer.writerow([ibm_row['timestamp'], ibm_row['io_bi'], ibm_row['io_bo'], dell_row['io_bi'], dell_row['io_bo']])
