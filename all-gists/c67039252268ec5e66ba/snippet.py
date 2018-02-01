#!/usr/bin/python
#
# chaintest   Summarize off-CPU time by kernel stack + 2 waker stacks
#             WORK IN PROGRESS. For Linux, uses BCC, eBPF.
#
# USAGE: chaintest [-h] [-u] [-p PID] [-i INTERVAL] [-T] [duration]
#
# PLEASE DO NOT RUN THIS IN PRODUCTION! This is a work in progress, intended to
# explore chain graphs on Linux, using eBPF capabilities from a particular
# kernel version (4.3ish). This tool will eventually get much better.
#
# The current implementation uses an unrolled loop for x86_64, and was written
# as a proof of concept. This implementation should be replaced in the future
# with an appropriate bpf_ call, when available.
#
# Off-cpu stack currently limited to a stack trace depth of 18 (maxtdepth),
# and waker stacks limited to 7. This is working around BPF_STACK_MAX (512).
#
# Copyright 2016 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 25-Jan-2016   Brendan Gregg   Created this.

from __future__ import print_function
from bcc import BPF
from time import sleep
import argparse
import signal

# arguments
examples = """examples:
    ./chaintest             # trace off-CPU + waker stack time until Ctrl-C
    ./chaintest 5           # trace for 5 seconds only
    ./chaintest -f 5        # 5 seconds, and output in folded format
    ./chaintest -u          # don't include kernel threads (user only)
    ./chaintest -p 185      # trace fo PID 185 only
"""
parser = argparse.ArgumentParser(
    description="Summarize off-CPU time by kernel stack + 2 waker stacks",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-u", "--useronly", action="store_true",
    help="user threads only (no kernel threads)")
parser.add_argument("-p", "--pid",
    help="trace this PID only")
parser.add_argument("-v", "--verbose", action="store_true",
    help="show raw addresses")
parser.add_argument("-f", "--folded", action="store_true",
    help="output folded format")
parser.add_argument("duration", nargs="?", default=99999999,
    help="duration of trace, in seconds")
args = parser.parse_args()
folded = args.folded
duration = int(args.duration)
debug = 0
maxwdepth = 7     # and MAXWDEPTH
maxtdepth = 18    # and MAXTDEPTH
if args.pid and args.useronly:
    print("ERROR: use either -p or -u.")
    exit()

# signal handler
def signal_ignore(signal, frame):
    print()

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

// carefully work around MAX_BPF_STACK limit of 512:
#define MAXWDEPTH	7
#define MAXTDEPTH	18

#define MINBLOCK_US	1

struct key_t {
    char waker0[TASK_COMM_LEN];
    char waker1[TASK_COMM_LEN];
    char target[TASK_COMM_LEN];
    u64 wret0[MAXWDEPTH];
    u64 wret1[MAXWDEPTH];
    u64 tret[MAXTDEPTH];
};
BPF_HASH(counts, struct key_t);
BPF_HASH(start, u32);
struct wokeby_t {
    char name0[TASK_COMM_LEN];
    char name1[TASK_COMM_LEN];
    u64 ret0[MAXWDEPTH];
    u64 ret1[MAXWDEPTH];
};
BPF_HASH(wokeby, u32, struct wokeby_t);

static u64 get_frame(u64 *bp) {
    if (*bp) {
        // The following stack walker is x86_64 specific
        u64 ret = 0;
        if (bpf_probe_read(&ret, sizeof(ret), (void *)(*bp+8)))
            return 0;
        if (bpf_probe_read(bp, sizeof(*bp), (void *)*bp))
            *bp = 0;
        if (ret < __START_KERNEL_map)
            return 0;
        return ret;
    }
    return 0;
}

int waker(struct pt_regs *ctx, struct task_struct *p) {
    u32 mypid, pid = p->pid;

    if (!(FILTER))
        return 0;

    u64 bp = 0;
    struct wokeby_t woke = {}, *mywokep;
    bpf_get_current_comm(&woke.name0, sizeof(woke.name0));
    bp = ctx->bp;

    // unrolled loop (MAXWDEPTH):
    int depth = 0;    // clang nukes depth
    if (!(woke.ret0[depth++] = get_frame(&bp))) goto out;
    if (!(woke.ret0[depth++] = get_frame(&bp))) goto out;
    if (!(woke.ret0[depth++] = get_frame(&bp))) goto out;
    if (!(woke.ret0[depth++] = get_frame(&bp))) goto out;
    if (!(woke.ret0[depth++] = get_frame(&bp))) goto out;
    if (!(woke.ret0[depth++] = get_frame(&bp))) goto out;
    woke.ret0[depth++] = get_frame(&bp);

out:
    mypid = bpf_get_current_pid_tgid();
    mywokep = wokeby.lookup(&mypid);
    if (mywokep) {
        // copy waker stack and process name:
        __builtin_memcpy(&woke.ret1, mywokep->ret0, sizeof(woke.ret1));
        __builtin_memcpy(&woke.name1, mywokep->name0, TASK_COMM_LEN);

        // XXX: can't delete yet
        // wokeby.delete(&pid);
    }

    wokeby.update(&pid, &woke);
    return 0;
}

int oncpu(struct pt_regs *ctx, struct task_struct *p) {
    u32 pid;
    u64 ts, *tsp;

    // record previous thread sleep time
    if (FILTER) {
        pid = p->pid;
        ts = bpf_ktime_get_ns();
        start.update(&pid, &ts);
    }

    // calculate current thread's delta time
    pid = bpf_get_current_pid_tgid();
    tsp = start.lookup(&pid);
    if (tsp == 0)
        return 0;        // missed start or filtered
    u64 delta = bpf_ktime_get_ns() - *tsp;
    start.delete(&pid);
    delta = delta / 1000;
    if (delta < MINBLOCK_US)
        return 0;

    // create map key
    u64 zero = 0, *val, bp = 0;
    struct key_t key = {};
    struct wokeby_t *woke;
    bpf_get_current_comm(&key.target, sizeof(key.target));
    bp = ctx->bp;

    // unrolled loop (MAXTDEPTH):
    int depth = 0;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out; // X

    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    if (!(key.tret[depth++] = get_frame(&bp))) goto out;
    key.tret[depth++] = get_frame(&bp);

out:
    woke = wokeby.lookup(&pid);
    if (woke) {
        // copy 1st waker stack and process name:
        __builtin_memcpy(&key.wret0, woke->ret0, sizeof(key.wret0));
        __builtin_memcpy(&key.waker0, woke->name0, TASK_COMM_LEN);

        // copy 2nd waker stack and process name:
        __builtin_memcpy(&key.wret1, woke->ret1, sizeof(key.wret1));
        __builtin_memcpy(&key.waker1, woke->name1, TASK_COMM_LEN);

        // XXX: can't delete yet        wokeby.delete(&pid);
    }

    val = counts.lookup_or_init(&key, &zero);
    (*val) += delta;
    return 0;
}
"""
if args.pid:
    filter = 'pid == %s' % args.pid
elif args.useronly:
    filter = '!(p->flags & PF_KTHREAD)'
else:
    filter = '1'
bpf_text = bpf_text.replace('FILTER', filter)
if debug:
    print(bpf_text)

# initialize BPF
b = BPF(text=bpf_text)
b.attach_kprobe(event="finish_task_switch", fn_name="oncpu")
b.attach_kprobe(event="try_to_wake_up", fn_name="waker")
matched = b.num_open_kprobes()
if matched == 0:
    print("0 functions traced. Exiting.")
    exit()

# header
if not folded:
    print("Tracing off-CPU time (us) by kernel stack", end="")
    if duration < 99999999:
        print(" for %d secs." % duration)
    else:
        print("... Hit Ctrl-C to end.")

# output
while (1):
    try:
        sleep(duration)
    except KeyboardInterrupt:
        # as cleanup can take many seconds, trap Ctrl-C:
        signal.signal(signal.SIGINT, signal_ignore)

    if not folded:
        print()
    counts = b.get_table("counts")
    for k, v in sorted(counts.items(), key=lambda counts: counts[1].value):
        if folded:
            # fold target stack
            line = k.target + ";"
            for i in reversed(range(0, maxtdepth)):
                if k.tret[i] == 0:
                    continue
                line = line + b.ksym(k.tret[i])
                if i != 0:
                    line = line + ";"

            # add delimiter
            line = line + ";-"

            # fold waker stack
            for i in range(0, maxwdepth):
                line = line + ";"
                if k.wret0[i] == 0:
                    break;
                line = line + b.ksym(k.wret0[i])
            if i != 0:
                line = line + ";" + k.waker0

            # add delimiter
            line = line + ";-"

            # fold waker stack
            for i in range(0, maxwdepth):
                line = line + ";"
                if k.wret1[i] == 0:
                    break;
                line = line + b.ksym(k.wret1[i])
            if i != 0:
                line = line + ";" + k.waker1

            # print as a line
            print("%s %d" % (line, v.value))
        else:
            # print wakeup name then stack in reverse order
            print("    %-16s %s" % ("waker1:", k.waker1))
            for i in reversed(range(0, maxwdepth)):
                if k.wret1[i] == 0:
                    continue;
                print("    %-16x %s" % (k.wret1[i],
                    b.ksym(k.wret1[i])))

            # print delimiter
            print("    %-16s %s" % ("-", "-"))

            # print wakeup name then stack in reverse order
            print("    %-16s %s" % ("waker0:", k.waker0))
            for i in reversed(range(0, maxwdepth)):
                if k.wret0[i] == 0:
                    continue;
                print("    %-16x %s" % (k.wret0[i],
                    b.ksym(k.wret0[i])))

            # print delimiter
            print("    %-16s %s" % ("-", "-"))

            # print default multi-line stack output
            for i in range(0, maxtdepth):
                if k.tret[i] == 0:
                    break
                print("    %-16x %s" % (k.tret[i],
                    b.ksym(k.tret[i])))
            print("    %-16s %s" % ("target:", k.target))
            print("        %d\n" % v.value)
    counts.clear()

    if not folded:
        print("Detaching...")
    exit()