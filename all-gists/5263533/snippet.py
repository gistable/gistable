#!/usr/bin/env python
import sys
import yaml
import json

def convert(infile):
    x = yaml.load(open(infile, 'r').read())

    print "Converting"
    print x
    for container in x['SURVIVAL']:
        print "Entering " + container
        x['SURVIVAL'][container] = json.loads(x['SURVIVAL'][container])

        if container in ('potion', 'stats', 'bedSpawnLocation'):
            continue # nothing to do here.

        for item in x['SURVIVAL'][container]:
            # Do some magic here..
            print " Found a %s at pos %s" %(x['SURVIVAL'][container][item]['is']['type'], item)

            val = x['SURVIVAL'][container][item]

            if val.has_key('is'):
                print '  - Fixing "is" -> "==":"org.bukkit.inventory.ItemStack"'
                t = val['is']
                t['=='] = "org.bukkit.inventory.ItemStack"
                del val['is']
                val = t

            if val.has_key('meta'):
                print '  - Fixing meta with "==": "ItemMeta",'
                val['meta']['=='] = 'ItemMeta'

            x['SURVIVAL'][container][item] = val

    print "Returning as serialised json"
    return json.dumps(x)

### main loop
if __name__ == '__main__':
    for x in sys.argv[1:]:
        print "Converting %s" % x
        outfile = x.replace('.yml', '.json')

        out = convert(x)
        of = open(outfile, 'w')
        of.write(out)
        of.close()
