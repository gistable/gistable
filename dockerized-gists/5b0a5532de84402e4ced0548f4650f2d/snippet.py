import os
import pwd
import psutil
import re
import string
import requests
import socket
import argparse
import tabulate
import pandas as pd

UID = 1

regex = re.compile(r'.+kernel-(.+)\.json')
port_regex = re.compile(r'port=(\d+)')

def get_proc_info():
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

    # memory info from psutil.Process
    df_mem = []
    # running ports
    ports = []
    default_port = 8888

    for pid in pids:
        try:
            ret = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
        except IOError:  # proc has already terminated
            continue

        # jupyter notebook processes
        if len(ret) > 0 and ('jupyter-notebook' in ret or 'ipython notebook' in ret):
            port_match = re.search(port_regex, ret)
            if port_match:
                port = port_match.group(1)
                ports.append(int(port))
            else:
                ports.append(default_port)
                default_port += 1
        if len(ret) > 0 and ('jupyter' in ret or 'ipython' in ret) and 'kernel' in ret:
            # kernel
            kernel_ID = re.sub(regex, r'\1', ret)
            kernel_ID = filter(lambda x: x in string.printable, kernel_ID)

            # memory
            process = psutil.Process(int(pid))
            mem = process.memory_info()[0] / float(1e9)

            # user name for pid
            for ln in open('/proc/{0}/status'.format(int(pid))):
                if ln.startswith('Uid:'):
                    uid = int(ln.split()[UID])
                    uname = pwd.getpwuid(uid).pw_name

            # user, pid, memory, kernel_ID
            df_mem.append([uname, pid, mem, kernel_ID])

    df_mem = pd.DataFrame(df_mem)
    df_mem.columns = ['user', 'pid', 'memory_GB', 'kernel_ID']
    return df_mem, ports

def get_session_info(ports, opts):
    # notebook info from assessing ports
    if opts.get('hostname'):
        hostnames = [opts['hostname']]
    else:
        hostnames = [socket.gethostname(), '127.0.0.1', 'localhost', '0.0.0.0']
    df_nb = []
    kernels = []

    for port in set(ports):
        for hostname in set(hostnames):
            sessions = None
            try:
                base_url = 'http://{0}:{1}/'.format(hostname, port)
                s = requests.Session()
                if opts.get('password'):
                    # Seems jupyter auth process has changed, need to first get a cookie,
                    # then add that cookie to the data being sent over with the password
                    data = {
                        'password': opts['password']
                    }
                    s.post(base_url + 'login', data=data)
                    data.update(s.cookies)
                    s.post(base_url + 'login', data=data)

                sessions = s.get(base_url + 'api/sessions').json()
            except:
                sessions = None

            if sessions:
                for sess in sessions:
                    kernel_ID = sess['kernel']['id']
                    if kernel_ID not in kernels:
                        notebook_path = sess['notebook']['path']
                        df_nb.append([port, kernel_ID, notebook_path])
                        kernels.append(kernel_ID)

    df_nb = pd.DataFrame(df_nb)
    df_nb.columns = ['port', 'kernel_ID', 'notebook_path']
    return df_nb

def parse_args():
    parser = argparse.ArgumentParser(description='Find memory usage.')
    parser.add_argument('--hostname', help='hostname (default: try to find it)')
    parser.add_argument('--password', help='password (only needed if pass-protected)')

    return parser.parse_args()

def main(opts):
    df_mem, ports = get_proc_info()
    df_nb = get_session_info(ports, opts)

    # joining tables
    df = pd.merge(df_nb, df_mem, on=['kernel_ID'], how='inner')
    df = df.sort_values('memory_GB', ascending=False).reset_index(drop=True)

    print tabulate.tabulate(df, headers=(df.columns.tolist()))
    return df

if __name__ == '__main__':
    args = vars(parse_args())
    main(args)
