from ctypes import CDLL, sizeof, memset, c_uint32, create_string_buffer

MAXPATHLEN = 1024
PROC_PIDPATHINFO_MAXSIZE = MAXPATHLEN*4
PROC_ALL_PIDS = 1
libc = CDLL('libc.dylib')

def get_pids():
    number_of_pids = libc.proc_listpids(PROC_ALL_PIDS, 0, None, 0)
    pid_list = (c_uint32 * (number_of_pids * 2))()
    return_code = libc.proc_listpids(PROC_ALL_PIDS, 0, pid_list, sizeof(pid_list))
    return [x for x in pid_list if x]

def get_executables(pid_list):
    results = []
    path_size = PROC_PIDPATHINFO_MAXSIZE
    path_buffer = create_string_buffer('\0'*path_size,path_size)
    for a_pid in pid_list:
        # re-use the buffer
        memset(path_buffer, 0, path_size)
        return_code = libc.proc_pidpath(a_pid, path_buffer, path_size)
        if path_buffer.value:
            # a string was returned
            results.append((a_pid, path_buffer.value))
    return results

get_executables(get_pids())
