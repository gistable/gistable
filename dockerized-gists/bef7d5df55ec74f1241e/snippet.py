def num_cpu_cores():
    with open('/proc/cpuinfo') as f:
        return f.read().count('processor')