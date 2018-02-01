#!/usr/bin/env python

import re
import os
import sys
import threading
import subprocess
import getopt
import time

def usage(is_help = False):
    """
    Function to show usage information
    
    Args:
        is_help: Whether to show the full help or just the command to show help
        
    Returns:
        True
    """
    
    if is_help == False:
        sys.stdout.write('Run \'%s --help\' for more information\n' % sys.argv[0])
        return True
        
    usage_info = 'Usage: %s [options]\nOptions:\n' % sys.argv[0]
    usage_info += ' -p,  --proc-interval <arg>      Sampling interval for /proc/stat; default to 1 second\n'
    usage_info += ' -t,  --top-interval <arg>       Sampling interval for top; default to 3 seconds or the value configured in .toprc\n'
    usage_info += ' -s,  --show-process             Whether to show process details in top\'s output; OFF by default\n'
    usage_info += ' -h,  --help                     Display this information\n'
    sys.stdout.write(usage_info)
    return True

def read_interval(value):
    """
    Function to read interval for top or /proc/stat.
    Raises an exception if the interval is not an integer or < 1
    
    Args:
        value: the string that contain the integer interval
        
    Returns:
        interval parsed from value
    """
    
    try:
        value = int(value)
    except Exception:
        value = -1
        
    if value < 1:
        raise Exception('Invalid interval specified')
    
    return value
           
class CPUSimulator(threading.Thread):
    """
    Class that simulates CPU utilization using multiple threads.
    Constructor starts the thread immediately, but the actual operation waits for the start event to be set.
    The idea is not to waste time in spawing threads and start executing ASAP.
    """
    
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.start()
    
    def run(*args):
        CPUSimulator.start_event.wait()
        
        while not CPUSimulator.stop_event.wait(0.2):
            i = 0 

            while i < 5000000 and not CPUSimulator.stop_event.is_set():
                i += 1
        
    def run_threads(threads, interval):
        CPUSimulator.start_event.set()
        time.sleep(interval)
        CPUSimulator.stop_event.set()
        
        for thread in threads:
            thread.join()
            
    run_threads = staticmethod(run_threads)
    start_event, stop_event = threading.Event(), threading.Event()
           
class Process(object):
    """
    Class to wrap subprocess execution.
    Constructor starts the process immediately, but the actual operation waits for the key press.
    The idea is not to waste time in spawing process and start executing ASAP.
    """
    
    def __init__(self, command):
        args = ['bash', '-c', 'read ; %s' % command]
        self.command = command
        self.process = subprocess.Popen(args, bufsize = 1, universal_newlines = True,
            stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)    
                    
    def start(self):
        self.process.stdin.write('\n')
        return self
        
    def print_output(self, padding = '', is_print_command = True):
        self.process.wait();
        output_lines = list(self.process.stdout.readlines())
        is_print_command and sys.stdout.write('\n%s\n' % self.command)
        
        for line in output_lines:
            sys.stdout.write('%s%s' % (padding * 2, line))
        
        return output_lines
    
class ProcProcess(Process):
    """
    Subclass for post processing /proc/stat output
    """
    
    def print_output(self, padding = '', is_show_process = False, min_interval = 1):
        output = Process.print_output(self, padding = padding)
        skip_lines = is_show_process and 2 or 1
        first_sample, second_sample = output[0].split(), output[skip_lines].split()
        result = [int(second_sample[j]) - int(first_sample[j]) for j in range(1, len(second_sample))]
        keys, cpu_total, utilization, cpu = ['us', 'ni', 'sy', 'id', 'wa', 'hi', 'si', 'st'], sum(result), '', first_sample[0]
        sys.stdout.write('%sDifference\n%s%s  = %d\n' % (padding, padding * 2, cpu + '  ' + ' '.join([str(res) for res in result]), cpu_total))

        for i in range(0, min(len(keys), len(first_sample) - 1)):
            utilization += i and ', ' or ''
            utilization += '%0.2f%% %s' % (float(result[i]) / cpu_total * 100, keys[i])
            
        if is_show_process:
            first_sample, second_sample = output[1].split(), output[1 + skip_lines].split()
            result = [int(second_sample[j]) - int(first_sample[j]) for j in range(1, len(second_sample))]
            total, process = sum(result), first_sample[0]
            sys.stdout.write('%s%s  = %d\n' % (padding * 2, process + '  ' + ' '.join([str(res) for res in result]), total))
            utilization += '\n%s%s  %.2f%%' % (padding * 2, process, total > cpu_total and 100 or float(total) / min_interval)

        sys.stdout.write('%sUtilization\n%s%s  %s\n' % (padding, padding * 2, cpu, utilization))
        return output

def run(*args):
    """
    The main function to execute the script.
    
    Args:
        args: arguments to be parsed 
    """
    
    if float('%d.%d' % (sys.version_info[0], sys.version_info[1])) < 2.7:
        sys.stderr.write('Requires python version 2.7 or above\n')
        sys.exit(1)
    
    proc_interval, top_interval, show_process, threads = 1, None, False, []
    command = 'for c in grep awk ; do [[ "$(type -P $c)" == "" ]] && echo "Could not find \'$c\' command" >&2 && exit 1 ; done'
    
    if Process(command).start().print_output(is_print_command = False):
        sys.exit(1)

    try:
        options = ('p:t:sh', ['proc-interval=', 'top-interval=', 'show-process', 'help'])

        for option, arg in getopt.getopt(args, options[0], options[1])[0]:
            if option in ['-p', '--proc-interval']:
                proc_interval = read_interval(arg)
            elif option in ['-t', '--top-interval']:
                top_interval = read_interval(arg)
            elif option in ['-s', '--show-process']:
                show_process = True
            elif option in ['-h', '--help']:
                usage(True) and sys.exit(0)
    except getopt.GetoptError:
        e = sys.exc_info()[1]
        sys.stderr.write(str(e).capitalize() + '\n')
        usage() and sys.exit(1)
    except Exception:
        e = sys.exc_info()[1]
        sys.stderr.write(str(e).capitalize() + '\n')
        sys.exit(1)
        
    with open('/proc/cpuinfo') as f:
        for line in f.readlines():
            if re.match('processor\s*:\s*[0-9]+\s*', line):
                threads.append(CPUSimulator())
                
    proc_command = 'grep -Ei "cpu\\s+" </proc/stat'
    top_command = 'top -b -n2 %s | awk "/^top/{i++}i==2"'
    new_line, top_command_args = '\n', ''
    
    if top_interval:
        top_command_args = '-d %d ' % top_interval
    else:
        top_interval = proc_interval
    
    if show_process:
        proc_command += ' ; awk "{print \\$2, \\$14, \\$15, \\$16, \\$17}" </proc/%d/stat ' % os.getpid()
        top_command_args += '-p %d' % os.getpid()
    else:
        new_line = ' ; '
        top_command += ' | grep -Ei "cpu\\(s\\)\\s*:"'
    
    proc_command = '%s%ssleep %d%s%s' % (proc_command, new_line, proc_interval, new_line, proc_command)
    proc_process = ProcProcess(proc_command)
    top_command = top_command % top_command_args
    top_process = Process(top_command)
    padding, start_time, min_interval = '  ', time.time(), min(proc_interval, top_interval)
    
    #at this point we have top and /proc/stat waiting to be executed in a bash process
    #also the threads to simulate CPU usage are started and waiting for event to be signaled
    #all we need to do is to start them and then measure the usage
    proc_process.start() and top_process.start()
    sys.stdout.write('Simulating CPU utilization using %d threads...\n' % len(threads))
    CPUSimulator.run_threads(threads, min_interval)
    sys.stdout.write('Simulation completed in %.3f seconds\n' % (time.time() - start_time))

    if top_interval < proc_interval:
        top_process.print_output(padding)
        proc_process.print_output(padding, show_process, min_interval = min_interval)
    else:
        proc_process.print_output(padding, show_process, min_interval = min_interval)
        top_process.print_output(padding)
    
    sys.stdout.write('\nTook %.3f seconds\n' % (time.time() - start_time))

if __name__ == '__main__':
    run(*sys.argv[1:])
