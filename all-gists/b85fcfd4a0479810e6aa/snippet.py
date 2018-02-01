import os.path
from Foundation import NSData, NSKeyedUnarchiver, SFLListItem, NSURL, NSMutableDictionary, NSKeyedArchiver, NSString, NSDictionary, NSArray

def load_favservers(sfl_path):
    if os.path.isfile(sfl_path):
        # File exists, use it
        sfl_decoded = NSKeyedUnarchiver.unarchiveObjectWithData_(NSData.dataWithContentsOfFile_(sfl_path))
    else:
        # File doesn't exist, make a blank template
        sfl_decoded = {u'items': [],
                       u'version': 1L,
                       u'properties': {"com.apple.LSSharedFileList.ForceTemplateIcons": False,},
                      }
    mutable_favs = dict(sfl_decoded)
    mutable_favs['items'] = list(mutable_favs['items'])
    return mutable_favs

def create_favitem(url=None, name=None):
    if name is None:
        # Make the display name the same as the URL by default
        name = url
    props = {NSString.stringWithString_('com.apple.LSSharedFileList.OverrideIcon.OSType'): NSString.stringWithString_(u'srvr')}
    props = NSDictionary.alloc().initWithDictionary_(props)
    return SFLListItem.alloc().initWithName_URL_properties_(name, NSURL.alloc().initWithString_(url), props)

def purify(obj):
    # This code ensures that certain data types are very definitely the ObjC versions
    d = dir(obj)
    if '__reversed__' in d:
        # list / NSArray
        return NSArray.alloc().initWithArray_(obj)
    elif 'items' in d:
        # dictionary / NSDictionary
        return NSDictionary.alloc().initWithDictionary_(obj)
    elif 'strip' in d:
        # string / NSString
        return NSString.alloc().initWithString_(obj)
    # Unhandled
    return obj

def save_favservers(favs, path):
    # Prior to running code through NSKeyedArchiver, we want to strip out custom pyObjC subclass types
    temp_keys = favs.keys()
    fixed_values = [purify(favs[x]) for x in temp_keys]
    fixed_keys   = [purify(x) for x in temp_keys]
    # Once everything is cleaned up, put it into a new NSDictionary
    formatted_favs = NSDictionary.alloc().initWithObjects_forKeys_(fixed_values, fixed_keys)
    return NSKeyedArchiver.archiveRootObject_toFile_(formatted_favs, path)

# How to use it
# -------------
# Pick the path:
sfl_path = os.path.expanduser('~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.FavoriteServers.sfl')
# Load it:
my_favs  = load_favservers(sfl_path)
# Make a new favorite:
new_fav  = create_favitem(url='smb://username@servername', name='A Cool Custom Name')
# Append it to the end:
my_favs['items'].append(new_fav)

# Saving back like this probably won't work if the user has the dialog open, so you'll want to
# do it at login with a tool like outset: https://github.com/chilcote/outset
# (The best time to do it would be when they're not logged in at all ...)
result = save_favservers(my_favs, sfl_path)