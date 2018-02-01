#!/usr/bin/env python

from __future__ import with_statement

import contextlib
import logging
import os
import sys
import urllib2
from boto.ec2.connection import EC2Connection
from optparse import OptionParser
from subprocess import check_call

def get_ec2_metadata(key):
    res = urllib2.urlopen("http://169.254.169.254/2008-02-01/meta-data/" + key)
    return res.read().strip()

def build_parser():
    parser = OptionParser(usage="Usage: %prog [options] <command> ...")
    parser.add_option("-d", "--dryrun", dest="dryrun", help="Show what would be done but don't take any action", default=False, action="store_true")
    parser.add_option("-k", "--awskeys", dest="awskeys", help="AWS key and secret key separated by a colon")
    parser.add_option("-l", "--locker", dest="lockers", help="Locker for specific services (mongo, mysql, ...) e.g. -l mongodb:port=27018", default=[], action="append")
    parser.add_option("-m", "--mount", dest="mount_point", help="Mount point of volume to snapshot")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true")
    return parser

def get_device_for_mount(mount_point):
    if not os.path.exists(mount_point):
        sys.stderr.write("Mount point %s does not exist\n" % mount_point)
        sys.exit(1)

    with open("/proc/mounts", "r") as fp:
        for line in fp:
            line = line.strip().split(' ')
            if line[1] == mount_point:
                return line[0]

    sys.stderr.write("Path %s does not refer to a mount point\n" % mount_point)
    sys.exit(1)

def get_devices_for_raid(device):
    devname = device.rsplit('/', 1)[-1]
    with open("/proc/mdstat", "r") as fp:
        for line in fp:
            line = [x for x in line.strip().split(' ') if x]
            if line and line[0] == devname:
                mdevs = []
                for x in line[4:]:
                    dev, num = x.split('[', 1)
                    num = num[:-1]
                    mdevs.append((int(num), dev if dev.startswith('/') else "/dev/"+dev))
                mdevs.sort()
                return [x[1] for x in mdevs]

    sys.stderr.write("Can't figure out devices for RAID device %s\n" % device)
    sys.exit(1)

class XFSLocker(object):
    def __init__(self, mount_point, dryrun=False):
        self.mount_point = mount_point
        self.dryrun = dryrun
    
    def validate(self):
        return True
    
    def __enter__(self):
        logging.info("Freezing XFS: %s", self.mount_point)
        if not self.dryrun:
            check_call(["/bin/sync"])
            check_call(["/usr/sbin/xfs_freeze", "-f", self.mount_point])

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Unfreezing XFS: %s", self.mount_point)
        if not self.dryrun:
            check_call(["/usr/sbin/xfs_freeze", "-u", self.mount_point])

class MongoLocker(object):
    def __init__(self, host="localhost", port=27017, slaveonly=False, dryrun=False):
        import pymongo.connection
        self.connection = pymongo.connection.Connection(host, int(port), slave_okay=True)
        self.dryrun = dryrun
        self.slaveonly = slaveonly
    
    def validate(self):
        if not self.slaveonly:
            return True
        info = self.connection.admin.command("isMaster")
        return not info["ismaster"]
    
    def __enter__(self):
        logging.info("Fsyncing and locking MongoDB")
        if not self.dryrun:
            self.connection.admin.command("fsync", 1, lock=1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Unlocking MongoDB")
        if not self.dryrun:
            self.connection.admin["$cmd"].sys.unlock.find_one()

class MySQLLocker(object):
    def __init__(self, user, password, host="localhost", port=3306, dryrun=False):
        import MySQLdb
        self.connection = MySQLdb.connect(host=host, port=port, user=user, passwd=password)
        self.dryrun = dryrun
    
    def validate(self):
        return True
    
    def __enter__(self):
        logging.info("Flushing and locking MySQL")
        if not self.dryrun:
            c = self.connection.cursor()

            # Don't pass FLUSH TABLES statements on to replication slaves
            # as this can interfere with long-running queries on the slaves.
            c.execute("SET SQL_LOG_BIN=0")

            c.execute("FLUSH LOCAL TABLES")
            c.execute("FLUSH LOCAL TABLES WITH READ LOCK")
            c.execute("SHOW MASTER STATUS")

            c.execute("SET SQL_LOG_BIN=1")

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Unlocking MySQL")
        if not self.dryrun:
            c = self.connection.cursor()
            c.execute("UNLOCK TABLES")

LOCKER_CLASSES = {
    'mongodb': MongoLocker,
    'mysql': MySQLLocker,
}

def backup(mount_point, aws_key, aws_secret_key, lockers=[], dryrun=False):
    devices = [get_device_for_mount(mount_point)]
    if devices[0].startswith("/dev/md"):
        devices = get_devices_for_raid(devices[0])

    instance_id = get_ec2_metadata('instance-id')
    ec2 = EC2Connection(aws_key, aws_secret_key)
    instance = ec2.get_all_instances([instance_id])[0].instances[0]
    
    all_volumes = ec2.get_all_volumes()
    volumes = []
    for v in all_volumes:
        if v.attach_data.instance_id == instance_id:
            if v.attach_data.device in devices:
                volumes.append(v)

    if not volumes:
        sys.stderr.write("No EBS volumes found for devices %s\n" % devices)
        sys.exit(1)

    logging.info("Instance ID: %s", instance_id)
    logging.info("Devices: %s", ", ".join(devices))
    logging.info("Volumes: %s", ", ".join(v.id for v in volumes))

    locker_instances = []
    for l in lockers:
        l = l.split(':')
        cls = LOCKER_CLASSES[l[0]]
        kwargs = {}
        for k, v in (x.split('=') for x in l[1:]):
            if v.lower() == "true":
                v = True
            elif v.lower() == "false":
                v = False
            kwargs[k] = v
        kwargs['dryrun'] = dryrun
        inst = cls(**kwargs)
        locker_instances.append(inst)
        if not inst.validate():
            return

    locker_instances.append(XFSLocker(mount_point, dryrun=dryrun))

    with contextlib.nested(*locker_instances):
        for v in volumes:
            name = v.tags.get('Name')
            logging.info("Snapshoting %s (%s)", v.id, name or 'NONAME')
            if not dryrun:
                snap = v.create_snapshot()
                if name:
                    snap.add_tag('Name', name)

def main():
    parser = build_parser()
    options, args = parser.parse_args()
    if not options.awskeys:
        parser.error("must specify AWS keys")
    if not options.mount_point:
        parser.error("must specify a mount point")

    logging.basicConfig(level=logging.INFO if options.verbose else logging.WARNING)

    aws_key, aws_secret_key = options.awskeys.split(':')
    backup(options.mount_point,
        aws_key = aws_key,
        aws_secret_key = aws_secret_key,
        lockers = options.lockers,
        dryrun = options.dryrun)

if __name__ == "__main__":
    main()
