reservations = ec2.get_all_instances(filters={"tag:Purpose": "Web"})
for res in reservations:
  for inst in res.instances:
    if inst.private_ip_address:
      if inst.state == 'running':
          print inst.private_ip_address