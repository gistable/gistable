def parse_cpu_info():
    cpu = {}
    for line in open("/proc/cpuinfo"):
        if ':' in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            cpu[k] = v

        if not line.strip():
            yield cpu
            cpu = {}

def cpu_report():
    cpus = list(parse_cpu_info())
    print "processor  physical id   core id unique"
    seen=set()
    for cpu in cpus:
        tup = (cpu['physical id'], cpu['core id'])
        cpu['unique'] = tup not in seen
        seen.add(tup)
        print "%(processor)9s  %(physical id)11s    %(core id)6s %(unique)s" % cpu

if __name__ == "__main__":
    cpu_report()