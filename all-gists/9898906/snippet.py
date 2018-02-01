# first get the disks...

disks = [d for d in vm.config.hardware.device
         if isinstance(d, pyVmomi.vim.vm.device.VirtualDisk) and
         isinstance(d.backing, pyVmomi.vim.vm.device.VirtualDisk.RawDiskMappingVer1BackingInfo)]
print d.deviceInfo.deviceName

# then later

ss = vm.runtime.host.configManager.storageSystem
for d in disks:
    try:
        lun = [l for l in ss.storageDeviceInfo.scsiLun
               if d.deviceName == l.deviceName][0]
        print d.deviceInfo.label, lun.canonicalName
    except IndexError:
        print 'Disk not found'
