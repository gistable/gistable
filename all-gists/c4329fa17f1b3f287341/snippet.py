# coding: utf-8

from TCLIService import TCLIService
from TCLIService.ttypes import TOpenSessionReq, TGetTablesReq, TFetchResultsReq, \
    TStatusCode, TGetResultSetMetadataReq, TGetColumnsReq, TType, TTypeId, \
    TExecuteStatementReq, TGetOperationStatusReq, TFetchOrientation, TCloseOperationReq, \
    TCloseSessionReq, TGetSchemasReq, TCancelOperationReq, THandleIdentifier, \
    TOperationHandle, TOperationState

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class HiveServerTColumnValue:
    def __init__(self, tcolumn_value):
        self.column_value = tcolumn_value

    @property
    def val(self):
        if self.column_value.boolVal is not None:
            return self.column_value.boolVal.value
        elif self.column_value.byteVal is not None:
            return self.column_value.byteVal.value
        elif self.column_value.i16Val is not None:
            return self.column_value.i16Val.value
        elif self.column_value.i32Val is not None:
            return self.column_value.i32Val.value
        elif self.column_value.i64Val is not None:
            return self.column_value.i64Val.value
        elif self.column_value.doubleVal is not None:
            return self.column_value.doubleVal.value
        elif self.column_value.stringVal is not None:
            return self.column_value.stringVal.value


class HiveServer2Connection(object):
    def __init__(self, host, port, user):
        self.host = host
        self.port = port
        self.user = user
        self.session_handle = None
        self._client = None

    def connect(self):
        transport = TSocket.TSocket(self.host, self.port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = TCLIService.Client(protocol)
        transport.open()
        self._client = client

    def open_session(self, username):
        req = TOpenSessionReq(username=username, configuration={})
        res = self._client.OpenSession(req)
        session_handle = res.sessionHandle
        return session_handle

    def call(self, fn, req, status=TStatusCode.SUCCESS_STATUS):
        if self.session_handle is None:
            self.session_handle = self.open_session(self.user)
        if hasattr(req, 'sessionHandle') and req.sessionHandle is None:
            req.sessionHandle = self.session_handle
        res = fn(req)
        return res

    def execute_statement(self, statement):
        req = TExecuteStatementReq(statement=statement, confOverlay={}, runAsync=True)
        res = self.call(self._client.ExecuteStatement, req)
        return res.operationHandle

    def fetch_result(self, operation_handle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=1000):
        fetch_req = TFetchResultsReq(operationHandle=operation_handle, orientation=orientation, maxRows=max_rows)
        res = self.call(self._client.FetchResults, fetch_req)
        if operation_handle.hasResultSet:
            meta_req = TGetResultSetMetadataReq(operationHandle=operation_handle)
            schema = self.call(self._client.GetResultSetMetadata, meta_req)
        else:
            schema = None
        return res, schema

    def query_state(self, operation_handle):
        req = TGetOperationStatusReq(operation_handle)
        res = self._client.GetOperationStatus(req)
        return res

    def cancel_operation(self, operation_handle):
        req = TCancelOperationReq(operation_handle)
        return self._client.CancelOperation(req)

    def close_session(self):
        req = TCloseSessionReq(sessionHandle=self.session_handle)
        return self._client.CloseSession(req)

    def close(self):
        self._client._iprot.trans.close()

    def cursor(self, secret=None, guid=None):
        if self._client is None:
            self.connect()
        return HiveServer2Cursor(self, secret, guid)


class HiveServer2Cursor(object):
    def __init__(self, conn, secret=None, guid=None):
        self.conn = conn
        self.secret = secret
        self.guid = guid
        self.operation_handle = self._make_operation_handle(self.secret, self.guid)

    @staticmethod
    def _make_operation_handle(secret, guid):
        if secret is None or guid is None:
            return None
        operation_id = THandleIdentifier(secret=secret, guid=guid)
        return TOperationHandle(hasResultSet=True, modifiedRowCount=None, operationType=0, operationId=operation_id)

    def execute(self, statement):
        self.operation_handle = self.conn.execute_statement(statement)
        if self.operation_handle is None:
            return False
        self.secret = self.operation_handle.operationId.secret
        self.guid = self.operation_handle.operationId.guid
        return True

    def get_state(self):
        res = self.conn.query_state(self.operation_handle)
        if res.operationState == TOperationState.FINISHED_STATE:
            return 1
        elif res.operationState == TOperationState.CLOSED_STATE or res.operationState == TOperationState.ERROR_STATE \
                or res.operationState == TOperationState.UKNOWN_STATE:
            return 2
        elif res.operationState == TOperationState.CANCELED_STATE:
            return 3
        return 0

    def fetch_result(self, max_rows=1000):
        def append_rows(_rlst, results):
            for row in results.rows:
                _rlst.append([HiveServerTColumnValue(column).val for column in row.colVals])
            return _rlst

        rlst = []
        while True:
            res, schema = self.conn.fetch_result(self.operation_handle, max_rows=max_rows)
            # hasMoreRows属性失效了
            if len(res.results.rows) == 0:
                break
            append_rows(rlst, res.results)
        return rlst

    def cancel_operation(self):
        return self.conn.cancel_operation(self.operation_handle)

    def close(self):
        return self.conn.close_session()


def main():
    from time import sleep

    conn1 = HiveServer2Connection(host='yourhost', port=10000, user='root')
    try:
        cur = conn1.cursor()
        cur.execute('select count(*) from test')
        secret = cur.secret
        guid = cur.guid
        # 原有的session不能断，否则查询会中断
        # cur.close()
    finally:
        conn1.close()
    conn2 = HiveServer2Connection(host='yourhost', port=10000, user='root')
    try:
        cur = conn2.cursor(secret=secret, guid=guid)
        while cur.get_state() == 0:
            print 'running'
            sleep(1)
        if cur.get_state() == 1:
            print 'success'
            for r in cur.fetch_result():
                print r[0]
        elif cur.get_state() == 2:
            print 'failed'
        cur.close()
    finally:
        conn2.close()


if __name__ == '__main__':
    main()