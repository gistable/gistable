#!/usr/bin/env python


def host_groups_to_knife(hosts_config, output_file="knife_commands.sh"):
  """Converts Nagios hosts config to knife role from file commands."""
  file = open(hosts_config, 'r')

  output = "#!/bin/bash\n"

  for line in file:
    # all data is collected if we get a }
    if line[0] == "}":
      # print the knife commands
      output += 'echo "updating %s";\n' % host_name
      for group in groups:
        output += 'knife node run list add %s "role[%s]";\n' % (address, group)
      output += "\n"
    # gather the data
    elif "address" in line:
      address = line.strip().split()[1]
    elif "host_name" in line:
      host_name = line.strip().split()[1]
    elif "hostgroups" in line:
      groups = line.strip().split()[1].split(',')
    
  # write the commands to file
  out = open(output_file, 'w')
  out.write(output)
  out.close()

if __name__ == "__main__":
  import sys
  if len(sys.argv) == 2:
    host_groups_to_knife(sys.argv[1])
  elif len(sys.argv) == 3:
    host_groups_to_knife(sys.argv[1], output_file=sys.argv[2])
  else:
    print "Wrong number of arguments.\n"
    print "Usage: python host_groups_to_knife.py infile outfile"
