# Only tested on OSX 10.11.5

import objc
from Foundation import NSBundle
Metadata_bundle = NSBundle.bundleWithIdentifier_('com.apple.Metadata')

functions = [
             ('_MDCopyExclusionList', '@'),
             ('_MDSetExclusion', '@@I'),
            ]

objc.loadBundleFunctions(Metadata_bundle, globals(), functions)

# get the current exclusions (returns list of path strings)
current_exclusions = _MDCopyExclusionList()

# add an exclusion for a path
result = _MDSetExclusion('/Path/We/Want/To/Exclude', 1)

# remove an exclusion for a path
result = _MDSetExclusion('/Path/We/No/Longer/Want/To/Exclude', 0)
