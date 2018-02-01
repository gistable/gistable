#!/usr/bin/python3.5

# Author: Dagang Wei (github.com/weidagang)
# Created: 2016-11-19
# Last modified: 2016-11-27
# License: MIT
# Self link: https://gist.github.com/weidagang/1b001d0e55c4eff15ad34cc469fafb84
#
# This code demonstrates the core algorithm for distributed MVCC based cross-row
# transactions. The algorithm is built on top of a distributed key-value database
# with single-row transaction support, which is very common for most of the
# mainstream NoSQL databases. Hence it can be used to build a cross-row transaction
# layer for those databases.
#
# The algorithm originates from Google's paper "Large-scale Incremental
# Processing Using Distributed Transactions and Notifications":
# https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Peng.pdf
#
# This implementation improved the original algorithm in error handlings which
# are not covered in the paper.
#
# [The public interface]
#
# In the public interface, a key-value store model is presented to the client,
# keys are 2 dimensional tuples (row_key, column_name), where row_key,
# column_name, values are all strings. For example, a bank account balance may
# look like ("account-22356", "balance") -> "123.5" and the holder may look like
# ("account-22356", "holder") -> "John Smith".
#
# [The underlying multi-verioned key-value storage engine]
#
# This algorithm assumes that we already have a distributed key-value database
# with single-row transaction support as the building block. Both the raw
# data and the meta data required to support multi-row transactions will be
# stored there.
#
# In the underlying key-value store model, key is a 3 dimensional tuple
# (row_key, column_name, timestamp), where row_key and column_name are strings,
# timestamp is integer. We call their corresponding values: row, column and
# cell. A column is comprised of multiple cells at different timestamps, a row
# is comprised of multiple columns.
#
# This code uses a fake in-memory key-value store for demonstration purpose, in
# practice, it should be replaced by real distributed NoSQL databases such as
# HBase.
#
# [The transaction model]
#
# There is a centralized timestamp generator called Timestamp Oracle (TSO) in
# the system, which generates mononitically increasing timestamps. Timestamps
# are used to establish a total order among transactions. Conceptually the state
# of the database moves forward step by step at discret timestamps. All the
# reads of a transaction happen instantly at its start timestamp, all the writes
# happen instantly at its commit timestamp. The transaction algorithm will
# detect conflicts and abort some of the conflicting transactions to prevent
# anomalies from happening which violates the order implied by the timestamps.
#
# When a transaction starts, it will be assigned a timestamp from the TSO as its
# start timestamp. Reads are from the snapshot of the database at the start
# timestamp. Only the latest data committed before the start timestamp is
# visible to the transaction.
#
# Read-only transactions don't need to commit, as they donn't take any locks.
# Mutations in a transaction will be buffered until commit time. When a
# transaction begins to commit, it will take a 2-phase commit approach. In the
# first phase, it prewrites the mutations along with locks at the transaction's
# start timestamp for each modified key. If no conflict is detected in this
# phase, it enters the second phase, in which a new timestamp from the TSO will
# be assigned to the transaction as its commit timestamp, and a meta data will
# be created at the commit timestamp. If any conflicts are detected, in the
# first phase, at most one of the conflicting transactions is allowed to
# proceed, others will have to be aborted.
#
# The atomicity property of this transaction algorithm is guaranteed by
# selecting one of the mutated keys as primary key, whose state represents the
# state of the whole transaction. Other keys are seconary, who have a reference
# to the primary. The atomicity of the multi-row transaction is then derived
# from the atomicity of the single-row transaction on the primary. Once the
# primary is committed or aborted, the secondaries must roll forward or back
# deterministically, but this follow-on process can happen asynchronously, or
# even be done by other transactions in the event of failure.

from typing import Dict, Tuple, List

# Constants
MIN_TS = 0
MAX_TS = (2 ** 64) - 1
LOCK_TIMEOUT = 2

# Basic types.
RowKey = str
ColumnName = str
Timestamp = int
Data = str

class ColumnKey:
  """Column key which is comprised of a row key and a column name."""
  def __init__(self, row_key: RowKey, column_name: ColumnName):
    self.row_key = row_key
    self.column_name = column_name

  @staticmethod
  def parse(column_key: str):
    row_key = column_key.split('/')[0]
    column_name = column_key.split('/')[1]
    return ColumnKey(row_key, column_name)

  def __str__(self):
    return '/'.join([self.row_key, self.column_name])

class Cell:
  def __init__(self, ts: Timestamp, value: Data):
    self.ts = ts
    self.value = value

  def __str__(self):
    return '{%d : %s}' % (self.ts, self.value)

class Column:
  def __init__(self):
    self.cells = [] # type: [Cell]

  def _str__(self):
    return str(self.cells)

class Row:
  def __init__(self):
    self.columns = {} # type: Dict[ColumnKey, Column]

  def __str__(self):
    return str(self.columns)

# The non-essential part of this code, which serves as a building block of the
# transaction algorithm. In practice, this should be a standalone service.
class TimestampOracle:
  """Timestamp oracle which generates mononitically increasing timestamps."""
  def __init__(self):
    self.ts = 0

  def next(self) -> int:
    self.ts = self.ts + 1
    return self.ts

# The non-essential part of this code.
class RowTransaction:
  """Single-row transaction for the underlying key-value storage engine.
  """
  def __init__(self, rows: Dict[RowKey, Row], row_key: RowKey):
    self.rows = rows
    self.row_key = row_key
    self.rollback_actions = []

  def get(
      self,
      column_name: str,
      min_ts:Timestamp=MIN_TS,
      max_ts:Timestamp=MAX_TS) -> Cell:
    """Gets the cell with the largest timestamp in the range of
       [min_ts, max_ts].
    """
    if self.row_key in self.rows and (
        column_name in self.rows[self.row_key].columns):
      max_cell = None
      for cell in self.rows[self.row_key].columns[column_name].cells:
        if cell.ts >= min_ts and cell.ts <= max_ts and (
            not max_cell or cell.ts > max_cell.ts):
          max_cell = cell
      return max_cell

  def write(self, column_name: str, ts: int, value: Data):
    """Inserts or updates a cell."""
    cell = Cell(ts, value)
    if not self.row_key in self.rows:
      self.rows[self.row_key] = Row()
      self.rollback_actions.append(lambda: self.rows.pop(self.row_key))
    if not column_name in self.rows[self.row_key].columns:
      self.rows[self.row_key].columns[column_name] = Column()
      self.rollback_actions.append(
          lambda: self.rows[self.row_key].columns.pop(column_name))
    index = len(self.rows[self.row_key].columns[column_name].cells)
    self.rows[self.row_key].columns[column_name].cells.append(cell)
    self.rollback_actions.append(
        lambda: self.rows[self.row_key].columns[column_name].cells.pop(index))

  def erase(self, column_name: str, ts: int):
    """Erases a cell, returns true if the cell exists, false otherwise."""
    if not self.row_key in self.rows:
      return False
    if not column_name in self.rows[self.row_key].columns:
      return False
    indices = [
        idx
        for idx, cell
        in enumerate(self.rows[self.row_key].columns[column_name].cells)
        if cell.ts == ts]
    index = indices[0] if indices else None
    if index is None:
      return False
    cell = self.rows[self.row_key].columns[column_name].cells[index]
    del self.rows[self.row_key].columns[column_name].cells[index]
    self.rollback_actions.append(
        lambda: self.rows[self.row_key].columns[column_name].cells.append(
            cell))
    return True

  def commit(self) -> bool:
    """Commits this transaction.

       In this fake in-memory store, commit never fails.
    """
    self.rollback_actions = []
    return True

  def abort(self):
    """Aborts this transaction."""
    for action in reversed(self.rollback_actions):
      action()

# The non-essential part of this code which serves as a building block of the
# transaction algorithm. Here we use a fake in-memory store for demonstration
# purpose. In practice, this correponds a NoSQL database with single-row
# transaction support, e.g., HBase.
class KvStore:
  """The underlying distributed multi-versioned key-value store which supports
     single-row cross column/cell transactioins.
  """

  def __init__(self):
    self.rows = {} # row_key -> row

  def start_row_transaction(self, row_key: RowKey):
    return RowTransaction(self.rows, row_key)

class KeyLockedError(Exception):
  """Exception for `get` when a conflicting lock exists."""
  def __init__(self, row_key: RowKey, column_name: ColumnName, ts: Timestamp):
    self.row_key = row_key
    self.column_name = column_name
    self.ts = ts

  def __str__(self):
    return "Column (%s, %s) is locked by txn(ts=%d)." % (
        self.row_key, self.column_name, self.ts)

# The core part of this code.
class Transaction:
  """Distributed multi-row transaction of snapshot-isolation level."""

  # The following are dependencies shared across transactions:

  # 1) The underlying distributed multi-versioned key-value store with
  # single-row transaction support.
  kv_store = KvStore()

  # 2) The timestamp oracle which generates mononitically increasing timestamps.
  tso = TimestampOracle()

  def __init__(self):
    """Starts a new transaction."""
    # Assign start timestamp.
    self.start_ts = self.tso.next() # type: int
    # Writes are buffered until commit time.
    self.write_buffer = {} # type: Dict[RowKey, Dict[ColumnName, Data]]
    self._debug('START')

  def get(self, row_key: RowKey, column_name: ColumnName) -> Data:
    """Gets the value of a column from the snapshot at the start timestamp.

       Raises:
          KeyLockedError if the column is locked by another transaction.
    """
    self._debug('+get(r=%s, c=%s)' % (row_key, column_name))

    # Start a single-row transaction in the underlying key-value store.
    row_txn = self.kv_store.start_row_transaction(row_key)

    # Check if there is lock with smaller timestamp.
    lock_cell = row_txn.get(column_name + ":lock", max_ts=self.start_ts)
    if lock_cell:
      self._debug('found lock (r=%s, c=%s, ts=%d, pr=%s)' % (
          row_key, column_name, lock_cell.ts, lock_cell.value))
      # If lock cell is found, it doesn't necessarily mean there's pending
      # transaction, it could be the case that the transaction has been
      # committed or aborted, but the secondary locks haven't been cleaned up
      # yet.
      if self.start_ts - lock_cell.ts >= LOCK_TIMEOUT:
        # If the lock is too old, we help clean it up. If the transaction is
        # still in pending state, it will be aborted.
        self._clean_up_lock(row_txn, row_key, column_name, lock_cell)
      else:
        raise KeyLockedError(row_key, column_name, lock_cell.ts)

    # Read the latest write cell before the start timestamp.
    write_cell = row_txn.get(column_name + ":write", max_ts=self.start_ts-1)
    if write_cell:
      # Found committed data. The data cell is prewritten at the start timestamp
      # of the transaction, the write cell is at the commit timestamp. The value
      # of the write cell is the timestamp of the data cell.
      data_commit_ts = write_cell.ts
      data_cell_ts = write_cell.value
      data_cell = row_txn.get(
        column_name + ":data", min_ts=data_cell_ts, max_ts=data_cell_ts)
      data = data_cell.value
    else:
      data = None

    # It's always safe to commit the single-row transaction to release locks if
    # there's any, depending on the implementation.
    row_txn.commit()

    if data:
      self._debug('-get(r=%s, c=%s) -> {c_ts=%d, v=%s}' % (
          row_key, column_name, data_commit_ts, data))
    else:
      self._debug('-get(r=%s, c=%s) -> None' % (row_key, column_name))

    return data

  def set(self, row_key: RowKey, column_name: ColumnName, value: Data):
    """Sets the value of a column.

       Writes will be buffered until commit time. Deletion is represented as
       setting value to None.
    """
    self._debug('set(r=%s, c=%s, v=%s)' % (
        row_key, column_name, value))
    if not row_key in self.write_buffer:
      self.write_buffer[row_key] = {}
    if not column_name in self.write_buffer[row_key]:
      self.write_buffer[row_key][column_name] = value

  def commit(self) -> bool:
    self._debug('committing...')
    ok = self._commit()
    if ok:
      self._debug('COMMITED at %s' % self.commit_ts)
    else:
      self._debug('ABORTED')
    return ok

  def _commit(self) -> bool:
    self.commit_ts = None

    # Return true directly for read-only transaction.
    if not self.write_buffer:
      return True

    self._select_primary()

    ok = self._prewrite_primary_row()
    if not ok:
      return False

    ok = self._prewrite_secondary_rows()
    if not ok:
      return False

    self._assign_commit_ts()

    ok = self._commit_primary_row()
    if not ok:
      return False

    # At this point, the transaction has already been committed. Committing
    # secondaries can be done in a best-effort manner, e.g., asynchronously.
    self._commit_secondary_rows()

    return True

  def abort(self):
    """Aborts this transaction."""
    # No-op, since writes are buffered until commit time.
    pass

  def _select_primary(self):
    # Arbitrarily select 1 (row, column) as the primary, whose state represents
    # the state of the whole transaction. Secondary (row, column)s store the
    # key of the primary in their lock cells.
    row_keys = list(self.write_buffer.keys())
    row_keys.sort()
    self.primary_row_key = row_keys[0]
    column_names = list(self.write_buffer[self.primary_row_key].keys())
    column_names.sort()
    self.primary_column_name = column_names[0]
    self.primary_column_key = ColumnKey(
        self.primary_row_key, self.primary_column_name)

  def _prewrite_primary_row(self) -> bool:
    """Prewrites the primary row at the start timestamp."""
    ok = self._prewrite_row(self.primary_row_key)
    if not ok:
      self._rollback_prewrite()
      return False
    return True

  def _prewrite_secondary_rows(self) -> bool:
    """Prewrites the secondary rows at start timestamp.

    Returns:
        True if all the prewrites are successfully; false otherwise.
    """
    for row_key in self.write_buffer:
      if row_key == self.primary_row_key:
        continue
      ok = self._prewrite_row(row_key)
      if not ok:
        self._rollback_prewrite()
        return False
    return True

  def _prewrite_row(self, row_key: RowKey) -> bool:
    """Prewrites the buffered mutations to a row at the start timestamp.

    Returns:
        True if all the prewrites are successfully; false otherwise.
    """
    row_txn = self.kv_store.start_row_transaction(row_key)
    writes = self.write_buffer[row_key]
    for column_name in writes:
      ok = self._prewrite_column(
          row_txn, row_key, column_name, writes[column_name])
      if not ok:
        row_txn.abort()
        return False
    return row_txn.commit()

  def _prewrite_column(
      self,
      row_txn: RowTransaction,
      row_key: RowKey,
      column_name: ColumnName,
      value: Data) -> bool:
      """Prewrites the buffered mutation to a column at the start timestamp.

      Return:
          True if successfully; false otherwise.
      """
      # Abort on writes after our start timestamp.
      write_cell = row_txn.get(column_name + ":write", min_ts=self.start_ts+1)
      if write_cell:
        # This is write-write conflict, we must abort this transaction to ensure
        # snapshot isolation.
        print('txn(ts=%d): write was found at commit_ts=%d.' % (
            self.start_ts, write_cell.ts))
        return False

      # Or locks at any timestamp.
      lock_cell = row_txn.get(column_name + ":lock", max_ts=MAX_TS)
      if lock_cell:
        # If lock cell is found, it doesn't necessarily mean there's pending
        # transaction, it could be the case that the transaction has been
        # committed or aborted, but the secondary locks haven't been cleaned up
        # yet.

        if self.start_ts - lock_cell.ts >= LOCK_TIMEOUT:
          # If the lock is too old, we help clean it up. If the transaction is
          # still in pending state, it will be aborted.
          self._clean_up_lock(row_txn, row_key, column_name, lock_cell)
        else:
          # The lock is still effective, abort this transaction and let client
          # retry.
          return False

      # Write lock cell whose value is the primary_column_key at start_ts.
      row_txn.write(
          column_name + ":lock", self.start_ts, str(self.primary_column_key))
      # Wrtie data cell with the value at start_ts.
      row_txn.write(column_name + ":data", self.start_ts, value)
      return True

  def _assign_commit_ts(self):
    """Assigns commit timestamp to this transaction."""
    self.commit_ts = self.tso.next()

  def _commit_primary_row(self) -> bool:
    """Commits the primary row.

       This is the commit point of the whole transaction. It is possible that
       this transaction has already been aborted by another transaction, in
       which case, the lock should have been cleaned up.

       Returns:
           True if committed, false otherwise.
    """
    ok = self._commit_row(self.primary_row_key)
    if not ok:
      self._rollback_prewrite()
    else:
      self._debug('primary row was committed at ts %d' % self.commit_ts)
    return ok

  def _commit_secondary_rows(self):
    """Commits secondary rows.

       The transaction has already been committed when the primary row was
       commited. Committing secondary rows is a best effort work. If any of the
       underlying single-row transaction fails to commit, it will eventually be
       fixed by other transactions.
    """
    for row_key in self.write_buffer:
      if row_key == self.primary_row_key:
        # Ignore the primary row.
        continue
      self._commit_row(row_key)

  def _commit_row(self, row_key: RowKey) -> bool:
    """Commits the writes to a row in a single-row transaction.

       Returns:
           True if successful, false otherwise.
    """
    row_txn = self.kv_store.start_row_transaction(row_key)
    for column_name in self.write_buffer[row_key]:
      ok = self._commit_column_prewrite(
          row_txn, column_name, self.start_ts, self.commit_ts)
      if not ok:
        row_txn.abort()
        return False
    return row_txn.commit()

  def _rollback_prewrite(self):
    """Rolls back all the prewrites of this transaction."""
    for row_key in self.write_buffer:
      self._rollback_row_prewrite(row_key)

  def _rollback_row_prewrite(self, row_key: RowKey):
    """Rolls back the prewrites of a row."""
    row_txn = self.kv_store.start_row_transaction(row_key)
    for column_name in self.write_buffer[row_key]:
      self._rollback_column_prewrite(row_txn, column_name, self.start_ts)
    row_txn.commit()

  @staticmethod
  def _commit_column_prewrite(
      row_txn: RowTransaction,
      column_name: ColumnName,
      start_ts: Timestamp,
      commit_ts: Timestamp) -> bool:
    """Applies the prewrite of a column in a single-row transaction.

    Returns:
        True if successful, false otherwise.
    """
    lock_cell = row_txn.get(
        column_name + ":lock", min_ts=start_ts, max_ts=start_ts)
    commit_cell = row_txn.get(
        column_name + ":commit", min_ts=start_ts, max_ts=start_ts)
    if commit_cell:
      # The transaction has been committed by another transaction.
      return True
    if not lock_cell:
      # The transaction has been aborted by another transaction.
      return False
    # Create write cell at commit_ts pointing to the data cell at start_ts.
    row_txn.write(column_name + ":write", ts=commit_ts, value=start_ts)
    # Create commit cell at start_ts whose value is commit_ts.
    row_txn.write(column_name + ":commit", ts=start_ts, value=commit_ts)
    # Erase lock cell at start_ts.
    row_txn.erase(column_name + ":lock", ts=start_ts)
    return True

  @staticmethod
  def _rollback_column_prewrite(
      row_txn: RowTransaction, column_name: ColumnName, ts: Timestamp):
    """Rolls back the prewrite of a column in a single-row transaction.
    """
    row_txn.erase(column_name + ":lock", ts)
    row_txn.erase(column_name + ":data", ts)

  def _clean_up_lock(
      self,
      row_txn: RowTransaction,
      row_key: RowKey,
      column_name: ColumnName,
      lock_cell: Cell) -> bool:
    """Cleans up a lock in a single-row transaction.

       The lock's assoicated transaction may have been committed, aborted or
       still pending. If committed, we must roll forward the transaction; if
       aborted, we must roll back; if pending, we first abort it, then roll
       back.

    Returns:
        True if the lock is cleaned up, False otherwise.
    """
    primary_column_key = ColumnKey.parse(lock_cell.value)
    primary_row_key = primary_column_key.row_key
    primary_column_name = primary_column_key.column_name
    is_primary_row = (primary_row_key == row_key)
    is_primary_column = is_primary_row and (primary_column_name == column_name)

    # Create a single-row transaction or reuse the current for the primary row.
    if is_primary_row:
      primary_row_txn = row_txn
    else:
      primary_row_txn = self.kv_store.start_row_transaction(primary_row_key)

    # Roll back or roll forward the prewrite of the lock is determined by the
    # transaction state.
    rollback = True

    # Check the state of the lock's transaction by inspecting the primary row.
    primary_lock_cell = primary_row_txn.get(
        primary_column_name + ":lock", lock_cell.ts)
    if primary_lock_cell:
      # The transaction is pending, abort it. Need to roll back the prewrite of
      # the primary column first.
      self._rollback_column_prewrite(
          primary_row_txn, primary_column_name, lock_cell.ts)
      if not is_primary_row:
        # Commit the primary transaction only if it's not reusing the current.
        ok = primary_row_txn.commit()
        if not ok:
          return False
      rollback = True
      self._debug('cleaned up pending primary lock (%s, %s, %d)' % (
          primary_row_key, primary_column_name, lock_cell.ts))
      print('Txn(s_ts=%d): ABORTED' % lock_cell.ts)
    else:
      # The transaction is either committed or aborted, must inspect the commit
      # cell.
      primary_commit_cell = primary_row_txn.get(
          primary_column_name + ":commit", lock_cell.ts)
      if primary_commit_cell:
        # The transaction is committed, roll forward the current prewrite.
        rollback = False
      else:
        # The transaction is aborted, roll back the current prewrite.
        rollback = True

    # At this point, the primary column must have been either committed or
    # aborted.

    if rollback:
      if not is_primary_column:
        self._rollback_column_prewrite(row_txn, column_name, lock_cell.ts)
        self._debug('cleaned up pending secondary lock (%s, %s, %d)' % (
            row_key, column_name, lock_cell.ts))
        self._debug('helped roll back secondary prewrite of txn(ts=%d)' % (
            lock_cell.ts))
    else:
      self._commit_column_prewrite(
          row_txn,
          column_name,
          start_ts=lock_cell.ts,
          commit_ts=primary_commit_cell.value)
      self._debug('helped roll forward secondary prewrite of txn(ts=%d)' % (
          lock_cell.ts))

  def _debug(self, message):
    print('Txn(s_ts=%d): %s' % (self.start_ts, message))

#### Unit tests ####
import unittest

class Tests(unittest.TestCase):
  def _test_snapshot_read(self):
    # Initialize John's account.
    txn0 = Transaction()
    txn0.set('john', 'balance', 123)
    txn0.set('john', 'age', 28)
    ok = txn0.commit()
    self.assertTrue(ok)

    txn1 = Transaction()
    txn2 = Transaction()

    # Initialize Bob and Smith's accounts
    bob_balance = txn1.get('bob', 'balance')
    self.assertIsNone(bob_balance)
    txn1.set('bob', 'balance', 100)
    txn1.set('bob', 'age', 23)
    txn1.set('smith', 'balance', 200)
    txn1.set('smith', 'age', 35)

    # Txn1 should not be visible to txn2.
    smith_balance = txn2.get('smith', 'balance')
    self.assertIsNone(smith_balance)

    ok = txn1.commit()
    self.assertTrue(ok)

    # Txn1 should not be visible to txn2, even after it is comitted.
    bob_balance = txn2.get('bob', 'balance')
    self.assertIsNone(bob_balance)
    txn2.set('john', 'balance', None)
    txn2.set('john', 'age', None)
    ok = txn2.commit()
    self.assertTrue(ok)

    # Txn1 should be visible to txn3.
    txn3 = Transaction()
    bob_balance = txn3.get('bob', 'balance')
    self.assertEqual(bob_balance, 100)
    bob_age = txn3.get('bob', 'age')
    self.assertEqual(bob_age, 23)
    smith_balance = txn3.get('smith', 'balance')
    self.assertEqual(smith_balance, 200)
    smith_age = txn3.get('bob', 'age')
    self.assertEqual(smith_age, 23)
    john_balance = txn3.get('john', 'balance')
    self.assertIsNone(john_balance)
    john_age = txn3.get('john', 'age')
    self.assertIsNone(john_age)
    # Transfer $25 from bob to smith.
    txn3.set('bob', 'balance', bob_balance + 25)
    txn3.set('smith', 'balance', smith_balance - 25)
    txn3.commit()

  def _test_write_write_conflict(self):
    # Txn4 and txn5 are in race to update bob's balance, the first to commit
    # wins.
    txn4 = Transaction()
    bob_balance = txn4.get('bob', 'balance')
    self.assertEqual(bob_balance, 125)
    txn5 = Transaction()
    txn5.set('bob', 'balance', 0)
    smith_balance = txn4.get('smith', 'balance')
    self.assertEqual(smith_balance, 175)
    txn4.set('bob', 'balance', bob_balance + 25)
    txn4.set('smith', 'balance', smith_balance - 25)
    ok = txn4.commit()
    self.assertTrue(ok)
    ok = txn5.commit()
    self.assertTrue(not ok)

  def _test_prewrite_read_conflict(self):
    txn6 = Transaction()
    txn7 = Transaction()
    txn6.set('bob', 'balance', 175)
    txn6.set('smith', 'balance', 125)
    # Test through private method to simulate txn6 has just finished prewrite.
    txn6._select_primary()
    ok = txn6._prewrite_primary_row()
    self.assertTrue(ok)
    ok = txn6._prewrite_secondary_rows()
    self.assertTrue(ok)
    self.assertRaises(KeyLockedError, lambda: txn7.get('smith', 'balance'))
    txn6._assign_commit_ts()
    ok = txn6._commit_primary_row()
    self.assertTrue(ok)
    txn6._commit_secondary_rows()

  def _test_roll_back_pending_transaction_by_conflicting_read(self):
    txn8 = Transaction()
    txn9 = Transaction()
    txn8.set('bob', 'balance', 200)
    txn8.set('smith', 'balance', 100)
    # Test through private method to simulate txn8 has just finished prewrite.
    txn8._select_primary()
    ok = txn8._prewrite_primary_row()
    self.assertTrue(ok)
    ok = txn8._prewrite_secondary_rows()
    self.assertTrue(ok)

    # The 1st read should fail for the lock.
    self.assertRaises(KeyLockedError, lambda: txn9.get('smith', 'balance'))

    # The 2nd read should succeed for LOCK_TIMEOUT = 2.
    txn10 = Transaction()
    smith_balance = txn10.get('smith', 'balance')
    self.assertEqual(smith_balance, 125) # The value before txn8

    txn8._assign_commit_ts()
    ok = txn8._commit_primary_row()
    self.assertFalse(ok) # Txn8 should fail to commit since it has been aborted.

  def _test_roll_forward_secondary_prewrites_by_read(self):
    txn11 = Transaction()
    txn11.set('bob', 'balance', 200)
    txn11.set('smith', 'balance', 100)
    # Test through private method to simulate txn11 has just finished committing
    # primary row.
    txn11._select_primary()
    ok = txn11._prewrite_primary_row()
    self.assertTrue(ok)
    ok = txn11._prewrite_secondary_rows()
    self.assertTrue(ok)
    txn11._assign_commit_ts()
    ok = txn11._commit_primary_row()
    self.assertTrue(ok)

    # Txn12 should help roll forward txn11.
    txn12 = Transaction()
    bob_balance = txn12.get('bob', 'balance')
    self.assertEqual(bob_balance, 200)
    smith_balance = txn12.get('smith', 'balance')
    self.assertEqual(smith_balance, 100)

  def _test_roll_forward_secondary_prewrites_by_prewrite(self):
    txn13 = Transaction()
    txn13.set('bob', 'balance', 110)
    txn13.set('smith', 'balance', 120)
    # Test through private method to simulate txn13 has just finished committing
    # primary row.
    txn13._select_primary()
    ok = txn13._prewrite_primary_row()
    self.assertTrue(ok)
    ok = txn13._prewrite_secondary_rows()
    self.assertTrue(ok)
    txn13._assign_commit_ts()
    ok = txn13._commit_primary_row()
    self.assertTrue(ok)

    # Txn14 should help roll forward txn13.
    txn14 = Transaction()
    txn14.set('bob', 'balance', 90)
    txn14.set('smith', 'balance', 140)
    ok = txn14.commit()
    self.assertTrue(ok)

    txn15 = Transaction()
    bob_balance = txn15.get('bob', 'balance')
    self.assertTrue(bob_balance == 90)
    smith_balance = txn15.get('smith', 'balance')
    self.assertTrue(smith_balance == 140)

  def _test_roll_back_secondary_prewrites_by_read(self):
    txn16 = Transaction()
    txn16.set('bob', 'balance', 80)
    txn16.set('smith', 'balance', 150)
    # Test through private method to simulate txn11 has just finished prewrite.
    txn16._select_primary()
    ok = txn16._prewrite_primary_row()
    self.assertTrue(ok)

    txn17 = Transaction()

    # Txn18 should abort txn16 (clean up the primary prewrite) for
    # LOCK_TIMEOUT = 2.
    txn18 = Transaction()
    bob_balance = txn18.get('bob', 'balance')
    self.assertEqual(bob_balance, 90) # The value before txn16

    # Txn16 should succeed to prewite seconary rows, even if the primary has
    # been rolled back.
    ok = txn16._prewrite_secondary_rows()
    self.assertTrue(ok)

    # Txn19 should roll back the seconary prewrite.
    txn19 = Transaction()
    bob_balance = txn19.get('smith', 'balance')
    self.assertEqual(bob_balance, 140) # The value before txn16

  def test_kv_store(self):
    kv_store = KvStore()

    txn1 = kv_store.start_row_transaction("row-1")
    txn1.write('column-a', ts=2, value='value-1')
    txn1.write('column-b', ts=2, value='value-2')
    txn1.commit()

    txn2 = kv_store.start_row_transaction("row-1")
    self.assertEqual(txn2.get('column-a', min_ts=0, max_ts=3).value, 'value-1')
    txn2.write('column-a', ts=4, value='value-3')
    txn2.write('column-a', ts=4, value='value-4')
    txn2.abort()

    txn3 = kv_store.start_row_transaction("row-1")
    self.assertEqual(txn3.get('column-a', min_ts=0, max_ts=5).value, 'value-1')
    self.assertEqual(txn3.get('column-b', min_ts=0, max_ts=5).value, 'value-2')
    erased = txn3.erase('column-a', ts=2)
    txn3.commit()

    txn4 = kv_store.start_row_transaction("row-1")
    self.assertIsNone(txn4.get('column-a', min_ts=0, max_ts=5))

  def test_transaction(self):
    self._test_snapshot_read()
    self._test_write_write_conflict()
    self._test_prewrite_read_conflict()
    self._test_roll_back_pending_transaction_by_conflicting_read()
    self._test_roll_forward_secondary_prewrites_by_read()
    self._test_roll_forward_secondary_prewrites_by_prewrite()
    self._test_roll_back_secondary_prewrites_by_read()

if __name__ == '__main__':
  unittest.main()
