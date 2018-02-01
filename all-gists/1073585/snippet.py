def proc_starttime(pid):
    p = re.compile(r"^btime (\d+)$", re.MULTILINE)
    m = p.search(open("/proc/stat").read())
    btime = int(m.groups()[0])
    clk_tck = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    stime = int(open("/proc/%d/stat" % pid).read().split()[21]) / clk_tck
    return btime + stime