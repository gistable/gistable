#!/usr/bin/env python

from cm_api.api_client import ApiResource

def main(args):
    cm_host = get(args, 1, "localhost")
    cm_user = get(args, 2, "admin")
    cm_pass = get(args, 3, "admin")

    api = ApiResource(cm_host, username=cm_user, password=cm_pass)
    dump(api)

def dump(api):
    clusters = api.get_all_clusters()
    for c in clusters:
        print "CLUSTER", c.name
        for s in c.get_all_services():
            print "  SERVICE", s
            for rg in s.get_all_role_config_groups():
                print "    RG", rg, rg.get_config()
            for r in s.get_all_roles(view="full"):
                print "    RO", r
                print "      ", r.roleConfigGroupRef
                print "      ", r.hostRef

def get(l, i, default):
    try:
        return l[i]
    except IndexError:
        return default

if __name__ == '__main__':
    import sys
    main(sys.argv)
