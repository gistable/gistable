from tornado import gen
import tornado.testing

import motor


class MyTestCase(tornado.testing.AsyncTestCase):
    def test_thing(self):
        client = motor.MotorClient('localhost', 27017, io_loop=self.io_loop)
        client.open_sync()

        @gen.engine
        def f(callback):
            collection = client.test.test_collection
            yield motor.Op(collection.remove)
            yield motor.Op(collection.insert, {'_id': 1, 'x': 17})
            doc = yield motor.Op(collection.find_one, {'_id': 1})
            self.assertEqual(17, doc['x'])
            callback()

        f(callback=self.stop)
        self.wait()


if __name__ == '__main__':
    import unittest
    unittest.main()
