import boto
import logging
import os
import time
import subprocess
import sys
import urllib2

logger = logging.getLogger("pgbackup")
logger.addHandler(level=logging.INFO, logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_LOCAL0))

def who_am_i():
    """Return one's instance id"""
    return urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id', timeout=1).read().strip()

def list_ebs(conn, blacklist=["/dev/sda1"]):
    """Get all ebs volumes for oneself
    
    @return [(device, ebs-id), ...]
    """
    r = conn.get_all_instances([who_am_i()])[0]
    assert len(r.instances) == 1, r.instances
    i = r.instances[0]
    return [(device, volume) for device, volume in i.block_device_mapping.items() if device not in blacklist]

def snap_ebs(device, volume, conn):
    return conn.create_snapshot(volume.volume_id, device)

def freeze(mnt):
    logger.info("Calling xfs_freeze -f")
    return subprocess.call(["sudo", "xfs_freeze", "-f", mnt]) == 0

def thaw(mnt):
    logger.info("Calling xfs_freeze -u")
    return subprocess.call(["sudo", "xfs_freeze", "-u", mnt]) == 0

def main():
    assert os.path.isdir(sys.argv[1]), "Usage: pgsnap.py xfs_mount_point"
    conn = boto.connect_ec2(os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_KEY_ID"])
    vols = list_ebs(conn)
    frozen = False
    start = time.time()
    try:
        frozen = freeze(sys.argv[1])
        assert frozen, "xfs_freeze failed"
        snaps = [snap_ebs(device, volume, conn) for device, volume in vols]
        logger.info("Snapshots: {0}".format(snaps))
    finally:
        if frozen:
            thaw(sys.argv[1])
            logger.info("XFS was frozen for {0}".format(time.time() - start))

if __name__ == '__main__':
    main()