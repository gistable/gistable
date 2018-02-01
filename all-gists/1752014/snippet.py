#coding:utf-8
import psutil
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

TIME_NUM = 90
FRAMES = 360

class processMoniter:
    def  __init__(self, pids):
        self.cpu_nums = psutil.NUM_CPUS
        self.max_mem = psutil.TOTAL_PHYMEM

        self.plist = [psutil.Process(pid) for pid in pids]

        self.get_system_info()
        self.get_processes_info()

    def get_system_info(self):
        cpu_percent = psutil.cpu_percent(interval=0.0, percpu=False)
        mem_percent = float(psutil.used_phymem()) / self.max_mem * 100
        return cpu_percent, mem_percent

    def get_process_info(self, p):
        if p.is_running:
            cpu_percent = p.get_cpu_percent(interval=0.0) / self.cpu_nums
            mem_percent = p.get_memory_percent()
        else:
            cpu_percent = 0.0
            mem_percent = 0.0
        return cpu_percent, mem_percent

    def get_processes_info(self):
        infodic = {}
        for p in self.plist:
            infodic[(p.pid, p.name)] = self.get_process_info(p)
        return infodic

class processUsage:
    def __init__ (self, maxnum):
        self.maxnum = maxnum
        self.cpu_usage = []
        self.mem_usage = []
        self.times = []

    def update(self, num, cpu, mem):
        self.cpu_usage.append(cpu)
        self.mem_usage.append(mem)

        if len(self.cpu_usage) > self.maxnum:
            self.cpu_usage = self.cpu_usage[1:]
            self.mem_usage = self.mem_usage[1:]
        else:
            self.times.append(num)

class processGraph:
    def __init__(self, pids):
        self.taskmgr = processMoniter(pids)

    def __setdata(self, usage, line):
            line.set_xdata(usage.mem_usage)
            line.set_ydata(usage.times)
            line.set_3d_properties(usage.cpu_usage)

    def update_lines(self, num, sysline, sysUsage, plines, pUsages, ax) :
        # System
        sCpu, sMem = self.taskmgr.get_system_info()
        sysUsage.update(num, sCpu, sMem)
        self.__setdata(sysUsage, sysline)

        # Processes
        pInfos = self.taskmgr.get_processes_info()
        for (pid, name), (cpu, mem) in pInfos.iteritems():
            pUsage = pUsages[pid]
            pUsage.update(num, cpu, mem)
            pLine = plines[pid]
            self.__setdata(pUsage, pLine)

        ax.set_xlim3d(0, 100)
        ax.set_ylim3d(0, TIME_NUM)
        ax.set_zlim3d(0, 100)

        ax.view_init(30, 1 * num)
        return sysline

    def show(self):
        fig = plt.figure()

        # init axis
        ax = fig.gca(projection='3d')
        ax.view_init(30, 0)

        ax.set_xlabel('Memory Usage (%)')
        ax.set_ylabel('Time')
        ax.set_zlabel('CPU Usage (%)')

        # System
        sysUsage = processUsage(TIME_NUM)
        sysline, = ax.plot(sysUsage.mem_usage, sysUsage.times,
                    zs=np.array(sysUsage.cpu_usage), zdir='z', label='zs=0, zdir=z')
        sysline.set_label('System')

        # Processes
        pUsages = {}
        pLines = {}
        info_dic = self.taskmgr.get_processes_info()
        for (pid, name), (cpu, mem) in info_dic.iteritems():
            pUsage = processUsage(TIME_NUM)
            pline, = ax.plot(pUsage.mem_usage, pUsage.times, zs=np.array(pUsage.cpu_usage),
                     zdir='z', label='zs=0, zdir=z')
            pline.set_label('{0}({1})'.format(name, pid))
            pLines[pid] = pline
            pUsages[pid] = pUsage

        ax.legend()

        # Creating the Animation object
        line_ani = animation.FuncAnimation(fig, self.update_lines, FRAMES,
                                        fargs=(sysline, sysUsage, pLines, pUsages, ax),
                                        interval=100, blit=False)
        plt.show()
        #line_ani.save('im.mp4')


# usage
pid1 = 6876
pid2 = 6804
graph = processGraph([pid1, pid2])
graph.show()
