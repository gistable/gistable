#!/usr/bin/env python
# coding: UTF-8

import socket
import struct

DEBUG = True
DEBUG2 = False

PTP_OC_GetDeviceInfo      = 0x1001
PTP_OC_OpenSession        = 0x1002
PTP_OC_CloseSession       = 0x1003
PTP_OC_GetStorageIDs      = 0x1004
PTP_OC_GetStorageInfo     = 0x1005
PTP_OC_GetNumObjects      = 0x1006
PTP_OC_GetObjectHandles   = 0x1007
PTP_OC_GetObjectInfo      = 0x1008
PTP_OC_GetObject          = 0x1009
PTP_OC_GetThumb           = 0x100A
PTP_OC_DeleteObject       = 0x100B
PTP_OC_InitiateCapture    = 0x100E
PTP_OC_GetDevicePropDesc  = 0x1014
PTP_OC_GetDevicePropValue = 0x1015
PTP_OC_SetDevicePropValue = 0x1016
PTP_OC_UnknownCommand     = 0x1022

PTP_RC_Undefined = 0x2000
PTP_RC_OK        = 0x2001

# Object Format Code
PTP_OFC_Undefined   = 0x3000
PTP_OFC_Association = 0x3001 
PTP_OFC_EXIF_JPEG   = 0x3801
PTP_OFC_JFIF        = 0x3808

PTP_EC_ObjectAdded       = 0x4002
PTP_EC_DevicePropChanged = 0x4006
PTP_EC_StoreFull         = 0x400a
PTP_EC_CaptureComplete   = 0x400d 

#==============================================================================
class PTP_IP(object):
    # -------------------------------------------------------------------------
    def __init__(self, host, name, GUID):
        '''Initialize'''
        self.host = host
        self.port = 15740
        self.name = name
        self.GUID = GUID
        self.command_sock = None
        self.event_sock = None

    # -------------------------------------------------------------------------
    def OpenConnection(self):
        # Init_Command
        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.command_sock.connect((self.host, self.port))
        except:
            print 'Connection Failed'
            return 0

        self.Send_InitCommandRequest(self.command_sock)
        result, self.session_id = self.Wait_InitCommandAck(self.command_sock)
        if result == 0:
            print 'InitCommandRequest failed'
            return 0

        print '(session_id = %d)' % self.session_id

        # Init_Event
        self.event_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.event_sock.connect((self.host, self.port))
        except:
            print 'Connection Failed'
            return 0

        self.Send_InitEventRequest(self.event_sock, self.session_id)
        result = self.Wait_InitEventAck(self.event_sock)
        if result == 0:
            print 'InitEventRequest failed'
            return 0

        self.transaction_id = 0

        return self.session_id

    # -------------------------------------------------------------------------
    def CloseConnection(self):
        if self.command_sock is not None:
            self.command_sock.close()
            self.command_sock = None

        if self.event_sock is not None:
            self.event_sock.close()
            self.event_sock = None

    # -------------------------------------------------------------------------
    def GetDeviceInfo(self):
        print 'PTP_OC_GetDeviceInfo'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_GetDeviceInfo)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'

    # -------------------------------------------------------------------------
    def OpenSession(self):
        print 'PTP_OC_OpenSession'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_OpenSession, self.session_id)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'
            return 0
        return 1

    # -------------------------------------------------------------------------
    def CloseSession(self):
        print 'PTP_OC_CloseSession'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_CloseSession)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'

    # -------------------------------------------------------------------------
    def GetStorageIDs(self):
        print 'PTP_OC_GetStorageIDs'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_GetStorageIDs)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'
            return []
        return self.unpackInt32Array(payload)

    # -------------------------------------------------------------------------
    def GetStorageInfo(self, storage_id):
        print 'PTP_OC_GetStorageInfo'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_GetStorageInfo, storage_id)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'

    # -------------------------------------------------------------------------
    def GetNumObjects(self, storage_id, obj_format = 0, parent_obj = 0):
        print 'PTP_OC_GetNumObjects'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_GetNumObjects,
                                    storage_id, obj_format, parent_obj)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'
            return 0
        return args[0]

    # -------------------------------------------------------------------------
    def GetObjectHandles(self, storage_id, obj_format = 0, parent_obj = 0):
        print 'PTP_OC_GetObjectHandles'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_GetObjectHandles,
                                    storage_id, obj_format, parent_obj)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'
            return []
        return self.unpackInt32Array(payload)

    # -------------------------------------------------------------------------
    def GetObjectInfo(self, obj_handle):
        print 'PTP_OC_GetObjectInfo'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_GetObjectInfo, obj_handle)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'
            return []
        # return payload
        return self.unpackObjectInfo(payload)

    # -------------------------------------------------------------------------
    def GetObject(self, obj_handle):
        print 'PTP_OC_GetObject'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_GetObject, obj_handle)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'
            return []
        return payload

    # -------------------------------------------------------------------------
    def GetThumb(self, obj_handle):
        print 'PTP_OC_GetThumb'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_GetThumb, obj_handle)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result != PTP_RC_OK:
            print 'Failed'
            return []
        return payload

    # -------------------------------------------------------------------------
    def SetDevicePropValue(self, prop_id, val):
        print 'PTP_OC_SetDevicePropValue'
        # payload = self.packInt16(val)
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    val, PTP_OC_SetDevicePropValue, prop_id)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result == 0:
            print 'Failed'
            return 0
        return 1

    # -------------------------------------------------------------------------
    def InitiateCapture(self):
        print 'Send PTP_OC_InitiateCapture'
        self.Send_PTPCommandRequest(self.command_sock, self.transaction_id,
                                    '', PTP_OC_InitiateCapture, 0, 0)
        self.transaction_id += 1
        result, args, payload = self.Wait_PTPCommandResponse(self.command_sock)
        if result == 0:
            print 'Failed'
            return 0

        print 'Wait PTP_EC_CaptureComplete'
        handle = 0
        for loop in range(0, 20):
            ptp_event, args = self.Wait_PTPEvent(self.event_sock)
            if ptp_event == PTP_EC_CaptureComplete:
                break
            elif ptp_event == PTP_EC_ObjectAdded:
                handle = args[0]

        return handle

    # -------------------------------------------------------------------------
    def Send_InitCommandRequest(self, sock):
        print 'Send InitCommandRequest'
        payload = ''
        payload += self.packGUID()
        payload += self.packString(self.name)
        payload += self.packInt32(1)

        self.sendCommand(sock, 1, payload)

    # -------------------------------------------------------------------------
    def Wait_InitCommandAck(self, sock):
        print 'Wait InitCommandAck'
        cmd_id, payload = self.recvResponse(sock)
        if cmd_id != 2:
            print 'failed'
            return 0, 0

        session_id = self.unpackInt32(payload[0:4])
        target_GUID = self.unpackGUID(payload[4:20])
        target_name = self.unpackString(payload[20:-4])
        # and unknown 4 bytes

        print 'Target GUID : %s' % target_GUID
        print 'Target Name : %s' % target_name

        return 1, session_id

    # -------------------------------------------------------------------------
    def Send_InitEventRequest(self, sock, session_id):
        print 'Send InitEventRequest'
        payload = ''
        payload += self.packInt32(session_id)

        self.sendCommand(sock, 3, payload)

    # -------------------------------------------------------------------------
    def Wait_InitEventAck(self, sock):
        print 'Wait InitEventAck'
        # sock.settimeout(10)
        cmd_id, payload = self.recvResponse(sock)
        if cmd_id != 4:
            print 'failed'
            return 0
        return 1

    # -------------------------------------------------------------------------
    def Send_PTPCommandRequest(self, sock, transaction_id,
                               ptp_payload, ptp_cmd, *args, **kwargs):
        # Cmd_Request
        payload = ''
        payload += self.packInt32(1)
        payload += self.packInt16(ptp_cmd)
        payload += self.packInt32(transaction_id)
        for arg in args:
            payload += self.packInt32(arg)
        self.sendCommand(sock, 6, payload)

        if ptp_payload == '':
            return

        # Start_Data_Packet
        payload = ''
        payload += self.packInt32(transaction_id)
        payload += self.packInt32(len(ptp_payload))
        payload += self.packInt32(0)
        self.sendCommand(sock, 9, payload)

        idx = 0
        next_idx = idx + 200
        while idx < len(ptp_payload):
            payload = ''
            payload += self.packInt32(transaction_id)
            payload += ptp_payload[idx:next_idx]
            if next_idx < len(ptp_payload):
                # Data_Packet
                self.sendCommand(sock, 10, payload)
            else:
                # End_Data_Packet
                self.sendCommand(sock, 12, payload)
            idx = next_idx
            next_idx += 200

    # -------------------------------------------------------------------------
    def Wait_PTPCommandResponse(self, sock):
        cmd_id, payload = self.recvResponse(sock)
        ptp_payload = ''
        if cmd_id == 9:
            # Start_Data_Packet
            transaction_id = self.unpackInt32(payload[0:4])
            ptp_payload_len = self.unpackInt32(payload[4:8])
            while True:
                # Data_Packet or End_Data_Packet
                cmd_id, payload = self.recvResponse(sock)
                if cmd_id != 10 and cmd_id != 12:
                    return 0, None, None
                temp_id = self.unpackInt32(payload[0:4])
                if temp_id != transaction_id:
                    return 0, None, None
                ptp_payload += payload[4:]
                if len(ptp_payload) >= ptp_payload_len or cmd_id == 12:
                    break
                if DEBUG:
                    print '.'
            # Cmd_Response
            cmd_id, payload = self.recvResponse(sock)

        if cmd_id != 7:
            return 0, None, None
        ptp_res = self.unpackInt16(payload[0:2])
        transaction_id = self.unpackInt32(payload[2:6])
        ptp_args = []
        idx = 6
        while idx < len(payload):
            ptp_args.append(self.unpackInt32(payload[idx:idx + 4]))
            idx += 4

        if DEBUG:
            print 'PTP Response: 0x%04X' % ptp_res
        if DEBUG2:
            self.printArgs(ptp_args)
            print '[Payl]',
            self.printPacket(ptp_payload)

        return ptp_res, ptp_args, ptp_payload

    # -------------------------------------------------------------------------
    def Wait_PTPEvent(self, sock):
        sock.settimeout(0.5)
        cmd_id, payload = self.recvResponse(sock)
        if cmd_id != 8:
            return 0, None
        # Event
        ptp_event = self.unpackInt16(payload[0:2])
        transaction_id = self.unpackInt32(payload[2:6])
        ptp_args = []
        idx = 6
        while idx < len(payload):
            ptp_args.append(self.unpackInt32(payload[idx:idx + 4]))
            idx += 4

        return ptp_event, ptp_args

    # -------------------------------------------------------------------------
    def sendCommand(self, sock, cmd_id, payload):
        packet = ''
        packet += self.packInt32(len(payload) + 8)
        packet += self.packInt32(cmd_id)
        packet += payload

        if DEBUG2:
            print '[SEND]',
            self.printPacket(packet)

        sock.send(packet)

    # -------------------------------------------------------------------------
    def recvResponse(self, sock):
        packet = ''
        # packet length
        try:
            recv_data = sock.recv(4)
        except:
            if DEBUG:
                print '.' # recv timeout
            return -1, None
        if recv_data is None or len(recv_data) != 4:
            return 0, None
        packet_len = self.unpackInt32(recv_data)
        if DEBUG2:
            print 'recv packet len = %d' % packet_len
        if packet_len < 8:
            return 0, None
        packet += recv_data

        # command
        try:
            recv_data = sock.recv(4)
        except:
            if DEBUG:
                print 'recv timeout, len=%d' % packet_len
            return -1, None
        if recv_data is None or len(recv_data) != 4:
            return 0, None
        cmd_id = self.unpackInt32(recv_data)
        if DEBUG2:
            print 'recv cmd id = %d' % cmd_id
        packet += recv_data

        # payload
        packet_len -= 8
        if packet_len == 0:
            recv_data = None
        else:
            try:
                recv_data = sock.recv(packet_len)
            except:
                if DEBUG:
                    print 'recv timeout, len=%d, cmd=%d' % (packet_len + 8,
                                                            cmd_id)
                    return -1, None
            if recv_data is None or len(recv_data) != packet_len:
                return 0, None
            packet += recv_data

        if DEBUG2:
            print '[RECV]',
            self.printPacket(packet)

        return cmd_id, recv_data

    # -------------------------------------------------------------------------
    def printPacket(self, packet):
        tab_idx = 1
        for ch in packet:
            print '%02X' % ord(ch),
            if (tab_idx % 8) == 0:
                print '\n      ',
            tab_idx += 1
        print ''

    # -------------------------------------------------------------------------
    def printArgs(self, args):
        print '%d ARGS' % len(args)
        idx = 0
        for arg in args:
            print '[ARGS %d] 0x%08X' % (idx, arg)
            idx += 1

    # -------------------------------------------------------------------------
    def packGUID(self):
        data = ''
        for val in self.GUID.split('-'):
            idx = 0
            while idx < len(val):
                data += chr(int(val[idx:idx + 2], 16))
                idx += 2
        return data

    # -------------------------------------------------------------------------
    def unpackGUID(self, packet):
        guid = ''
        idx = 0
        for ch in packet:
            if idx == 4 or idx == 6 or idx == 8 or idx == 10:
                guid += '-'
            guid += '%02x' % ord(ch)
            idx += 1
        return guid

    # -------------------------------------------------------------------------
    def packString(self, str):
        data = ''
        for ch in str:
            data += ch
            data += '\x00'
        data += '\x00'
        data += '\x00'
        return data

    # -------------------------------------------------------------------------
    def unpackString(self, packet):
        str = ''
        idx = 0
        for ch in packet:
            if (idx & 1) == 0:
                str += ch
            idx += 1
        return str

    # -------------------------------------------------------------------------
    def unpackInt32(self, payload):
        return struct.unpack('<I', payload)[0]

    # -------------------------------------------------------------------------
    def packInt32(self, val):
        return struct.pack('<I', val)

    # -------------------------------------------------------------------------
    def unpackInt16(self, payload):
        return struct.unpack('<H', payload)[0]

    # -------------------------------------------------------------------------
    def packInt16(self, val):
        if val < 0:
            val = 0x10000 + val
        return struct.pack('<H', val)

    # -------------------------------------------------------------------------
    def unpackInt32Array(self, payload):
        num_items = self.unpackInt32(payload[0:4])
        if num_items == 0 or (num_items * 4) > (len(payload) - 4):
            return []
        items = []
        idx = 4
        while idx < len(payload):
            items.append(self.unpackInt32(payload[idx:idx+4]))
            idx += 4
        return items

    # -------------------------------------------------------------------------
    def unpackPTPString(self, payload):
        len = ord(payload[0])
        if len == 0:
            return ''
        end = (len * 2 - 1)
        return self.unpackString(payload[1:end])

    # -------------------------------------------------------------------------
    def unpackObjectInfo(self, payload):
        info = {}
        info['StorageID'] = self.unpackInt32(payload[0:4])
        info['ObjectFormat'] = self.unpackInt16(payload[4:6])
        info['ProtectionStatus'] = self.unpackInt16(payload[6:8])
        info['ObjectCompressedSize'] = self.unpackInt32(payload[8:12])
        info['ThumbFormat'] = self.unpackInt16(payload[12:14])
        info['ThumbCompressedSize'] = self.unpackInt32(payload[14:18])
        info['ThumbPixWidth'] = self.unpackInt32(payload[18:22])
        info['ThumbPixHeight'] = self.unpackInt32(payload[22:26])
        info['ImagePixWidth'] = self.unpackInt32(payload[26:30])
        info['ImagePixHeight'] = self.unpackInt32(payload[30:34])
        info['ImageBitDepth'] = self.unpackInt32(payload[34:38])
        info['ParentObject'] = self.unpackInt32(payload[38:42])
        info['AssociationType'] = self.unpackInt16(payload[42:44])
        info['AssociationDesc'] = self.unpackInt32(payload[44:48])
        info['SequenceNumber'] = self.unpackInt32(payload[48:52])
        idx = 52
        info['Filename'] = self.unpackPTPString(payload[idx:])
        idx += ord(payload[idx]) * 2 + 1
        info['CaputureDate'] = self.unpackPTPString(payload[idx:])
        idx += ord(payload[idx]) * 2 + 1
        info['ModificationDate'] = self.unpackPTPString(payload[idx:])
        idx += ord(payload[idx]) * 2 + 1
        info['Keywords'] = self.unpackPTPString(payload[idx:])
        return info

#==============================================================================
class THETA360(PTP_IP):
    # -------------------------------------------------------------------------
    def __init__(self):
        '''Initialize'''
        PTP_IP.__init__(self, '192.168.1.1',
                        'THETA', '8a7ab04f-ebda-4f33-8649-8bf8c1cdc838')

    # -------------------------------------------------------------------------
    def open(self):
        if self.OpenConnection() == 0:
            # Failed to open connection
            return False
        if self.OpenSession() == 0:
            # Failed to open session
            return False
        return True

    # -------------------------------------------------------------------------
    def close(self):
        self.CloseSession()
        self.CloseConnection()

    # -------------------------------------------------------------------------
    # set EV shift
    # EV shift: 2000,1700,1300,1000,700,300,0,-300,-700,-1000,-1300,-1700,-2000
    def setEVShift(self, ev_shift):
        self.SetDevicePropValue(0x5010, self.packInt16(ev_shift))

    # -------------------------------------------------------------------------
    def shutter(self):
        self.InitiateCapture()

    # -------------------------------------------------------------------------
    def num_files(self):
        ids = self.GetStorageIDs()
        if len(ids) == 0:
            return 0
        return self.GetNumObjects(ids[0])

    # -------------------------------------------------------------------------
    def prepare(self):
        self.ids = self.GetStorageIDs()
        if len(self.ids) == 0:
            return 0
        self.handles = self.GetObjectHandles(self.ids[0])
        return len(self.handles)

    # -------------------------------------------------------------------------
    def get_info(self, idx):
        info = self.GetObjectInfo(self.handles[idx])
        if DEBUG:
            print 'filename: %s' % info['Filename']
            print 'object format: 0x%04X' % info['ObjectFormat']
            print 'object size: %d' % info['ObjectCompressedSize']
            print 'thumbnail size: %d' % info['ThumbCompressedSize']
            print 'seq. no.: %d' % info['SequenceNumber']
            print 'capture date: %s' % info['CaputureDate']
        return info

    # -------------------------------------------------------------------------
    def get_thumb(self, idx):
        return self.GetThumb(self.handles[idx])

    # -------------------------------------------------------------------------
    def get_object(self, idx):
        return self.GetObject(self.handles[idx])

    # -------------------------------------------------------------------------
    def write_local(self, filename, image):
        f = open(filename, 'wb')
        f.write(image)
        f.close()

#==============================================================================
def create():
    t = THETA360()
    t.open()
    return t

#==============================================================================
# Sample: shutter & download image to PC
if __name__ == '__main__':
    theta = THETA360()
    # DEBUG2 = True

    if theta.open() is True:
        # set EV shift
        #theta.setEVShift(-1000)

        theta.InitiateCapture()

        # set default EV shift
        #theta.setEVShift(0)

        # download image
        num_objs = theta.prepare()
        obj_idx = num_objs - 1
        obj_info = theta.get_info(obj_idx)
        image = theta.get_object(obj_idx)
        theta.write_local(obj_info['Filename'], image)
        print 'saved "%s"' % obj_info['Filename']

        theta.close()
