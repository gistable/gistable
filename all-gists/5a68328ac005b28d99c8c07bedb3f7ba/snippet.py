import os, os.path, json, hashlib, subprocess, argparse, sys, stat

BUFFER_SIZE = 65536

def checksum_directory(source_path, progress=False):
    filesystem_details = dict()
    # rough guess of how many files are in a directory
    # horrible hack with a little fudge
    if not os.path.isdir(source_path):
        raise Exception('no such directory')

    all_file_count = len(subprocess.check_output(['/usr/bin/find', source_path]).splitlines()) + 10
    count_so_far = 0
    last_update = 0
    for root_path, directories, files in os.walk(source_path, followlinks=False):
        for d in directories:
            count_so_far += 1
            true_full_path = os.path.join(root_path, d)
            # print "d:", true_full_path
            chroot_path = os.path.join('/', os.path.relpath(true_full_path, source_path))
            if os.path.islink(true_full_path):
                # record symlink
                symlink_destination = os.readlink(true_full_path)
                filesystem_details[chroot_path] = ['s', symlink_destination]
            else:
                # record directory
                filesystem_details[chroot_path] = ['d', '']
        for f in files:
            count_so_far += 1
            true_full_path = os.path.join(root_path, f)
            # print "f:", true_full_path
            chroot_path = os.path.join('/', os.path.relpath(true_full_path, source_path))
            if os.path.islink(true_full_path):
                # record symlink
                symlink_destination = os.readlink(true_full_path)
                filesystem_details[chroot_path] = ['s', symlink_destination]
            elif (not stat.S_ISREG(os.stat(true_full_path).st_mode)):
                # this isn't a normal file or a symlink!!
                # we can record the st_mode
                filesystem_details[chroot_path] = ['*', str(os.stat(true_full_path).st_mode)]
            else:
                # record file with its hash
                h = hashlib.sha1()
                with open(true_full_path, 'rb') as g:
                    b = g.read(BUFFER_SIZE)
                    while len(b) > 0:
                        h.update(b)
                        b = g.read(BUFFER_SIZE)
                filesystem_details[chroot_path] = ['f', h.hexdigest()]
        if progress:
            if count_so_far > (last_update + 1000):
                # need to emit progress
                last_update = count_so_far
                print "* PROGRESS:", "{0:.2%}".format((1.*last_update)/all_file_count)
    formatted_output = '"]\n"/'.join(json.dumps(filesystem_details).split('"], "/')).strip().rstrip("}").lstrip("{")
    formatted_output = "{\n" + ",\n".join(["    "+x for x in sorted(formatted_output.splitlines())]) + "\n}"
    return formatted_output

def main():
    parser = argparse.ArgumentParser(description='Generate a json output analysis of a directory and its file contents')
    parser.add_argument("-p", "--progress", help="progress output", action='store_true', default=False)
    parser.add_argument('source', help='/path/to/input/directory')
    parser.add_argument('output', nargs="?", default=None, help="/path/to/output.json [default=stdout]")
    args = parser.parse_args()
    if not args.source:
        parser.print_help()
        sys.exit(1)
    try:
        result = checksum_directory(args.source, args.progress)
    except:
        print "ERROR: verify you have permissions (sudo?) to read the destination fully and that it exists"
        sys.exit(1)
    if args.output is None:
        print result
    else:
        with open(args.output, 'wb') as f:
            f.write(result)

if __name__ == "__main__":
    main()
