import unittest
import mock
import subprocess

class PythonSubprocessTest(unittest.TestCase):

    class MockPopen(object):
        def __init__(self):
            pass
        def communicate(self, input=None):
            pass
        @property
        def returncode(self):
            pass

    def test_process_with_mock_subprocess(self):
        mock_popen = PythonSubprocessTest.MockPopen()
        mock_popen.communicate = mock.Mock(return_value=('hello mock subprocess stdout', 'hello mock subprocess stderr'))
        mock_returncode = mock.PropertyMock(return_value=1)
        type(mock_popen).returncode = mock_returncode
        '''
        set attribute Popen return mock_popen when create Popen object
        '''
        setattr(subprocess, 'Popen', lambda *args, **kargs: mock_popen)

        expected_object = Process()
        self.assertEqual(expected_object.call_process(), ('hello mock subprocess stdout', 'hello mock subprocess stderr', 1))

        '''
        expected communicate must be call once time!!!
        '''
        mock_popen.communicate.assert_called_once_with()
        mock_returncode.assert_called_once_with()

class Process(object):

    def __init__(self):
        pass

    def call_process(self):
        p = subprocess.Popen(['ls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        exitcode = p.returncode

        return stdout, stderr, exitcode
