# This code leverages the pre-existing XML parser in objc but takes just the constant values
# without any deeper parsing of classes, structs, etc.

# Useful for when objc.loadBundleVariables as used here https://gist.github.com/pudquick/ac8f22326f095ed2690e
# is not possible because the constant isn't defined as a framework symbol, only in a header
# (which the System .bridgesupport files helpfully included entries for)

import objc

def constant_loader(framework_bridgesupport_path, target_dict, values = None):
    with open(framework_bridgesupport_path, 'r') as f:
        xml = f.read()
        prs = objc._bridgesupport._BridgeSupportParser(xml, 'no path necessary for constants')
        if values is None:
            target_dict.update(prs.values)
        else:
            for k in values:
                if prs.values.has_key(k):
                    target_dict[k] = prs.values[k]

# Example usage:
# constant_loader('/System/Library/Frameworks/IOKit.framework/Resources/BridgeSupport/IOKit.bridgesupport', globals(), ['kIOMediaClass'])
# >>> kIOMediaClass
# 'IOMedia'
