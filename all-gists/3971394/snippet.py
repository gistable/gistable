#!/usr/bin/env python2
# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; coding: utf-8; -*-

# usage:
#  $ cat /sys/devices/platform/mmc_host/mmcXXXX/mmcYYYY/csd | csdinfo
#
# reference:
#  'Physical Layer Simplified Specification Version 3.01'
#  https://www.sdcard.org/downloads/pls/simplified_specs/Part_1_Physical_Layer_Simplified_Specification_Ver_3.01_Final_100518.pdf


class CSDRegisterError(StandardError):
    pass


def bitslice(val, start, end):
    if start > end:
        (start, end) = (end, start)
        reverse = True
    else:
        reverse = False
    r = 0
    shift = 0
    for i in range(start, end+1):
        b = (val >> i) & 1
        if reverse:
            r |= b << shift
            shift += 1
        else:
            r <<= 1
            r |= b
    return r

class CSDRegisterBase(object):
    FIELD_MAP = {}
    def __init__(self, csd):
        self.csd = csd

    def read_field(self, field):
        slicer = self.FIELD_MAP[field]
        width = max(slicer) - min(slicer) + 1
        binary = bitslice(self.csd, slicer[0], slicer[1])
        return (binary, width)

# CardSpecificDataRegister Version 1.0:
class CSDRegister_V10(CSDRegisterBase):
    FIELD_MAP = {
        'CSD_STRUCTURE': (127, 126),
        'TAAC': (119, 112),
        'NSAC': (111, 104),
        'TRAN_SPEED': (103, 96),
        'CCC': (95, 84),
        'READ_BL_LEN': (83, 80),
        'READ_BL_PARTIAL': (79, 79),
        'WRITE_BLK_MISALIGN': (78, 78),
        'READ_BLK_MISALIGN': (77, 77),
        'DSR_IMP': (76, 76),
        'C_SIZE': (73, 62),
        'VDD_R_CURR_MIN': (61, 59),
        'VDD_R_CURR_MAX': (58, 56),
        'VDD_W_CURR_MIN': (55, 53),
        'VDD_W_CURR_MAX': (52, 50),
        'C_SIZE_MULT': (49, 47),
        'ERASE_BLK_EN': (46, 46),
        'SECTOR_SIZE': (45, 39),
        'WP_GRP_SIZE': (38, 32),
        'WP_GRP_ENABLE': (31, 31),
        'R2W_FACTOR': (28, 26),
        'WRITE_BL_LEN': (25, 22),
        'WRITE_BL_PARTIAL': (21, 21),
        'FILE_FORMAT_GRP': (15, 15),
        'COPY': (14, 14),
        'PERM_WRITE_PROTECT': (13, 13),
        'TMP_WRITE_PROTECT': (12, 12),
        'FILE_FORMAT': (11, 9),
        'CRC': (7, 1)
        }
    TIME_VALUE = ['reserved',
                  1.0, 1.2, 1.3, 1.5,
                  2.0, 2.5, 3.0, 3.5,
                  4.0, 4.5, 5.0, 5.5,
                  6.0, 7.0, 8.0]
    VDD_MIN = ['0.5mA', '1mA', '5mA', '10mA',
               '25mA', '35mA', '60mA', '100mA']
    VDD_MAX = ['1mA', '5mA', '10mA', '25mA',
               '35mA', '45mA', '80mA', '200mA']
    def __init__(self, csd):
        CSDRegisterBase.__init__(self, csd)

    @property
    def CSD_STRUCTURE(self):
        return self.read_field('CSD_STRUCTURE')

    @property
    def TAAC(self):
        return self.read_field('TAAC')

    @property
    def NSAC(self):
        return self.read_field('NSAC')

    @property
    def TRAN_SPEED(self):
        return self.read_field('TRAN_SPEED')

    @property
    def CCC(self):
        return self.read_field('CCC')

    @property
    def READ_BL_LEN(self):
        return self.read_field('READ_BL_LEN')

    @property
    def READ_BL_PARTIAL(self):
        return self.read_field('READ_BL_PARTIAL')

    @property
    def WRITE_BLK_MISALIGN(self):
        return self.read_field('WRITE_BLK_MISALIGN')

    @property
    def READ_BLK_MISALIGN(self):
        return self.read_field('READ_BLK_MISALIGN')

    @property
    def DSR_IMP(self):
        return self.read_field('DSR_IMP')

    @property
    def C_SIZE(self):
        return self.read_field('C_SIZE')

    @property
    def VDD_R_CURR_MIN(self):
        return self.read_field('VDD_R_CURR_MIN')

    @property
    def VDD_R_CURR_MAX(self):
        return self.read_field('VDD_R_CURR_MAX')

    @property
    def VDD_W_CURR_MIN(self):
        return self.read_field('VDD_W_CURR_MIN')

    @property
    def VDD_W_CURR_MAX(self):
        return self.read_field('VDD_W_CURR_MAX')


    @property
    def C_SIZE_MULT(self):
        return self.read_field('C_SIZE_MULT')

    @property
    def ERASE_BLK_EN(self):
        return self.read_field('ERASE_BLK_EN')

    @property
    def SECTOR_SIZE(self):
        return self.read_field('SECTOR_SIZE')

    @property
    def WP_GRP_SIZE(self):
        return self.read_field('WP_GRP_SIZE')

    @property
    def WP_GRP_ENABLE(self):
        return self.read_field('WP_GRP_ENABLE')

    @property
    def R2W_FACTOR(self):
        return self.read_field('R2W_FACTOR')

    @property
    def WRITE_BL_LEN(self):
        return self.read_field('WRITE_BL_LEN')

    @property
    def WRITE_BL_PARTIAL(self):
        return self.read_field('WRITE_BL_PARTIAL')

    @property
    def FILE_FORMAT_GRP(self):
        return self.read_field('FILE_FORMAT_GRP')

    @property
    def COPY(self):
        return self.read_field('COPY')

    @property
    def PERM_WRITE_PROTECT(self):
        return self.read_field('PERM_WRITE_PROTECT')

    @property
    def TMP_WRITE_PROTECT(self):
        return self.read_field('TMP_WRITE_PROTECT')

    @property
    def FILE_FORMAT(self):
        return self.read_field('FILE_FORMAT')

    @property
    def CRC(self):
        return self.read_field('CRC')

    @staticmethod
    def print_binary(v):
        print '  binary: 0b%s (0x%0x)' % (format(v[0], '0%db' % (v[1])),
                                          v[0])

    def report_CSD_STRUCTURE(self):
        v = self.CSD_STRUCTURE
        version = ['1.0', '2.0'][v[0]]
        print 'CSD structure'
        self.print_binary(v)
        print '  version: {0}'.format(version)

    def report_TAAC(self):
        v = self.TAAC
        time_unit_map = ['1ns', '10ns', '1us',
                         '10us', '1ms', '1ms', '10ms']
        time_unit = time_unit_map[bitslice(v[0], 2, 0)]
        time_value = self.TIME_VALUE[bitslice(v[0], 6, 3)]
        print 'TAAC: data read access-time'
        self.print_binary(v)
        print '  time unit: {0}'.format(time_unit)
        print '  time value: {0}'.format(time_value)

    def report_NSAC(self):
        v = self.NSAC
        clock = v[0] * 100
        print 'NSAC: worst case of data read access-time'
        self.print_binary(v)
        print '  data access time: {0} clock cycle'.format(clock)

    def report_TRAN_SPEED(self):
        v = self.TRAN_SPEED
        rate_unit_map = ['100 Kbit/s', '1Mbit/s',
                         '10Mbit/s', '100Mbit/s', 'reserved']
        rate_unit = rate_unit_map[bitslice(v[0], 2, 0)]
        time_value = self.TIME_VALUE[bitslice(v[0], 6, 3)]
        print 'TRAN_SPEED: max data transfer speed'
        self.print_binary(v)
        print '  transfer rate unit: {0}'.format(rate_unit)
        print '  time value: {0}'.format(time_value)

    def report_CCC(self):
        v = self.CCC
        cls = bitslice(v[0], 9, 9)
        print 'CCC: card command class'
        self.print_binary(v)
        print '  class {0}'.format(cls)

    def report_READ_BL_LEN(self):
        v = self.READ_BL_LEN
        print 'READ_BL_LEN: max read data block length'
        self.print_binary(v)
        print '  block length: {0} bytes'.format(2**v[0])

    def report_READ_BL_PARTIAL(self):
        v = self.READ_BL_PARTIAL
        print 'READ_BL_PARTIAL: partial blocks for read allowed'
        print '  allowed: {0}'.format(v[0])

    def report_WRITE_BLK_MISALIGN(self):
        v = self.WRITE_BLK_MISALIGN
        print 'WRITE_BLK_MISALIGN: write block misalignment'
        print '  allowed: {0}'.format(v[0])

    def report_READ_BLK_MISALIGN(self):
        v = self.READ_BLK_MISALIGN
        print 'READ_BLK_MISALIGN: read block misalignment'
        print '  allowed: {0}'.format(v[0])

    def report_DSR_IMP(self):
        v = self.DSR_IMP
        print 'DSR_IMP: driver stage register'
        print '  implemented: {0}'.format(v[0])

    def report_C_SIZE(self):
        v = self.C_SIZE
        print 'C_SIZE: value for compute card capacity'
        self.print_binary(v)
        print '  value: {0}'.format(v[0])

    def report_VDD_R_CURR_MIN(self):
        v = self.VDD_R_CURR_MIN
        print 'VDD_R_CURR_MIN: read current @VDD min'
        print '  ampere: {0}'.format(self.VDD_MIN[v[0]])

    def report_VDD_R_CURR_MAX(self):
        v = self.VDD_R_CURR_MAX
        print 'VDD_R_CURR_MAX: read current @VDD max'
        print '  ampere: {0}'.format(self.VDD_MAX[v[0]])

    def report_VDD_W_CURR_MIN(self):
        v = self.VDD_W_CURR_MIN
        print 'VDD_W_CURR_MIN: read current @VDD min'
        print '  ampere: {0}'.format(self.VDD_MIN[v[0]])

    def report_VDD_W_CURR_MAX(self):
        v = self.VDD_W_CURR_MAX
        print 'VDD_W_CURR_MAX: read current @VDD max'
        print '  ampere: {0}'.format(self.VDD_MAX[v[0]])

    def report_C_SIZE_MULT(self):
        v = self.C_SIZE_MULT
        mult = 2 ** (v[0] + 2)
        print 'C_SIZE_MULT: device size multiplier'
        print '  multiply: {0}'.format(mult)

    def report_ERASE_BLK_EN(self):
        v = self.ERASE_BLK_EN
        unit = 'SECTOR_SIZE' if v[0] else '512 bytes'
        print 'ERASE_BLK_EN: unit of the data to be erased'
        print '  unit: {0}'.format(unit)

    def report_SECTOR_SIZE(self):
        v = self.SECTOR_SIZE
        print 'SECTOR_SIZE: size of an erasable sector'
        print '  size: {0} block'.format(v[0] + 1)

    def report_WP_GRP_SIZE(self):
        v = self.WP_GRP_SIZE
        print 'WP_GRP_SIZE: the size of a write protected group'
        print '  size: {0} block'.format(v[0] + 1)

    def report_WP_GRP_ENABLE(self):
        v = self.WP_GRP_ENABLE
        print 'WP_GRP_ENABLE: write protect enabled'
        print '  enabled: {0}'.format(v[0])

    def report_R2W_FACTOR(self):
        v = self.R2W_FACTOR
        mult = 2 ** bitslice(v[0], 5, 0)
        print 'R2W_FACTOR: multiples of read access time'
        self.print_binary(v)
        print '  factor: {0}'.format(mult)

    def report_WRITE_BL_LEN(self):
        v = self.WRITE_BL_LEN
        length = 2 ** v[0]
        print 'WRITE_BL_LEN: max write data block length'
        self.print_binary(v)
        print '  length: {0} bytes'.format(length)

    def report_WRITE_BL_PARTIAL(self):
        v = self.WRITE_BL_PARTIAL
        print 'WRITE_BL_PARTIAL: partial block write allowed'
        print '  allowed: {0}'.format(v[0])

    def report_FILE_FORMAT_GRP(self):
        v = self.FILE_FORMAT_GRP
        print 'FILE_FORMAT_GRP: file format group'
        self.print_binary(v)

    def report_COPY(self):
        v = self.COPY
        print 'COPY: copy flag'
        print '  copied contents: {0}'.format(v[0])

    def report_PERM_WRITE_PROTECT(self):
        v = self.PERM_WRITE_PROTECT
        print 'PERM_WRITE_PROTECT: permanent write protection'
        print '  protect: {0}'.format(v[0])

    def report_TMP_WRITE_PROTECT(self):
        v = self.TMP_WRITE_PROTECT
        print 'TMP_WRITE_PROTECT: temporary write protection'
        print '  protect: {0}'.format(v[0])

    def report_FILE_FORMAT(self):
        v = self.FILE_FORMAT
        fmt_tbl = ['Hard disk-like file system with partition table',
                   'DOS FAT with boot sector only(no partition table)',
                   'Universal File Format',
                   'Others/Unknown']
        print 'FILE_FORMAT: file format'
        self.print_binary(v)
        print '  type: {0}'.format(fmt_tbl[v[0]])

    def report_CRC(self):
        v = self.CRC
        print 'CRC: check sum'
        self.print_binary(v)
        
    def report(self):
        print 'CSD Register Value: %032x' % (self.csd)
        self.report_CSD_STRUCTURE()
        self.report_TAAC()
        self.report_NSAC()
        self.report_TRAN_SPEED()
        self.report_CCC()
        self.report_READ_BL_LEN()
        self.report_READ_BL_PARTIAL()
        self.report_WRITE_BLK_MISALIGN()
        self.report_READ_BLK_MISALIGN()
        self.report_DSR_IMP()
        self.report_C_SIZE()
        self.report_VDD_R_CURR_MIN()
        self.report_VDD_R_CURR_MAX()
        self.report_VDD_W_CURR_MIN()
        self.report_VDD_W_CURR_MAX()
        self.report_C_SIZE_MULT()
        self.report_ERASE_BLK_EN()
        self.report_SECTOR_SIZE()
        self.report_WP_GRP_SIZE()
        self.report_WP_GRP_ENABLE()
        self.report_R2W_FACTOR()
        self.report_WRITE_BL_LEN()
        self.report_WRITE_BL_PARTIAL()
        self.report_FILE_FORMAT_GRP()
        self.report_COPY()
        self.report_PERM_WRITE_PROTECT()
        self.report_TMP_WRITE_PROTECT()
        self.report_FILE_FORMAT()
        self.report_CRC()

# CardSpecificDataRegister Version 2.0:
class CSDRegister_V20(CSDRegister_V10):
    FIELD_MAP = {
        'CSD_STRUCTURE': (127, 126),
        'TAAC': (119, 112),
        'NSAC': (111, 104),
        'TRAN_SPEED': (103, 96),
        'CCC': (95, 84),
        'READ_BL_LEN': (83, 80),
        'READ_BL_PARTIAL': (79, 79),
        'WRITE_BLK_MISALIGN': (78, 78),
        'READ_BLK_MISALIGN': (77, 77),
        'DSR_IMP': (76, 76),
        'C_SIZE': (69, 48),
        'ERASE_BLK_EN': (46, 46),
        'SECTOR_SIZE': (45, 39),
        'WP_GRP_SIZE': (38, 32),
        'WP_GRP_ENABLE': (31, 31),
        'R2W_FACTOR': (28, 26),
        'WRITE_BL_LEN': (25, 22),
        'WRITE_BL_PARTIAL': (21, 21),
        'FILE_FORMAT_GRP': (15, 15),
        'COPY': (14, 14),
        'PERM_WRITE_PROTECT': (13, 13),
        'TMP_WRITE_PROTECT': (12, 12),
        'FILE_FORMAT': (11, 9),
        'CRC': (7, 1)
        }
    def __init__(self, csd):
        CSDRegister_V10.__init__(self, csd)

    def report_C_SIZE(self):
        v = self.C_SIZE
        capacity = (v[0] + 1) * 512
        print 'C_SIZE: capacity'
        self.print_binary(v)
        print '  capacity: {0} Kbytes ({1} Mbytes)'.format(capacity, capacity/1024)

    def report(self):
        print 'CSD Register Value: %032x' % (self.csd)
        self.report_CSD_STRUCTURE()
        self.report_TAAC()
        self.report_NSAC()
        self.report_TRAN_SPEED()
        self.report_CCC()
        self.report_READ_BL_LEN()
        self.report_READ_BL_PARTIAL()
        self.report_WRITE_BLK_MISALIGN()
        self.report_READ_BLK_MISALIGN()
        self.report_DSR_IMP()
        self.report_C_SIZE()
        self.report_ERASE_BLK_EN()
        self.report_SECTOR_SIZE()
        self.report_WP_GRP_SIZE()
        self.report_WP_GRP_ENABLE()
        self.report_R2W_FACTOR()
        self.report_WRITE_BL_LEN()
        self.report_WRITE_BL_PARTIAL()
        self.report_FILE_FORMAT_GRP()
        self.report_COPY()
        self.report_PERM_WRITE_PROTECT()
        self.report_TMP_WRITE_PROTECT()
        self.report_FILE_FORMAT()
        self.report_CRC()

def CSDRegister(csd):
    if type(csd) == str:
        csd = long(csd, 16)
    assert type(csd) == long
    val = bitslice(csd, 127, 126)
    if val == 0:
        return CSDRegister_V10(csd)
    elif val == 1:
        return CSDRegister_V20(csd)
    else:
        raise CSDRegisterError()


if __name__ == '__main__':
    import sys
    s = sys.stdin.read()
    CSDRegister(s.split()[0]).report()



'''
output like:

CSD Register Value: 400e00325b5900003b377f800a404000
CSD structure
  binary: 0b01 (0x1)
  version: 2.0
TAAC: data read access-time
  binary: 0b00001110 (0xe)
  time unit: 10ms
  time value: 1.0
NSAC: worst case of data read access-time
  binary: 0b00000000 (0x0)
  data access time: 0 clock cycle
TRAN_SPEED: max data transfer speed
  binary: 0b00110010 (0x32)
  transfer rate unit: 10Mbit/s
  time value: 2.5
CCC: card command class
  binary: 0b010110110101 (0x5b5)
  class 0
READ_BL_LEN: max read data block length
  binary: 0b1001 (0x9)
  block length: 512 bytes
READ_BL_PARTIAL: partial blocks for read allowed
  allowed: 0
WRITE_BLK_MISALIGN: write block misalignment
  allowed: 0
READ_BLK_MISALIGN: read block misalignment
  allowed: 0
DSR_IMP: driver stage register
  implemented: 0
C_SIZE: capacity
  binary: 0b0000000011101100110111 (0x3b37)
  capacity: 7761920 Kbytes (7580 Mbytes)
ERASE_BLK_EN: unit of the data to be erased
  unit: SECTOR_SIZE
SECTOR_SIZE: size of an erasable sector
  size: 128 block
WP_GRP_SIZE: the size of a write protected group
  size: 1 block
WP_GRP_ENABLE: write protect enabled
  enabled: 0
R2W_FACTOR: multiples of read access time
  binary: 0b010 (0x2)
  factor: 4
WRITE_BL_LEN: max write data block length
  binary: 0b1001 (0x9)
  length: 512 bytes
WRITE_BL_PARTIAL: partial block write allowed
  allowed: 0
FILE_FORMAT_GRP: file format group
  binary: 0b0 (0x0)
COPY: copy flag
  copied contents: 1
PERM_WRITE_PROTECT: permanent write protection
  protect: 0
TMP_WRITE_PROTECT: temporary write protection
  protect: 0
FILE_FORMAT: file format
  binary: 0b000 (0x0)
  type: Hard disk-like file system with partition table
CRC: check sum
  binary: 0b0000000 (0x0)

'''

