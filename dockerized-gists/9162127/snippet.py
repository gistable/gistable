#! env python

from boto import ec2

conn = ec2.connect_to_region('us-west-2')

vols = conn.get_all_volumes(filters={'status': 'available'})
for vol in vols:
    print 'checking vol:', vol.id, 'status:', vol.status, 'attachment_id:', vol.attach_data.status
    conn.delete_volume(vol.id)