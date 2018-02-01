from pkg_resources import working_set
for x in working_set:
    print("%s: %s" % (x.key, x.version))