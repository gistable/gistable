# k`sOSe - detect SSDT hooks

import ctypes
import struct
from ctypes.wintypes import *
from ctypes import windll

SYSCALLS = [
	"NtAcceptConnectPort",
	"NtAccessCheck",
	"NtAccessCheckAndAuditAlarm",
	"NtAccessCheckByType",
	"NtAccessCheckByTypeAndAuditAlarm",
	"NtAccessCheckByTypeResultList",
	"NtAccessCheckByTypeResultListAndAuditAlarm",
	"NtAccessCheckByTypeResultListAndAuditAlarmByHandle",
	"NtAddAtom",
	"NtQueryBootOptions",
	"NtAdjustGroupsToken",
	"NtAdjustPrivilegesToken",
	"NtAlertResumeThread",
	"NtAlertThread",
	"NtAllocateLocallyUniqueId",
	"NtAllocateUserPhysicalPages",
	"NtAllocateUuids",
	"NtAllocateVirtualMemory",
	"NtAreMappedFilesTheSame",
	"NtAssignProcessToJobObject",
	"NtCallbackReturn",
	"NtModifyBootEntry",
	"NtCancelIoFile",
	"NtCancelTimer",
	"NtClearEvent",
	"NtClose",
	"NtCloseObjectAuditAlarm",
	"NtCompactKeys",
	"NtCompareTokens",
	"NtCompleteConnectPort",
	"NtCompressKey",
	"NtConnectPort",
	"NtContinue",
	"NtCreateDebugObject",
	"NtCreateDirectoryObject",
	"NtCreateEvent",
	"NtCreateEventPair",
	"NtCreateFile",
	"NtCreateIoCompletion",
	"NtCreateJobObject",
	"NtCreateJobSet",
	"NtCreateKey",
	"NtCreateMailslotFile",
	"NtCreateMutant",
	"NtCreateNamedPipeFile",
	"NtCreatePagingFile",
	"NtCreatePort",
	"NtCreateProcess",
	"NtCreateProcessEx",
	"NtCreateProfile",
	"NtCreateSection",
	"NtCreateSemaphore",
	"NtCreateSymbolicLinkObject",
	"NtCreateThread",
	"NtCreateTimer",
	"NtCreateToken",
	"NtCreateWaitablePort",
	"NtDebugActiveProcess",
	"NtDebugContinue",
	"NtDelayExecution",
	"NtDeleteAtom",
	"NtModifyBootEntry",
	"NtDeleteFile",
	"NtDeleteKey",
	"NtDeleteObjectAuditAlarm",
	"NtDeleteValueKey",
	"NtDeviceIoControlFile",
	"NtDisplayString",
	"NtDuplicateObject",
	"NtDuplicateToken",
	"NtQueryBootOptions",
	"NtEnumerateKey",
	"NtEnumerateSystemEnvironmentValuesEx",
	"NtEnumerateValueKey",
	"NtExtendSection",
	"NtFilterToken",
	"NtFindAtom",
	"NtFlushBuffersFile",
	"NtFlushInstructionCache",
	"NtFlushKey",
	"NtFlushVirtualMemory",
	"NtFlushWriteBuffer",
	"NtFreeUserPhysicalPages",
	"NtFreeVirtualMemory",
	"NtFsControlFile",
	"NtGetContextThread",
	"NtGetDevicePowerState",
	"NtGetPlugPlayEvent",
	"NtGetWriteWatch",
	"NtImpersonateAnonymousToken",
	"NtImpersonateClientOfPort",
	"NtImpersonateThread",
	"NtInitializeRegistry",
	"NtInitiatePowerAction",
	"NtIsProcessInJob",
	"NtIsSystemResumeAutomatic",
	"NtListenPort",
	"NtLoadDriver",
	"NtLoadKey",
	"NtLoadKey2",
	"NtLockFile",
	"NtLockProductActivationKeys",
	"NtLockRegistryKey",
	"NtLockVirtualMemory",
	"NtMakePermanentObject",
	"NtMakeTemporaryObject",
	"NtMapUserPhysicalPages",
	"NtMapUserPhysicalPagesScatter",
	"NtMapViewOfSection",
	"NtModifyBootEntry",
	"NtNotifyChangeDirectoryFile",
	"NtNotifyChangeKey",
	"NtNotifyChangeMultipleKeys",
	"NtOpenDirectoryObject",
	"NtOpenEvent",
	"NtOpenEventPair",
	"NtOpenFile",
	"NtOpenIoCompletion",
	"NtOpenJobObject",
	"NtOpenKey",
	"NtOpenMutant",
	"NtOpenObjectAuditAlarm",
	"NtOpenProcess",
	"NtOpenProcessToken",
	"NtOpenProcessTokenEx",
	"NtOpenSection",
	"NtOpenSemaphore",
	"NtOpenSymbolicLinkObject",
	"NtOpenThread",
	"NtOpenThreadToken",
	"NtOpenThreadTokenEx",
	"NtOpenTimer",
	"NtPlugPlayControl",
	"NtPowerInformation",
	"NtPrivilegeCheck",
	"NtPrivilegeObjectAuditAlarm",
	"NtPrivilegedServiceAuditAlarm",
	"NtProtectVirtualMemory",
	"NtPulseEvent",
	"NtQueryAttributesFile",
	"NtQueryBootOptions",
	"NtQueryBootOptions",
	"NtQueryDebugFilterState",
	"NtQueryDefaultLocale",
	"NtQueryDefaultUILanguage",
	"NtQueryDirectoryFile",
	"NtQueryDirectoryObject",
	"NtQueryEaFile",
	"NtQueryEvent",
	"NtQueryFullAttributesFile",
	"NtQueryInformationAtom",
	"NtQueryInformationFile",
	"NtQueryInformationJobObject",
	"NtQueryInformationPort",
	"NtQueryInformationProcess",
	"NtQueryInformationThread",
	"NtQueryInformationToken",
	"NtQueryInstallUILanguage",
	"NtQueryIntervalProfile",
	"NtQueryIoCompletion",
	"NtQueryKey",
	"NtQueryMultipleValueKey",
	"NtQueryMutant",
	"NtQueryObject",
	"NtQueryOpenSubKeys",
	"NtQueryPerformanceCounter",
	"NtQueryQuotaInformationFile",
	"NtQuerySection",
	"NtQuerySecurityObject",
	"NtQuerySemaphore",
	"NtQuerySymbolicLinkObject",
	"NtQuerySystemEnvironmentValue",
	"NtQuerySystemEnvironmentValueEx",
	"NtQuerySystemInformation",
	"NtQuerySystemTime",
	"NtQueryTimer",
	"NtQueryTimerResolution",
	"NtQueryValueKey",
	"NtQueryVirtualMemory",
	"NtQueryVolumeInformationFile",
	"NtQueueApcThread",
	"NtRaiseException",
	"NtRaiseHardError",
	"NtReadFile",
	"NtReadFileScatter",
	"NtReadRequestData",
	"NtReadVirtualMemory",
	"NtRegisterThreadTerminatePort",
	"NtReleaseMutant",
	"NtReleaseSemaphore",
	"NtRemoveIoCompletion",
	"NtRemoveProcessDebug",
	"NtRenameKey",
	"NtReplaceKey",
	"NtReplyPort",
	"NtReplyWaitReceivePort",
	"NtReplyWaitReceivePortEx",
	"NtReplyWaitReplyPort",
	"NtRequestDeviceWakeup",
	"NtRequestPort",
	"NtRequestWaitReplyPort",
	"NtRequestWakeupLatency",
	"NtResetEvent",
	"NtResetWriteWatch",
	"NtRestoreKey",
	"NtResumeProcess",
	"NtResumeThread",
	"NtSaveKey",
	"NtSaveKeyEx",
	"NtSaveMergedKeys",
	"NtSecureConnectPort",
	"NtQueryBootOptions",
	"NtQueryBootOptions",
	"NtSetContextThread",
	"NtSetDebugFilterState",
	"NtSetDefaultHardErrorPort",
	"NtSetDefaultLocale",
	"NtSetDefaultUILanguage",
	"NtSetEaFile",
	"NtSetEvent",
	"NtSetEventBoostPriority",
	"NtSetHighEventPair",
	"NtSetHighWaitLowEventPair",
	"NtSetInformationDebugObject",
	"NtSetInformationFile",
	"NtSetInformationJobObject",
	"NtSetInformationKey",
	"NtSetInformationObject",
	"NtSetInformationProcess",
	"NtSetInformationThread",
	"NtSetInformationToken",
	"NtSetIntervalProfile",
	"NtSetIoCompletion",
	"NtSetLdtEntries",
	"NtSetLowEventPair",
	"NtSetLowWaitHighEventPair",
	"NtSetQuotaInformationFile",
	"NtSetSecurityObject",
	"NtSetSystemEnvironmentValue",
	"NtQuerySystemEnvironmentValueEx",
	"NtSetSystemInformation",
	"NtSetSystemPowerState",
	"NtSetSystemTime",
	"NtSetThreadExecutionState",
	"NtSetTimer",
	"NtSetTimerResolution",
	"NtSetUuidSeed",
	"NtSetValueKey",
	"NtSetVolumeInformationFile",
	"NtShutdownSystem",
	"NtSignalAndWaitForSingleObject",
	"NtStartProfile",
	"NtStopProfile",
	"NtSuspendProcess",
	"NtSuspendThread",
	"NtSystemDebugControl",
	"NtTerminateJobObject",
	"NtTerminateProcess",
	"NtTerminateThread",
	"NtTestAlert",
	"NtTraceEvent",
	"NtTranslateFilePath",
	"NtUnloadDriver",
	"NtUnloadKey",
	"NtUnloadKeyEx",
	"NtUnlockFile",
	"NtUnlockVirtualMemory",
	"NtUnmapViewOfSection",
	"NtVdmControl",
	"NtWaitForDebugEvent",
	"NtWaitForMultipleObjects",
	"NtWaitForSingleObject",
	"NtWaitHighEventPair",
	"NtWaitLowEventPair",
	"NtWriteFile",
	"NtWriteFileGather",
	"NtWriteRequestData",
	"NtWriteVirtualMemory",
	"NtYieldExecution",
	"NtCreateKeyedEvent",
	"NtOpenKeyedEvent",
	"NtReleaseKeyedEvent",
	"NtWaitForKeyedEvent",
	"NtQueryPortInformationProcess"
]

class SYSDBG_PACKET(ctypes.Structure):
	_fields_ = (
		("Address",		ctypes.c_void_p),
		("Buffer",		ctypes.c_void_p),
		("BufferLen",		ULONG)
	)

class SYSTEM_MODULE_INFORMATION(ctypes.Structure):
	_fields_ = (
		("ModuleCount",		ULONG),
		("WhoCares",		ctypes.c_void_p * 2),
		("BaseAddress",		ctypes.c_void_p),
		("Size",		ULONG),
		("MoarStuff",		ULONG),
		("MoarMoar",		USHORT),
		("HeyThere",		USHORT),
		("Pwned",		USHORT),
		("W00t",		USHORT),
		("ImageName",		ctypes.c_char_p * 256)
	)

class TOKEN_PRIVS(ctypes.Structure):
	_fields_ = (
		("PrivilegeCount",	ULONG),
		("Privileges",		ULONG * 3)
	)


def get_debug_privs():
	token = HANDLE()
	windll.advapi32.OpenProcessToken(windll.kernel32.GetCurrentProcess(), 0x00000020, ctypes.byref(token))
	privs = TOKEN_PRIVS()
	privs.PrivilegeCount = 1
	privs.Privileges = (0x14, 0, 2) 
	windll.advapi32.AdjustTokenPrivileges(token, 0, ctypes.byref(privs), 0, 0, 0)
	windll.kernel32.CloseHandle(token)

def get_sdt_rva():
	ntos_handle = windll.kernel32.LoadLibraryA("ntoskrnl.exe")
	return windll.kernel32.GetProcAddress(ntos_handle, "KeServiceDescriptorTable") - ntos_handle

def get_kernel_addr():
	buffer_size = ULONG(0)
	windll.ntdll.ZwQuerySystemInformation(11, 0, 0, ctypes.byref(buffer_size));
	
	sysmod_info = ctypes.create_string_buffer(buffer_size.value)
	windll.ntdll.ZwQuerySystemInformation(11, ctypes.byref(sysmod_info), buffer_size.value, ctypes.byref(buffer_size));
	
	mod_list = ctypes.cast(sysmod_info, ctypes.POINTER(SYSTEM_MODULE_INFORMATION))
	return (mod_list[0].BaseAddress, mod_list[0].BaseAddress + mod_list[0].Size)

def kernel_read(addr, size):
	sysdbg_packet = SYSDBG_PACKET()
	sysdbg_packet.Address = addr
	if size == 4:
		buff = ULONG()
	else:
		buff = ctypes.create_string_buffer(size)

	sysdbg_packet.Buffer = ctypes.cast(ctypes.byref(buff), ctypes.c_void_p)
	sysdbg_packet.BufferLen = size 
	windll.ntdll.ZwSystemDebugControl(8, ctypes.byref(sysdbg_packet), ctypes.sizeof(SYSDBG_PACKET), 0, 0, 0)

	return buff
	
def get_ssdt():
	ssdt_ptr = kernel_read(kernel_start + get_sdt_rva(), 4)
	ssdt_size = kernel_read(kernel_start + get_sdt_rva() + 8, 4)

	return (ssdt_ptr.value, ssdt_size.value)

get_debug_privs()
(kernel_start, kernel_end) = get_kernel_addr()
print "[+] Got kernel @ 0x%08x => 0x%08x" % (kernel_start, kernel_end)

(ssdt_ptr, ssdt_size) = get_ssdt()
print "[+] Got SSDT @ 0x%08x, entries: 0x%04x" % (ssdt_ptr, ssdt_size)

ssdt = kernel_read(ssdt_ptr, ssdt_size*4)

offset = 0
while offset < ssdt_size*4:
	address = struct.unpack('<L', ssdt[offset:offset+4])[0]
	if address > kernel_end or address < kernel_start:
		try:
			syscall = SYSCALLS[offset/4]
		except:
			syscall = "syscall_id_%02x" % (offset/4)

		print "[*] Hooked %s => 0x%08x" % (syscall, address)
	offset += 4
