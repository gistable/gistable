import xmlrpclib


class ProcessStatus(object):
    RUNNING = 'RUNNING'
    STOPPED = 'STOPPED'
    FATAL = 'FATAL'
    RESTARTING = 'RESTARTING'
    SHUTDOWN = 'SHUTDOWN'


class SupervisorClient(object):
    """ Supervisor client to work with remote supervisor
    """

    def __init__(self, host='localhost', port=9001):
        self.server = xmlrpclib.Server('http://{}:{}/RPC2'.format(host, port))

    def _generate_correct_process_name(self, process):
        return "{}:1".format(process)

    def start(self, process):
        """ Start process
        :process: process name as String
        """
        return self.server.supervisor.startProcess(self._generate_correct_process_name(process))

    def stop(self, process):
        """ Stop process
        :process: process name as String
        """
        return self.server.supervisor.stopProcess(self._generate_correct_process_name(process))

    def status(self, process):
        """ Retrieve status process
        :process: process name as String
        """
        return self.server.supervisor.getProcessInfo(self._generate_correct_process_name(process))['statename']
