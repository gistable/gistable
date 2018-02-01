#! /usr/bin/env python
# -*- coding: utf-8 *-*
#
# Copyright (C) Nicolas Bareil <nico@chdir.org>
#
# This program is published under Apache 2.0 license

from optparse import OptionParser
import fileinput
import logging
import os
import sys
import struct
import ntfs.mft.MFT

ops = {
    0x00:                         'Noop',
    0x01:        'CompensationLogRecord',
    0x02:  'InitializeFileRecordSegment',
    0x03:  'DeallocateFileRecordSegment',
    0x04:  'WriteEndOfFileRecordSegment',
    0x05:              'CreateAttribute',
    0x06:              'DeleteAttribute',
    0x07:          'UpdateResidentValue',
    0x08:       'UpdateNonresidentValue',
    0x09:           'UpdateMappingPairs',
    0x0A:          'DeleteDirtyClusters',
    0x0B:         'SetNewAttributeSizes',
    0x0C:            'AddIndexEntryRoot',
    0x0D:         'DeleteIndexEntryRoot',
    0x0E:      'AddIndexEntryAllocation',
    0x0F:   'DeleteIndexEntryAllocation',
    0x10:        'WriteEndOfIndexBuffer',
    0x11:         'SetIndexEntryVcnRoot',
    0x12:   'SetIndexEntryVcnAllocation',
    0x13:           'UpdateFileNameRoot',
    0x14:     'UpdateFileNameAllocation',
    0x15:   'SetBitsInNonresidentBitMap',
    0x16: 'ClearBitsInNonresidentBitMap',
    0x17:                       'HotFix',
    0x18:            'EndTopLevelAction',
    0x19:           'PrepareTransaction',
    0x1A:            'CommitTransaction',
    0x1B:            'ForgetTransaction',
    0x1C:     'OpenNonresidentAttribute',
    0x1D:       'OpenAttributeTableDump',
    0x1E:           'AttributeNamesDump',
    0x1F:           'DirtyPageTableDump',
    0x20:         'TransactionTableDump',
    0x21:         'UpdateRecordDataRoot',
    0x22:   'UpdateRecordDataAllocation' ,
}

recordHeaderLength = 48          # restartArea->RecordHeaderLength
updateSequenceArrayOffset = 0x40 # restartArea->UpdateSequenceArrayOffset
updateSequenceArraySize = 9      # restartArea->UpdateSequenceArraySize

def ntfsFixup(usv, usa, buf):
    fixed=[]
    prev = 0
    i = 1
    while i < updateSequenceArraySize:
        pos = i * 512
        if buf[pos-2:pos] != usv:
            log.error('[i=%d,pos=%d] %r != %r' % (i, pos, usv, buf[pos-2:pos]))
            sys.exit(1)
        fixed.append(buf[prev:pos-2])
        fixed.append(usa[i-1])
        fixed.append(usa[i])
        prev = pos
        i += 1
    return ''.join(fixed)

def decode_page(pagebuf, remainder):
    if pagebuf[:4] == '\xff\xff\xff\xff': # End of file
        return
    if pagebuf[:4] != 'RCRD':
        log.error("Bad magic: %r" % pagebuf[:4])
        sys.exit(1)

    rcrd = ntfsFixup(pagebuf[0x28:0x28+2],
                     pagebuf[0x28:updateSequenceArrayOffset],
                     pagebuf)

    # PAGE_HEADER | UPDATE SEQUENCE ARRAY      | OPERATION RECORD HEADER
    # 0           0x28                         0x40

    offset = 0x40
    while offset+recordHeaderLength < len(rcrd):
        if offset % 8 != 0:
            log.error('a record header must be aligned on 64 bits (offset=%#x)' % offset)
            sys.exit(2)

        thisLsn = struct.unpack('<Q', rcrd[offset:offset+8])[0]
        clientPreviousLsn = struct.unpack('<Q', rcrd[offset+8:offset+8+8])[0]
        clientUndoNextLsn = struct.unpack('<Q', rcrd[offset+16:offset+16+8])[0]
        clientDataLength  = struct.unpack('<I', rcrd[offset+24:offset+24+4])[0]

        log.debug('thisLsn=%#d prev_lsn=%#d clientDataLength=%d' % (thisLsn, clientPreviousLsn, clientDataLength))

        if clientDataLength != 0:
            client_data = rcrd[offset+recordHeaderLength : offset+recordHeaderLength+clientDataLength]
            recordPageHeaderFlag = struct.unpack('<H', rcrd[offset+0x28 : offset+0x28+2])[0]
            if clientDataLength > len(rcrd) - offset:
                if recordPageHeaderFlag & 0x1 == 0:
                    log.warning('returning from loop, flags=%#x' % recordPageHeaderFlag)
                    #sys.exit(2)
                return remainder+client_data
            decode_lsn_record(remainder + client_data)
            remainder = ''
        offset += recordHeaderLength + clientDataLength
        offset += (8-offset) % 8
    return ''


def decode_lsn_record(buf):
    if len(buf) < 12:
        return
    redo_op  = struct.unpack('<H', buf[0:2])[0]
    undo_op  = struct.unpack('<H', buf[2:4])[0]
    redo_ofs  = struct.unpack('<H', buf[4:6])[0]
    redo_len  = struct.unpack('<H', buf[6:8])[0]
    undo_ofs  = struct.unpack('<H', buf[8:10])[0]
    undo_len  = struct.unpack('<H', buf[10:12])[0]

    log.debug('redo_ops=%s undo_op=%s redo_ofs=%#x redo_len=%d undo_ofs=%#x undo_len=%d' % (ops.get(redo_op, hex(redo_op)), ops.get(undo_op, hex(undo_op)), redo_ofs, redo_len, undo_ofs, undo_len))
    if redo_op > 0x22 or undo_op > 0x22:
        log.warning('Anormal redo_op or undo_op')
        #sys.exit(1)
    if redo_op == 0x02:
        r = ntfs.mft.MFT.MFTRecord(buf[redo_ofs:redo_ofs+redo_len], 0, False, need_fixup=False)
        log.debug(buf[redo_ofs:redo_ofs+redo_len].encode('hex'))
        fn = r.filename_information()
        if fn:
            print fn.filename()

def usage(ret=1):
    parser.print_help()
    sys.exit(ret)


if __name__ == '__main__':
    parser = OptionParser(usage=u'usage: %prog [options] $LogFile')
    parser.add_option('-v', '--verbose', dest='verbose', action="store_true",
                      default=False, help=u"Verbose mode")
    parser.add_option('-d', '--debug', dest='debug', action="store_true",
                      default=False, help=u"Debug mode")
    (options,args) = parser.parse_args()

    loglvl = logging.WARNING if options.verbose else logging.INFO
    loglvl = logging.DEBUG if options.debug else loglvl
    logging.basicConfig(level=loglvl,
                        format="%(asctime)s %(name)8s %(levelname)5s: %(message)s")
    log = logging.getLogger(sys.argv[0])

    f = open(args[0])
    buf = f.read(4096) # restart area
    buf = f.read(4096) # restart area
    remainder=''
    while True:
        buf = f.read(4096)
        if not buf:
            break
        remainder = decode_page(buf, remainder)

