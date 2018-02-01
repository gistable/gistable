class dstat_plugin(dstat):

    def __init__(self):
        self.nick = ('latency',)
        self.type = 'd'
        self.width = 4
        self.scale = 34
        self.diskfilter = re.compile('^(dm-[0-9]+|md[0-9]+|[hs]d[a-z]+[0-9]+)$')
        self.open('/proc/diskstats')
        self.cols = 1

    def discover(self, *objlist):
        ret = []
        for l in self.splitlines():
            if len(l) < 13: continue
            if l[3:] == ['0',] * 11: continue
            name = l[2]
            ret.append(name)
        for item in objlist: ret.append(item)
        if not ret:
            raise Exception, "No suitable block devices found to monitor"
        return ret

    def vars(self):
        ret = []
        if op.disklist:
            varlist = op.disklist
        else:
            varlist = []
            blockdevices = [os.path.basename(filename) for filename in glob.glob('/sys/block/*')]
            for name in self.discover:
                if self.diskfilter.match(name): continue
                if name not in blockdevices: continue
                varlist.append(name)
#           if len(varlist) > 2: varlist = varlist[0:2]
            varlist.sort()
        for name in varlist:
            if name in self.discover:
                ret.append(name)
        return ret

    def name(self):
        return self.vars

    def extract(self):
        for name in self.vars: self.set2[name] = (0, 0, 0, 0, )
        for l in self.splitlines():
            if len(l) < 13: continue
            if l[5] == '0' and l[9] == '0': continue
            name = l[2]
            if l[3:] == ['0',] * 11: continue
            if name in self.vars:
                self.set2[name] = (
                        self.set2[name][0] + long(l[3]),
                        self.set2[name][1] + long(l[6]),
                        self.set2[name][2] + long(l[7]),
                        self.set2[name][3] + long(l[10]),
                )
        for name in self.set2.keys():
            if len(self.set1[name]) == 4:
                read_ios = self.set2[name][0] - self.set1[name][0]
                read_ticks = self.set2[name][1] - self.set1[name][1]
                write_ios = self.set2[name][2] - self.set1[name][2]
                write_ticks = self.set2[name][3] - self.set1[name][3]

                total_ios = read_ios + write_ios
                total_ticks = read_ticks + write_ticks
                if total_ios > 0:
                    self.val[name] = (total_ticks / total_ios, )
                else:
                    self.val[name] = (0, )
            else:
                self.val[name] = (0, )
        if step == op.delay:
            self.set1.update(self.set2)