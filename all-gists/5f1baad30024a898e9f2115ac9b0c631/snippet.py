import objc
from Foundation import NSBundle

# Predefine some opaque types
DASessionRef = objc.createOpaquePointerType('DASessionRef', '^{__DASession=}', None)
DADiskRef    = objc.createOpaquePointerType('DADiskRef',    '^{__DADisk=}',    None)

# Load DiskManagement framework classes
DiskManagment = objc.loadBundle('DiskManagment', globals(), bundle_path='/System/Library/PrivateFrameworks/DiskManagement.framework')

# Load DiskArbitration framework functions
DiskArbitration_bundle = NSBundle.bundleWithIdentifier_('com.apple.DiskArbitration')
functions = [
             ('DASessionCreate',  '@o@'),
             ('DADiskGetBSDName', '*^{__DADisk=}'),
            ]
objc.loadBundleFunctions(DiskArbitration_bundle, globals(), functions)

class diskRef(object):
    def __init__(self, dObj, controller, rawRef=False):
        if rawRef:
            self.cf_type    = objc.objc_object(c_void_p=dObj.__pointer__)
            self.ref_type   = dObj
        else:
            self.cf_type    = dObj
            self.ref_type   = DADiskRef(c_void_p=(dObj.__c_void_p__().value))
        self.controller = controller
    def __repr__(self):
        return self.cf_type.__repr__()
    @property
    def devname(self):
        return self.controller.shared.deviceNodeForDisk_error_(self.ref_type, None)
    @property
    def volname(self):
        return self.controller.shared.volumeNameForDisk_error_(self.ref_type, None)
    @property
    def type(self):
        return self.controller.shared.ioContentOfDisk_error_(self.ref_type, None)
    @property
    def facts(self):
        possible = [x for x in dir(self.controller.shared) if (x.startswith('is') and x.endswith('_error_'))]
        return [y for y in sorted([x.split('is',1)[-1].rsplit('_error_',1)[0] for x in possible]) if not '_' in y]
    @property
    def physical_store(self):
        # This APFS and other disk types as well supposedly, looking at the code - like CoreStorage, SoftRAID ....
        try:
            results = self.controller.shared.physicalDisksForDisk_storageSystemName_error_(self.ref_type, None, None)
            if results[0] is not None:
                return diskRef(results[0], self.controller)
        except:
            pass
        return None
    def Is(self, factname):
        if factname not in self.facts:
            raise Exception('no such fact, check disk.facts')
        selector = getattr(self.controller.shared, 'is' + factname + '_error_', None)
        if selector is None:
            raise Exception('no such fact, check disk.facts')
        return (selector)(self.ref_type,None)

class diskList(object):
    # This is dict-list hybrid that allows for slicing as well as lookups by dev name
    def __init__(self, disks):
        self._disk_list = disks[:]
        self._disk_dict = dict()
        for i,d in enumerate(disks):
            self._disk_dict[d.devname] = d
    def __iter__(self):
        return iter(self._disk_list)
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._disk_list.__getitem__(index)
        elif isinstance(index, int):
            return self._disk_list.__getitem__(index)
        elif isinstance(index, diskRef):
            # someone passed in a disk, so .. give them back the disk?
            return index
        return self._disk_dict[index]
    def __repr__(self):
        return self._disk_list.__repr__()

class diskManager(object):
    def setup_managers(self):
        # Create a DiskArb session
        session = DASessionCreate(None)
        # Get the shared disk manager
        self.shared = DMManager.sharedManager()
        session_p = DASessionRef(c_void_p=(session.__c_void_p__().value))
        # connect the DA session
        self.shared.setDefaultDASession_(session_p)
        self.shared.setLanguage_('English')
        # init the CS manager
        self.shared_cs = DMCoreStorage.alloc().initWithManager_(self.shared)
    def __init__(self):
        self.shared = None
        self.shared_cs = None
        self.setup_managers()
    def _formatted_disks(self, disk_list):
        all_disks = sorted([diskRef(d, self) for d in disk_list], key=lambda x: x.devname)
        return diskList(all_disks)
    @property
    def topLevelDisks(self):
        return self._formatted_disks(self.shared.topLevelDisks())
    @property
    def disks(self):
        return self._formatted_disks(self.shared.disks())
    def diskForPath(self, path):
        return diskRef(self.shared.diskForPath_error_(path, None), self, rawRef=True)

# Example usage
#
# from diskman import diskManager
# dm = diskManager()
# 
# >>> dm.disks
# [<DADisk 0x7fd748434520 [0x7fff7c0b1440]>{id = /dev/disk0}, <DADisk 0x7fd748434550 [0x7fff7c0b1440]>{id = /dev/disk0s1}, ...
# 
# >>> dm.diskForPath('/')
# <DADisk 0x7fa041c1a180 [0x7fff7c0b1440]>{id = /dev/disk1}
# 
# >>> dm.diskForPath('/').volname
# u'Macintosh HD'
# 
# >>> dm.diskForPath('/').devname
# u'/dev/disk1'
# 
# >>> dm.disks['/dev/disk1'].facts
# ['AppleDiskImage', 'AppleRAIDDisk', 'AppleRAIDMemberDisk', 'AppleRAIDSetDisk', 'AppleRAIDSpareDisk', 'AppleRAIDUUID', ...
# 
# >>> dm.disks['/dev/disk1'].Is('EjectableDisk')
# 0
#
# >>> dm.disks['/dev/disk1'].Is('InternalDisk')
# 1
