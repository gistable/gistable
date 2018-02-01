"""
Convert a MongoDB ObjectID to a version-1 UUID.

Python 2.7+ required for datetime.timedelta.total_seconds().

ObjectID:
    - UNIX timestamp (32 bits)
    - Machine identifier (24 bits)
    - Process ID (16 bits)
    - Counter (24 bits)

UUID 1:
    - Timestamp (60 bits)
    - Clock sequence (14 bits)
    - Node identifier (48 bits)
"""

import datetime
import uuid

from bson import objectid

class _UTC(datetime.tzinfo):
    ZERO = datetime.timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return self.ZERO

UTC = _UTC()
UUID_1_EPOCH = datetime.datetime(1582, 10, 15, tzinfo=UTC)
UUID_TICKS_PER_SECOND = 10000000
UUID_VARIANT_1 = 0b1000000000000000

def _unix_time_to_uuid_time(dt):
    return int((dt - UUID_1_EPOCH).total_seconds() * UUID_TICKS_PER_SECOND)

def objectid_to_uuid(oid):
    oid_time = oid.generation_time.astimezone(UTC)
    oid_hex = str(oid)
    machine_pid_hex = oid_hex[8:18]
    counter = int(oid_hex[18:], 16)

    timestamp_hex = '1%015x' % (_unix_time_to_uuid_time(oid_time))
    clock_hex = '%04x' % (UUID_VARIANT_1 | (counter & 0x3fff))
    node_hex = '%012x' % int(machine_pid_hex, 16)

    converted_uuid = uuid.UUID(
        '%s-%s-%s-%s-%s' % (
            timestamp_hex[-8:],
            timestamp_hex[4:8],
            timestamp_hex[:4],
            clock_hex,
            node_hex
        )
    )

    assert converted_uuid.variant == uuid.RFC_4122
    assert converted_uuid.version == 1

    return converted_uuid

if __name__ == '__main__':
    oid = objectid.ObjectId()
    print oid

    oid_as_uuid = objectid_to_uuid(oid)
    print '{%s}' % oid_as_uuid
