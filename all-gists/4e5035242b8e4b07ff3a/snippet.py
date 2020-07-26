"""
Map oplog to you custom interface. To, for example, have triggers in mongo.
see example in '__main__' below

https://gist.github.com/rescommunes/4e5035242b8e4b07ff3a
"""

import logging
from time import sleep
import pickle

from pymongo.errors import AutoReconnect, OperationFailure
from bson.timestamp import Timestamp as bson_Timestamp


log = logging.getLogger(__name__)
QUERY_OPTION_OPLOG_RELAY = 8


class TimestampHandler(object):
    def __init__(self, timestamp_file=None):
        self.timestamp_file = timestamp_file if timestamp_file is not None else 'current.ts'
        self.current = self.load()

    def load(self):
        log.debug("Loading: %s" % self.timestamp_file)
        try:
            fh = open(self.timestamp_file, 'rb')
            timestamp_time_op_count = pickle.load(fh)
            fh.close()
        except IOError as exc:
            log.debug("No timestamp file '%s'. Using defaults" % self.timestamp_file)
            timestamp_time_op_count = (0, 0)
        start_time, op_count = timestamp_time_op_count
        start_time = start_time if start_time is not None else 0
        return TimestampHandler.encode(start_time, op_count=op_count)

    def update(self, ts):
        self.current = ts
        return TimestampHandler.decode(ts)

    def save(self):
        log.debug("Saving: %s" % self.timestamp_file)
        timestamp_time_op_count = TimestampHandler.decode(
            self.current,
            with_op_count=True,
            as_unix_time=True
        )
        fh = open(self.timestamp_file, 'wb')
        pickle.dump(timestamp_time_op_count, fh)
        fh.close()

    def __str__(self):
        dt, op_count = TimestampHandler.decode(self.current, with_op_count=True)
        return "%s (op_count=%d)" % (dt, op_count)

    @staticmethod
    def encode(bson_timestamp_time, op_count=None):
        op_count = op_count if op_count is not None else 0
        return bson_Timestamp(bson_timestamp_time, op_count)

    @staticmethod
    def decode(timestamp, with_op_count=False, as_unix_time=False):
        if not as_unix_time:
            timestamp_time = timestamp.as_datetime()
        else:
            timestamp_time = timestamp.time
        if not with_op_count:
            return timestamp_time
        return timestamp_time, timestamp.inc


class OperationManagers(object):
    def __init__(self, connection, manager_map):
        self.manager_map = {}
        self._load(connection, manager_map)

    def _load(self, connection, manager_map):
        for manager_class, namespace_map in manager_map.items():
            manager_instance = manager_class(connection)
            self.manager_map[manager_instance] = namespace_map

    def all_managers(self):
        return self.manager_map.keys()

    def namespace_managers(self, ns):
        namespace_parts = ns.split('.')
        managers = []
        for manager, namespace_map in self.manager_map.items():
            if namespace_parts in namespace_map:
                managers.append(manager)
                continue

            for wild_match in OperationManagers.namespace_wild_match(namespace_parts):
                if wild_match in namespace_map:
                    managers.append(manager)
                    continue
        managers = list(set(managers))
        return managers, ns.split('.')

    @staticmethod
    def namespace_wild_match(namespace_parts):
        for idx in range(len(namespace_parts) - 1, -1, -1):
            yield namespace_parts[:idx] + ['*'] * len(namespace_parts[idx:])


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class OperationInterface(object):
    def __init__(self, mongo_connection):
        self.mongo_connection = mongo_connection

    def insert(self, timestamp, namespace, document):
        log.debug("%s Unprocessed insert: %s %r" % (self, timestamp, namespace))

    def update(self, timestamp, namespace, doc_id, update_spec):
        log.debug("%s Unprocessed update: %s %r" % (self, timestamp, namespace))

    def delete(self, timestamp, namespace, doc_id):
        log.debug("%s Unprocessed delete: %s %r" % (self, timestamp, namespace))

    def command(self, timestamp, namespace, command_doc):
        log.debug("%s Unprocessed command: %s %r" % (self, timestamp, namespace))

    def noop(self, timestamp, namespace, noop_doc):
        log.debug("%s Unprocessed noop: %s %r" % (self, timestamp, namespace))

    def unknown_op(self, entry, more=None):
        log.warn("%s Unknown Entry: %r,  %r" % (self, more, entry))

    def __repr__(self):
        return "<OperationInterface:%s>" % self.__class__.__name__


class TailOplog(object):
    POLL_TIME = 1

    def __init__(self, connection, manager_map, ts):
        self._connection = connection
        self._operation_manager = OperationManagers(connection, manager_map)
        self._oplog = self.oplog_collection()
        self._ts = ts
        self._is_running = True

    def oplog_collection(self):
        collection_name = 'oplog.rs'
        valid_oplog_connection(self._connection)
        log.debug("Opening oplog collection %r" % collection_name)
        return self._connection.local[collection_name]

    def next_ops(self):
        query = {'ts': {'$gt': self._ts.current}}
        cursor = self._oplog.find(query, tailable=True)
        cursor.add_option(QUERY_OPTION_OPLOG_RELAY)
        log.debug('Next ops: %s' % self._ts)
        return cursor

    def stop(self):
        self._is_running = False

    def start(self):
        while self._is_running:
            try:
                next_ops_cursor = self.next_ops()
                self.tail(next_ops_cursor)
                sleep(self.POLL_TIME)
            except (AutoReconnect, OperationFailure) as exc:
                log.warn("%s, %s" % (exc.__class__.__name__, exc))

    def tail(self, next_ops_cursor):
        for current_op in next_ops_cursor:
            if not self._is_running:
                break
            try:
                dt_timestamp = self._ts.update(current_op['ts'])
                namespace = current_op['ns']
            except KeyError as exc:
                for manager in self._operation_manager.all_managers():
                    manager.unknown_op(current_op, more=exc)
                continue
            managers, namespace = self._operation_manager.namespace_managers(namespace)
            if not managers:
                continue
            operation = current_op['op']
            for manager in managers:
                if operation == 'i':
                    document = current_op['o']
                    manager.insert(dt_timestamp, namespace, document)
                elif operation == 'u':
                    doc_id = current_op['o2']['_id']
                    update_spec = current_op['o']
                    manager.update(dt_timestamp, namespace, doc_id, update_spec)
                elif operation == 'd':
                    doc_id = current_op['o']['_id']
                    manager.delete(dt_timestamp, namespace, doc_id)
                elif operation == 'c':
                    command_doc = current_op['o']
                    manager.command(dt_timestamp, namespace, command_doc)
                elif operation == 'n':
                    noop_doc = current_op['o']
                    manager.noop(dt_timestamp, namespace, noop_doc)
                else:
                    manager.unknown_op(current_op, more="no_op")
            self._ts.save()


def valid_oplog_connection(connection):
    try:
        connection.admin.command("isdbgrid")
        raise Exception("No support for dbgrid")
    except OperationFailure:
        pass
    main = connection.admin.command("isMain")
    if not main or 'setName' not in main:
        raise Exception("Need replica set to have an oplog")
    log.info("Using replica set: '%s' on %r " % (main["setName"], connection))


if __name__ == '__main__':
    """
    Example
    note: if oplog is old (its a capped collection) you will be missing entries
          in that case you'd need to sync up the /thing/ your modifying
    """
    from pymongo import MongoClient
    import signal

    logging.basicConfig(level=logging.DEBUG)

    def stop_on_sigint(stoppable_instance):
        # noinspection PyUnusedLocal
        def signal_handler(signal_int, frame):
            log.info('Stopping Instance: %r' % stoppable_instance)
            stoppable_instance.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)

    class OperationLocal(OperationInterface):
        def __init__(self, connection):
            super(OperationLocal, self).__init__(connection)
            self.local = {}

        def insert(self, timestamp, namespace, document):
            """if your NOT working on some *system* namespace you'll have document[_id]"""
            log.debug("Inserting: %s" % document['_id'])
            self.local[document['_id']] = document

        def update(self, timestamp, namespace, doc_id, update_spec):
            """
            update_spec is way to complex to solve for this example. We just use find_one.
            This  method is problematic if the current ts is old and the document
               was modified or deleted. Depends on what happening but, you can
               peek into update_spec to see if work is necessary
            """
            collection = self.mongo_connection[namespace[0]][namespace[1]]
            document = collection.find_one({'_id': doc_id})
            if document:
                log.debug("Updating: %s" % doc_id)
                self.local[doc_id] = document

        def delete(self, timestamp, namespace, doc_id):
            log.debug("Deleting: %s" % doc_id)
            del self.local[doc_id]


    base_connection = MongoClient(host='localhost', tz_aware=True)

    """
    mapping can use '*' to represent anything in order so
     [['*']] would match any ns which is length 1 (ie: noop)
     [['*', '*']] would match any ns which is length 2
     [['*', '*', '*']] would map any ns which is length 3 (ie "db.something.index")
    or you can get specific from left to right only
     [['database', '*', '*'], ['database','collection']] etc

    multiple `OperationInterface`s would work but, the timestamp handling my get out of
     sync if you have errors.

    """
    test_manager_map = {
        OperationLocal: [
            ['database', 'organization'],
            ['database', 'collection_2'],
            ['other', 'collection_1']
        ]
    }

    ts_handler = TimestampHandler(timestamp_file="local.current.ts")
    watch = TailOplog(base_connection, test_manager_map, ts_handler)
    log.info('Starting: %r' % watch.__class__.__name__)
    stop_on_sigint(watch)
    watch.start()