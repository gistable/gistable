# -*- coding: utf-8 -*-
from twisted.enterprise import adbapi
from twisted.python import log
import MySQLdb
import itertools

class ReconnectingMixin:
    """MySQL 重新连接时， ConnectionPool 可以正确执行指定的操作，流程是：

    - 执行操作
    - 如果是连接错误，重新执行一次操作

    参考:

    - http://www.gelens.org/2008/09/12/reinitializing-twisted-connectionpool/
    - http://www.gelens.org/2009/09/13/twisted-connectionpool-revisited/
    - http://twistedmatrix.com/pipermail/twisted-python/2009-July/020007.html

    """
    def _myRunInteraction(self, interaction, *args, **kw):
        '''拷贝自 adbapi.ConnectionPool._runInteraction

        简化了 _runInteraction:
        
        - 去掉对俘获到的异常的打印，而是交给下面的 _runInteraction 处理
        - 取消 rollback 操作，有需要 rollback 的请注意，只是我从来没用过
        '''
        conn = self.connectionFactory(self)
        trans = self.transactionFactory(self, conn)
        result = interaction(trans, *args, **kw)
        trans.close()
        conn.commit()
        return result

    def _runInteraction(self, interaction, *args, **kw):
        try:
            return self._myRunInteraction(interaction, *args, **kw)
        except MySQLdb.OperationalError, e:
            if e[0] not in (2006, 2013):
                raise
            log.msg("MySQLdb: got error %s, retrying operation" %(e))
            conn = self.connections.get(self.threadID())
            self.disconnect(conn)
            # try the interaction again
            return self._myRunInteraction(interaction, *args, **kw)

class InsertIdMixin:
    """在Twisted下用MySQL adbapi获取自增id

    http://blog.sina.com.cn/s/blog_6262a50e0101nbqc.html

    """
    def runMySQLInsert(self, *args, **kw):
        return self.runInteraction(self._runMySQLInsert, *args, **kw)

    def _runMySQLInsert(self, trans, *args, **kw):
        trans.execute(*args, **kw)
        return trans.connection.insert_id()


class MultiQueryMixin:
    """返回多个结果集
    """
    def runMultiQuery(self, *args, **kw):
        return self.runInteraction(self._runMultiQuery, *args, **kw)

    def _runMultiQuery(self, trans, *args, **kw):
        result_sets = kw.pop("result_sets", None)

        trans.execute(*args, **kw)

        results = []
        for i in itertools.count():
            if not result_sets or i in result_sets:
                results.append(trans.fetchall())
            if not trans.nextset():
                break

        return results


class ConnectionPool(ReconnectingMixin, InsertIdMixin, MultiQueryMixin, adbapi.ConnectionPool):
    def __init__(self, *connargs, **connkw):
        adbapi.ConnectionPool.__init__(self, 'MySQLdb', *connargs, **connkw)
