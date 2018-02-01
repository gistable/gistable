# 实际执行任务的进程是 multiprocessing.Process 启动的，主进程会等待子进程结束并检查 exitcode 0.
# 另外如果多次任务执行失败会重启操作系统。

# 实际用法：
# with TaskHeartbeat(host_id, secret_key, task['id'], task['timeout']):
#     实际任务

class TaskHeartbeat(threading.Thread):

    def __init__(self, host_id, secret_key, task_id, timeout):
        super(TaskHeartbeat, self).__init__()
        self.setDaemon(True)

        self.is_exit = False
        self.host_id = host_id
        self.secret_key = secret_key
        self.task_id = task_id
        self.timeout = timeout

    def run(self):
        start_time = arrow.utcnow()
        timeout_time = start_time.replace(seconds=+self.timeout)

        while not self.is_exit:
            if arrow.utcnow() > timeout_time:
		# TODO: 上报执行超时
                kill_child_processes(os.getpid())
                os._exit(123)
                return

	    # TODO: 上报心跳
            time.sleep(30)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 继续传播异常，外部会捕获并上报任务失败
        self.is_exit = True
        return False