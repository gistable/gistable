# encoding: utf-8
from __future__ import print_function
import docker
import unittest
from fabric.api import env, run, execute


class DockerTest(unittest.TestCase):
    def setUp(self):
        self.client = docker.Client(**self.get_client_spec())
        specs = self.get_containers_spec()
        self.containers = []
        boot2docker = self.boot2docker()
        for spec in specs:
            cont = self.client.create_container(**spec['create'])['Id']
            self.client.start(cont, **spec['run'])
            self.containers.append(cont)
            if boot2docker:
                env.hosts.append('127.0.0.1:%s' % spec['run']['port_bindings'][22])
            else:
                env.hosts.append(self.client.inspect_container(cont)['NetworkSettings']['IPAddress'])

    def get_containers_spec(self):
        """
        element in format {'create': {}, 'run': {}}
        """
        return []

    def get_client_spec(self):
        return {}

    def boot2docker(self):
        """
        in case of boot2docker, to successfully ssh to container
        we need to map container port to host port
        :return: bool
        """
        return False

    def tearDown(self):
        for cont in self.containers:
            self.client.stop(cont)
            self.client.remove_container(cont)



class MyTestCase(DockerTest):
    def setUp(self):
        super(MyTestCase, self).setUp()
        env.user = 'root'
        env.password = '123456'

    def get_client_spec(self):
        return {'base_url': 'tcp://192.168.59.103:2375'}

    def get_containers_spec(self):
        self.image = self.get_image_name()
        create_params = {'image': self.image, 'detach': True}
        return [
            {'create': create_params,
             'run': {'port_bindings': {22: x}}} for x in xrange(49000, 49004)
        ]

    def boot2docker(self):
        return True

    def get_image_name(self):
        return 'ncclight'

    def test_x(self):
        print(env.hosts)
        print(self.containers)
        def echo():
            return run("echo test")
        execute(echo)


if __name__ == '__main__':
    unittest.main()