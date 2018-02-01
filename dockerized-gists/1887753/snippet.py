from subprocess import check_output
import json
import collections


def hiera(key, environment, location, hostname, merge=None, preserve_order=True, bin="/usr/local/bin/hiera", confdir="/etc/puppet/"):
    if preserve_order:
        obj_pair_hook=collections.OrderedDict
    else:
        obj_pair_hook=None

    if merge==list:
        merge_opt='-a'
    elif merge==dict:
        merge_opt='-h'
    else:
        merge_opt=None

    args = [bin, key, 'environment=%s' % environment, 'location=%s' % location, 'hostname=%s' % hostname, 'settings::confdir=%s' % confdir]

    if merge_opt:
	args.append(merge_opt)

    o = check_output(args).rstrip()

    if o == 'nil':
	return None
    else:
        try:
            i = o.replace('=>', ':')
            return json.loads(i, object_pairs_hook=obj_pair_hook)
        except:
            return o