import objc
packagekit_bundle = objc.loadBundle('PackageKit', module_globals=globals(), bundle_path='/System/Library/PrivateFrameworks/PackageKit.framework', scan_classes=False)
PKReceipt = objc.lookUpClass('PKReceipt')

receipts = PKReceipt.receiptsOnVolumeAtPath_('/')

first_receipt = receipts[0]

# Things you can look up:
# installPrefixPath
# installProcessName
# installDate
# packageVersion
# packageIdentifier
# description
# receiptStoragePaths
# packageGroups

# >>> first_receipt.packageVersion()
# u'10.11.4.1.1.1457768702'

# Direct access to the BOM for the package receipt
# >>> bom = first_receipt._BOM()
# >>> e = bom.directoryEnumerator()
# >>> e.nextObject()
# u'System'
# >>> e.nextObject()
# u'System/Library'
# >>> e.nextObject()
# u'System/Library/CoreServices'
# >>> e.nextObject()
# u'System/Library/CoreServices/SystemVersion.plist'
# [...]
