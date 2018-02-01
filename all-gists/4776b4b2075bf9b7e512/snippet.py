from Foundation import NSKeyedUnarchiver
from struct import unpack

# This entire function is black magic of the highest order and I'll blog about it later
def extract_share(bookmark_data):
    content_offset, = unpack('I', bookmark_data[12:16])
    first_TOC, = unpack('I', bookmark_data[content_offset:content_offset+4])
    first_TOC += content_offset
    TOC_len, rec_type, level, next_TOC, record_count = unpack('IIIII', bookmark_data[first_TOC:first_TOC+20])
    TOC_cursor = first_TOC + 20
    record_offsets = {}
    for i in range(record_count):
        record_id, offset = unpack('<IQ', bookmark_data[TOC_cursor:TOC_cursor+12])
        record_offsets[record_id] = offset + content_offset
        TOC_cursor += 12
    mount_record = record_offsets.get(0x2050, None)
    # Check to see if we actually had a volMountURL record
    if mount_record is not None:
        mount_length, rec_type = unpack('II', bookmark_data[mount_record:mount_record+8])
        mount_record += 8
        mount_URL = (bookmark_data[mount_record:mount_record+mount_length]).decode('utf-8')
        return mount_URL
    else:
        return None

def get_recentservers(sfl_file_path):
    # Read the com.apple.LSSharedFileList.RecentServers.sfl file (located in ~/Library/Application Support/com.apple.sharedfilelist on 10.11+)
    with open(sfl_file_path, 'rb') as f:
        raw_data = f.read()
    # It's NSKeyedArchiver data - let's decode it!
    recent_servers = NSKeyedUnarchiver.unarchiveObjectWithData_(buffer(raw_data))
    # Build an empty set
    server_URLs = []
    # Add in our discovered server URLs from the SFLListItems and return in 'SFLListItem.order' order
    for x in sorted(recent_servers['items'], lambda y,_: int(y.order())):
        url = extract_share(x.bookmark()[:].tobytes())
        if url is not None:
            server_URLs.append(url)
    return server_URLs

# Example usage:
# get_recentservers('com.apple.LSSharedFileList.RecentServers.sfl')