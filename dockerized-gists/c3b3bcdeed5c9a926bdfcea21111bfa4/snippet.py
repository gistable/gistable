import posixpath, urlparse, urllib2, re, ast, struct, cmd, os, os.path
import xml.etree.ElementTree as ET

def discover_roms(rom_url):
    # step 1: based on the URL, download the _files.xml for the details
    # I could do this a lot easier, but this is more fun
    url_parts = urlparse.urlsplit(rom_url)
    base_path, page_path = posixpath.split(url_parts.path)
    files_path = posixpath.join(url_parts.path, page_path + '_files.xml')
    new_parts  = url_parts._replace(path=files_path)
    xml_url    = urlparse.urlunsplit(new_parts)
    # download it
    f = urllib2.urlopen(xml_url)
    files_xml = f.read()
    f.close()
    # step 2: parse the XML, looking for a large multi-part zip
    root = ET.fromstring(files_xml)
    zips = dict()
    for child in root:
        if child.get('source') == 'original':
            # if it's part of the real content
            m = re.match('^(.+)\.(?:zip|z[0-9]{2})$', child.get('name')) 
            if m:
                # It's a file of the form .zip, .z01, .z02, etc.
                group_name = m.group(1)
                file_name  = m.group(0)
                file_size  = ast.literal_eval(child.find('size').text)
                # record the results
                zips[group_name] = zips.get(group_name, dict())
                zips[group_name]['size']  = zips[group_name].get('size', 0) + file_size
                zips[group_name]['files'] = zips[group_name].get('files', list()) + [(file_name, file_size)]
    # step 3: select the largest file group
    rom_archive, archive_info = sorted(zips.items(), key=lambda x: x[1]['size'], reverse=True)[0]
    total_size    = archive_info['size']
    # This should sort into: .z01, .z02, [...], .zip order
    archive_files = sorted(archive_info['files'], key=lambda x: x[0])
    # step 4: grab the last 200k of the final .zip file, which should be enough to contain the end of the central directory
    #         since the max size is a 2 byte / 16-bit value (65535)
    eocd_zip, eocd_size = archive_files[-1]
    # byte ranges are zero-based
    last_200 = eocd_size - 100*1024
    # build the url
    eocd_path = posixpath.join(url_parts.path, eocd_zip)
    new_parts = url_parts._replace(path=eocd_path)
    eocd_url  = urlparse.urlunsplit(new_parts)
    # build the request
    req = urllib2.Request(eocd_url)
    req.add_header("Range","bytes=%s-" % (last_200))
    # grab that EOCD!
    f = urllib2.urlopen(req)
    eocd_raw = f.read()
    f.close()
    # step 6: search for the last EOCD signature
    EOCD = re.findall(r'PK\x05\x06.{16}', eocd_raw)[-1]
    # unpack it
    magic, d_count, d_cd, ignore, records_total, cd_size, cd_offset = struct.unpack('<4sHHHHLL', EOCD)
    # step 7: grab the real central directory
    # (it's probably on the same zip as the eocd, but whee, let's follow the spec)
    cd_zip = archive_files[d_cd][0]
    # build the url
    cd_path   = posixpath.join(url_parts.path, cd_zip)
    new_parts = url_parts._replace(path=cd_path)
    cd_url    = urlparse.urlunsplit(new_parts)
    # build the request
    req = urllib2.Request(cd_url)
    req.add_header("Range","bytes=%s-%s" % (cd_offset, cd_offset + cd_size - 1))
    # grab that CD!
    f = urllib2.urlopen(req)
    cd_raw = f.read()
    f.close()
    # step 7: parse the central directory!
    # ... probably not safe to parse like this, but it's fun!
    raw_entries = re.split(r'(PK\x01\x02)', cd_raw)[1:]
    raw_entries = map(lambda x: ''.join(x), zip(raw_entries[::2],raw_entries[1::2]))
    entries = []
    # parse out the entries and where they are in the archive
    for x in raw_entries:
        magic, ignore_16, c_size, u_size, fn_len, e_len, fc_len, f_disk, ignore_6, f_offset = struct.unpack('<4s16sLLHHHH6sL', x[:46])
        f_name = x[46:46+fn_len]
        # only remember compressed files!
        if c_size:
            d = dict()
            d['path']   = f_name
            d['name']   = posixpath.split(f_name)[-1]
            d['zip']    = f_disk
            d['size']   = c_size
            d['offset'] = f_offset
            entries.append(d)
    result = dict()
    result['source'] = url_parts
    result['roms'] = entries
    result['zips'] = archive_files
    return result

def find_rom(rom_info, rom_name):
    return [x for x in rom_info['roms'] if rom_name in x['name']]

def get_byte_range(rom_info, first_zip, start, num_bytes):
    bytes_raw = ''
    url_parts   = rom_info['source']
    range_start = start
    range_end   = start + num_bytes - 1
    # check to see if range_end is beyond the length of the first_zip
    zip_name, zip_size = rom_info['zips'][first_zip]
    f_path    = posixpath.join(url_parts.path, zip_name)
    new_parts = url_parts._replace(path=f_path)
    f_url     = urlparse.urlunsplit(new_parts)
    # build the request
    req = urllib2.Request(f_url)
    # now the tricky part
    if range_start >= zip_size:
        # Whoops! We're trying to start beyond the end of the file
        adjusted_start = range_start - zip_size
        adjusted_end   = range_end   - zip_size
        zip_name, zip_size = rom_info['zips'][first_zip+1]
        f_path    = posixpath.join(url_parts.path, zip_name)
        new_parts = url_parts._replace(path=f_path)
        f_url     = urlparse.urlunsplit(new_parts)
        # build the request
        req = urllib2.Request(f_url)
        req.add_header("Range","bytes=%s-%s" % (adjusted_start, adjusted_end))
        # grab it
        f = urllib2.urlopen(req)
        bytes_raw = f.read()
        f.close()
    elif range_end >= zip_size:
        # We need to download from two zips
        # So let's get the first one
        req.add_header("Range","bytes=%s-" % (range_start))
        # grab part 1
        f = urllib2.urlopen(req)
        part_1 = f.read()
        f.close()
        # How ever many bytes we got, get the rest from the next zip file
        remaining_bytes = num_bytes - len(part_1)
        zip_name, zip_size = rom_info['zips'][first_zip+1]
        f_path    = posixpath.join(url_parts.path, zip_name)
        new_parts = url_parts._replace(path=f_path)
        f_url     = urlparse.urlunsplit(new_parts)
        # build the request
        req = urllib2.Request(f_url)
        req.add_header("Range","bytes=0-%s" % (remaining_bytes-1))
        # grab part 2
        f = urllib2.urlopen(req)
        part_2 = f.read()
        f.close()
        bytes_raw = part_1 + part_2
    else:
        # Yay, it's the simple case and we can download from one zip
        req.add_header("Range","bytes=%s-%s" % (range_start, range_end))
        # grab those bytes!
        f = urllib2.urlopen(req)
        bytes_raw = f.read()
        f.close()
    return bytes_raw

def download_rom(rom_info, rom_record, save_path):
    # first we need to get the local header for the file to see how much total bytes to skip
    local_header = get_byte_range(rom_info, rom_record['zip'], rom_record['offset'], 30)
    # parse the local header
    magic, ignore_22, fn_len, e_len = struct.unpack('<4s22sHH', local_header)
    real_offset = rom_record['offset'] + 30 + fn_len + e_len
    # now we can get the actual rom file!
    raw_rom = get_byte_range(rom_info, rom_record['zip'], real_offset, rom_record['size'])
    f = open(save_path, 'wb')
    f.write(raw_rom)
    f.close()

class romArchive(cmd.Cmd):
    def __init__(self, archiveorg_rom_url):
        cmd.Cmd.__init__(self)
        self.rom_url  = archiveorg_rom_url
        print "[INITIALIZING: %s]" % self.rom_url
        self.rom_info = discover_roms(self.rom_url)
    def do_pwd(self, line):
        "Print current directory"
        print os.getcwd()
    def do_cd(self, line):
        "Change current directory"
        if os.path.isdir(line):
            os.chdir(line)
        else:
            print "Error: No such dir: %s" % line
    def do_ls(self, line):
        "Print contents of current directory"
        dirpath, dirnames, filenames = os.walk(os.getcwd()).next()
        for x in sorted(dirnames):
            print x + '/'
        for x in sorted(filenames):
            print x
    def do_quit(self, line):
        "Exit"
        return True
    def do_find(self, line):
        "find <part of file name>"
        if line:
            results = find_rom(self.rom_info, line)
            if not results:
                print "No results."
            else:
                for x in sorted(results, key=lambda y: y['path']):
                    print 'path:', x['path']
                    print 'name:', x['name']
                    print 'size:', x['size']
                    print ''
    def do_get(self, line):
        "get <file name>"
        if line:
            results = sorted(find_rom(self.rom_info, line), key=lambda y: y['path'])
            target = results[0]
            print "[DOWNLOADING: %s]" % target['path']
            download_rom(self.rom_info, target, target['name'])
            print "[SAVED: %s]" % target['name']
    do_q    = do_quit
    do_EOF  = do_quit
    do_exit = do_quit

# Keep to HTTP URLs to avoid issues with SPI/TLS/HTTPS requirements on python 2
# (though archive.org seems to be friendly/compatible, if you do want to do HTTPS)

def main():
    rom_url = "http://archive.org/download/MAME0.78-MAME2003-ROMs-CHDs-Samples"
    # rom_url = "https://archive.org/download/MAME0.37b5-MAME2000-ROMSet"
    # and https://archive.org/download/MAME0.106-Reference-Set-ROMs-CHDs-Samples, etc.
    # (make sure you're using the '/download/' form of the URL)
    ra = romArchive(rom_url)
    ra.cmdloop()

if __name__ == '__main__':
    main()
