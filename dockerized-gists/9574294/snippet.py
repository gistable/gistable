#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79 autoindent

"""
Python source code
Last modified: 15 Feb 2014 - 13:38
Last author: lmwangi at gmail  com

Displays the available memory fragments
by querying /proc/buddyinfo

Example:
# python buddyinfo.py

"""
import optparse
import os
import re
from collections import defaultdict
import logging


class Logger:
    def __init__(self, log_level):
        self.log_level = log_level

    def get_formatter(self):
        return logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def get_handler(self):
        return logging.StreamHandler()

    def get_logger(self):
        """Returns a Logger instance for the specified module_name"""
        logger = logging.getLogger('main')
        logger.setLevel(self.log_level)
        log_handler = self.get_handler()
        log_handler.setFormatter(self.get_formatter())
        logger.addHandler(log_handler)
        return logger


class BuddyInfo(object):
    """BuddyInfo DAO"""
    def __init__(self, logger):
        super(BuddyInfo, self).__init__()
        self.log = logger
        self.buddyinfo = self.load_buddyinfo()

    def parse_line(self, line):
        line = line.strip()
        self.log.debug("Parsing line: %s" % line)
        parsed_line = re.match("Node\s+(?P<numa_node>\d+).*zone\s+(?P<zone>\w+)\s+(?P<nr_free>.*)", line).groupdict()
        self.log.debug("Parsed line: %s" % parsed_line)
        return parsed_line

    def read_buddyinfo(self):
        buddyhash = defaultdict(list)
        buddyinfo = open("/proc/buddyinfo").readlines()
        for line in map(self.parse_line, buddyinfo):
            numa_node =  int(line["numa_node"])
            zone = line["zone"]
            free_fragments = map(int, line["nr_free"].split())
            max_order = len(free_fragments)
            fragment_sizes = self.get_order_sizes(max_order)
            usage_in_bytes =  [block[0] * block[1] for block in zip(free_fragments, fragment_sizes)]
            buddyhash[numa_node].append({
                "zone": zone,
                "nr_free": free_fragments,
                "sz_fragment": fragment_sizes,
                "usage": usage_in_bytes })
        return buddyhash

    def load_buddyinfo(self):
        buddyhash = self.read_buddyinfo()
        self.log.info(buddyhash)
        return buddyhash

    def page_size(self):
        return os.sysconf("SC_PAGE_SIZE")

    def get_order_sizes(self, max_order):
        return [self.page_size() * 2**order for order in range(0, max_order)]

    def __str__(self):
        ret_string = ""
        width = 20
        for node in self.buddyinfo:
            ret_string += "Node: %s\n" % node
            for zoneinfo in self.buddyinfo.get(node):
                ret_string += " Zone: %s\n" % zoneinfo.get("zone")
                ret_string += " Free KiB in zone: %.2f\n" % (sum(zoneinfo.get("usage")) / (1024.0))
                ret_string += '\t{0:{align}{width}} {1:{align}{width}} {2:{align}{width}}\n'.format(
                        "Fragment size", "Free fragments", "Total available KiB",
                        width=width,
                        align="<")
                for idx in range(len(zoneinfo.get("sz_fragment"))):
                    ret_string += '\t{order:{align}{width}} {nr:{align}{width}} {usage:{align}{width}}\n'.format(
                        width=width,
                        align="<",
                        order = zoneinfo.get("sz_fragment")[idx],
                        nr = zoneinfo.get("nr_free")[idx],
                        usage = zoneinfo.get("usage")[idx] / 1024.0)

        return ret_string

def main():
    """Main function. Called when this file is a shell script"""
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-s", "--size", dest="size", choices=["B","K","M"],
                      action="store", type="choice", help="Return results in bytes, kib, mib")

    (options, args) = parser.parse_args()
    logger = Logger(logging.DEBUG).get_logger()
    logger.info("Starting....")
    logger.info("Parsed options: %s" % options)
    print logger
    buddy = BuddyInfo(logger)
    print buddy

if __name__ == '__main__':
    main()