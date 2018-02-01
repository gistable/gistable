import pkg_resources, pprint

requires = {p.key: [r.key for r in p.requires()] for p in pkg_resources.working_set}

def graph(pkg):
    if not requires[pkg]:
        return {pkg: {}}

    return {pkg: {k: v for p in requires[pkg] for k, v in graph(p).items() }}

pprint.pprint({k: v for r in requires for k, v in graph(r).items()})
