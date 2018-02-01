#!/usr/bin/python

import socket
import struct
from protobuf import IpcConnectionContext_pb2 as IpcConnectionContext
from protobuf import RpcPayloadHeader_pb2 as RpcPayloadHeader

# --- Connection header ---
# Client.writeConnectionHeader()
preamble = (
            "hrpc"  # Server.HEADER
            "\7"    # Server.CURRENT_VERSION
            "P"     # AuthMethod.SIMPLE
            "\0"    # Server.IpcSerializationType.PROTOBUF
            )

protocol = "org.apache.hadoop.mapred.JobSubmissionProtocol"

# --- Connection context ---
# Client.writeConnectionContext()
context = IpcConnectionContext.IpcConnectionContextProto()
context.userInfo.effectiveUser = "tsuna"
context.protocol = protocol
context = context.SerializeToString()
hello = preamble + struct.pack(">I", len(context)) + context

# --- RPC ---
# Client.sendParam()
header = RpcPayloadHeader.RpcPayloadHeaderProto()
header.rpcKind = RpcPayloadHeader.RPC_WRITABLE
header.rpcOp = RpcPayloadHeader.RPC_FINAL_PAYLOAD
header.callId = 0
header = header.SerializeToString()
assert len(header) <= 127, repr(header)
header = chr(len(header)) + header

# --- Payload ---
# Because we chose RPC_WRITABLE, our payload is a WritableRpcEngine$Invocation.
writableRpcVersion = 2
payload = struct.pack(">Q", writableRpcVersion)  # 8 bytes, lolz
payload += struct.pack(">H", len(protocol)) + protocol
method = "getAllJobs"
payload += struct.pack(">H", len(method)) + method
clientVersion = 28
payload += struct.pack(">Q", clientVersion)  # 8 bytes again, lolz again
clientMethodsHash = 0xDEADBEEF  # Unused crap
payload += struct.pack(">I", clientMethodsHash)
numParams = 0
payload += struct.pack(">I", numParams)

payload = header + payload
rpc = struct.pack(">I", len(payload)) + payload

sock = socket.socket()
sock.connect(("127.0.0.1", 8021))
sock.sendall(hello + rpc)
print repr(sock.recv(4096))  # TBD: read output properly and deserialize it